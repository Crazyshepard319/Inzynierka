"""
Rejestracja RGB <-> termal metoda z dopasowanie2.py (SimpleITK: informacja wzajemna Mattesa na
jasnosci obrazow, najpierw podobienstwo, potem przeksztalcenie afiniczne), dostosowana do znacznika Π.

Zmiany wzgledem archiwum/dopasowanie2.py:
  - start: znacznik wykrywany tak jak w dopasowanie3.py (wzorzec Π 35 x 26 mm, pasek 9 mm) zamiast progu
    nasycenia i wyboru najbardziej okraglego konturu; kat, skala i przesuniecie z dopasowania
    ksztaltow (Π nie ma symetrii obrotowej, wiec nie trzeba sprawdzac czterech katow),
  - opcjonalnie metryka liczona tylko w otoczeniu znacznika (maska obrazu stalego),
  - zdjecie zmniejszone do 1000 px (jak w dopasowanie3.py), wynik jako macierz 3x3 T
    (piksel zdjecia -> piksel termowizji), zgodna z <wynik>_macierz.txt z dopasowanie3.py.

    T, info = rejestruj_mi(rgb_path, ter_path, otoczenie=True)

Wynik na 94 parach z 23.10 (porownaj_rejestracje.py, blad 8 naroznikow z CVAT po rejestracji):
    dopasowanie3.py (ECC na maskach)       mediana 0,62 mm, <= 2 mm na 91/94 parach
    ta metoda, MI w otoczeniu znacznika    mediana 3,47 mm, <= 2 mm na 32/94
    ta metoda, MI na calym obrazie         mediana 4,78 mm, <= 2 mm na 16/94
Informacja wzajemna jasnosci nie poprawia startu z ksztaltu (mediana 3,27 mm): folia na zdjeciu jest
jasna i lustrzana, na termowizji ciemna z odbiciami, a skora z wlosami na zdjeciu jest gladka na
termowizji - zaleznosc jasnosci miedzy modalnosciami nie jest stala. Dlatego system uzywa dopasowanie3.py.
"""
import math

import cv2
import numpy as np
import SimpleITK as sitk

import dopasowanie3 as d3


def _sitk(obraz):
    img = sitk.GetImageFromArray(np.ascontiguousarray(obraz, np.float32))
    img.SetSpacing((1.0, 1.0))
    img.SetOrigin((0.0, 0.0))
    return sitk.Normalize(img)


def _do_macierzy(tf):
    """Przeksztalcenie SimpleITK (punkty obrazu stalego -> ruchomego) jako macierz 3x3."""
    A = np.array(tf.GetMatrix(), np.float64).reshape(2, 2)
    c = np.array(tf.GetCenter(), np.float64)
    t = np.array(tf.GetTranslation(), np.float64)
    M = np.eye(3)
    M[:2, :2] = A
    M[:2, 2] = A @ (-c) + c + t
    return M


def rejestruj_mi(rgb_path, ter_path, otoczenie=True, log=print):
    """Zwraca (T 3x3: piksel zdjecia -> piksel termowizji, info)."""
    ter = d3.wykryj_znacznik_termal(ter_path)
    img = d3.imread(rgb_path)
    w = d3.wykryj_folie_rgb(img)
    sc, m_rgb, im = w["sc"], w["maska"], w["im"]

    # start z ksztaltow znacznikow (podobienstwo: srodek, skala z pol, kat), RGB(rob.) -> termal
    W0, kat, iou, _ = d3.wstepne_dopasowanie(m_rgb, ter["maska"])
    A0 = W0[:2, :2]
    skala = math.sqrt(abs(np.linalg.det(A0)))
    kat_rad = math.atan2(A0[1, 0], A0[0, 0])
    c, _ = d3.srodek_pole(m_rgb)
    t0 = A0 @ c + W0[:2, 2] - c
    log(f"  start z ksztaltu: kat={math.degrees(kat_rad):.1f} st  skala={skala:.4f}  IoU ksztaltu={iou:.3f}")

    fixed = _sitk(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY))
    g_ter, _ = d3.wczytaj_termal(ter_path)
    moving = _sitk(g_ter)

    maska = None
    if otoczenie:                      # metryka tylko w otoczeniu znacznika (otoczka + 25% rozmiaru)
        r = int(0.25 * math.sqrt(cv2.countNonZero(m_rgb)))
        ot = np.zeros_like(m_rgb)
        cv2.fillConvexPoly(ot, cv2.convexHull(cv2.findNonZero(m_rgb)), 255)
        ot = cv2.dilate(ot, d3._kolo(r))
        maska = sitk.GetImageFromArray((ot > 0).astype(np.uint8))
        maska.CopyInformation(fixed)

    def metoda(probki, poziomy, wygladzenia, lr, iteracje, okno, minimum):
        r = sitk.ImageRegistrationMethod()
        r.SetMetricAsMattesMutualInformation(64)
        r.SetMetricSamplingStrategy(r.RANDOM)
        r.SetMetricSamplingPercentage(probki, seed=1)
        if maska is not None:
            r.SetMetricFixedMask(maska)
        r.SetInterpolator(sitk.sitkLinear)
        r.SetOptimizerAsGradientDescent(learningRate=lr, numberOfIterations=iteracje,
                                        convergenceMinimumValue=minimum, convergenceWindowSize=okno)
        r.SetOptimizerScalesFromPhysicalShift()
        r.SetShrinkFactorsPerLevel(poziomy)
        r.SetSmoothingSigmasPerLevel(wygladzenia)
        r.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
        return r

    # faza 1: podobienstwo (jak w dopasowanie2.py)
    tf = sitk.Similarity2DTransform()
    tf.SetCenter(tuple(c))
    tf.SetScale(skala)
    tf.SetAngle(kat_rad)
    tf.SetTranslation(tuple(t0))
    r1 = metoda(0.25, [4, 2, 1], [2.0, 1.0, 0.0], 0.1, 500, 25, 1e-7)
    r1.SetInitialTransform(tf, inPlace=True)
    r1.Execute(fixed, moving)
    log(f"  faza 1 (podobienstwo): MI={r1.GetMetricValue():.4f}  {r1.GetOptimizerStopConditionDescription()[:60]}")

    # faza 2: afiniczne (jak w dopasowanie2.py)
    af = sitk.AffineTransform(2)
    af.SetMatrix(tf.GetMatrix())
    af.SetCenter(tf.GetCenter())
    af.SetTranslation(tf.GetTranslation())
    r2 = metoda(0.40, [2, 1], [0.5, 0.0], 0.02, 300, 30, 1e-8)
    r2.SetInitialTransform(af, inPlace=True)
    r2.Execute(fixed, moving)
    log(f"  faza 2 (afiniczne): MI={r2.GetMetricValue():.4f}")

    T = _do_macierzy(af) @ np.diag([sc, sc, 1.0])        # piksel zdjecia (oryginal) -> piksel termalny
    return T, dict(mi=r2.GetMetricValue(), zgodnosc_rgb=w["zgodnosc"], zgodnosc_termal=ter["zgodnosc"],
                   start=_do_macierzy(tf) @ np.diag([sc, sc, 1.0]))
