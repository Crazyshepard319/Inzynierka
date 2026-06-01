"""
Rejestracja multimodalna: RGB <-> termal
Eksportuje: run_registration(rgb_path, ter_path, out_path)
"""

import cv2
import math
import numpy as np
import SimpleITK as sitk
from pathlib import Path


MAX_DET_PX = 800


# ── Funkcje pomocnicze (module-level, importowalne) ───────────────────────────

def _morph(maska, r):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r*2+1, r*2+1))
    m = cv2.morphologyEx(maska, cv2.MORPH_CLOSE, k, iterations=4)
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, k, iterations=2)


def _wybierz_kontur(kontury):
    def ocen(k):
        a = cv2.contourArea(k)
        if a < 50:
            return 0.0
        p = cv2.arcLength(k, True)
        return a * (4*np.pi*a/p**2 + 0.05) if p else 0.0
    return max(kontury, key=ocen)


def wykryj_znacznik(sciezka, tryb):
    """
    Zwraca: (centrum [cx,cy] px, promien px, kontur w oryginalnej skali)
    tryb='termal': Otsu INV na szarosci
    tryb='rgb'   : niska saturacja HSV (znacznik metaliczny)
    """
    sciezka = Path(sciezka)
    img_orig = cv2.imread(str(sciezka))
    if img_orig is None:
        raise FileNotFoundError(f"Nie mozna otworzyc: {sciezka}")
    h_orig, w_orig = img_orig.shape[:2]

    sc = min(1.0, MAX_DET_PX / max(w_orig, h_orig))
    img = cv2.resize(img_orig, (int(w_orig*sc), int(h_orig*sc)),
                     interpolation=cv2.INTER_AREA) if sc < 1.0 else img_orig
    h, w = img.shape[:2]
    r_morph = max(2, min(w, h) // 60)

    if tryb == 'termal':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, maska = cv2.threshold(gray, 0, 255,
                                 cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        maska = cv2.inRange(hsv, np.array([0, 0, 60]), np.array([180, 65, 255]))

    maska = _morph(maska, r_morph)
    cv2.imwrite(str(sciezka.parent / f"_maska_{tryb}.png"), maska)

    kontury, _ = cv2.findContours(maska, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    if not kontury:
        raise RuntimeError(
            f"[{tryb}] Brak konturow! Sprawdz: {sciezka.parent / f'_maska_{tryb}.png'}")

    k = _wybierz_kontur(kontury)
    area = cv2.contourArea(k)
    M = cv2.moments(k)
    if M['m00'] == 0:
        raise RuntimeError(f"[{tryb}] Zerowy moment konturu")

    cx = (M['m10'] / M['m00']) / sc
    cy = (M['m01'] / M['m00']) / sc
    promien = np.sqrt(area / np.pi) / sc
    kolo = 4*np.pi*area / cv2.arcLength(k, True)**2
    k_orig = (k.astype(np.float32) / sc).astype(np.int32)

    if kolo < 0.35:
        print(f"  OSTRZEZENIE [{tryb}] kolowos={kolo:.2f} - detekcja moze byc niedokladna")
    print(f"  [{tryb}] centrum=({cx:.1f},{cy:.1f})  "
          f"promien={promien:.1f}px  kolowos={kolo:.3f}  obraz={w_orig}x{h_orig}")

    d = img_orig.copy()
    lw = max(2, int(promien*0.02))
    cv2.drawContours(d, [k_orig], -1, (0, 255, 0), lw)
    cv2.circle(d, (int(cx), int(cy)), int(promien), (255, 100, 0), lw)
    cv2.circle(d, (int(cx), int(cy)), lw*3, (0, 0, 255), -1)
    sc_s = min(1.0, 1200 / max(w_orig, h_orig))
    cv2.imwrite(str(sciezka.parent / f"_debug_{tryb}.png"),
                cv2.resize(d, (int(w_orig*sc_s), int(h_orig*sc_s))))

    return np.array([cx, cy], dtype=float), promien, k_orig


def estymuj_obrot_ksztalt(k_rgb, c_rgb, r_rgb, k_ter, c_ter, r_ter,
                           sz=300, krok_deg=1, debug_dir=None):
    """
    Szuka kata [stopnie, konwencja OpenCV CCW] przy ktorym obrocimy znacznik
    termalny tak, by jak najlepiej pokrywal sie z ksztaltem z RGB.
    """
    def rasteryzuj(k, cx, cy, r):
        pts = k.reshape(-1, 2).astype(np.float64)
        pts = (pts - [cx, cy]) / r * (sz * 0.42) + [sz//2, sz//2]
        pts = np.clip(pts.astype(np.int32), 0, sz-1)
        img = np.zeros((sz, sz), dtype=np.uint8)
        cv2.fillPoly(img, [pts], 255)
        return img

    mapa_rgb = rasteryzuj(k_rgb, c_rgb[0], c_rgb[1], r_rgb)
    mapa_ter = rasteryzuj(k_ter, c_ter[0], c_ter[1], r_ter)

    kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    mapa_rgb_d = cv2.dilate(mapa_rgb, kern)

    cx2 = cy2 = sz // 2
    najlepszy_kat = 0
    najlepszy_ov  = -1

    for kat in range(0, 360, krok_deg):
        R = cv2.getRotationMatrix2D((cx2, cy2), float(kat), 1.0)
        obr = cv2.warpAffine(mapa_ter, R, (sz, sz))
        ov = cv2.countNonZero(cv2.bitwise_and(mapa_rgb_d, obr))
        if ov > najlepszy_ov:
            najlepszy_ov  = ov
            najlepszy_kat = kat

    if debug_dir is not None:
        R_best = cv2.getRotationMatrix2D((cx2, cy2), float(najlepszy_kat), 1.0)
        obr_best = cv2.warpAffine(mapa_ter, R_best, (sz, sz))
        porownanie = np.zeros((sz, sz, 3), dtype=np.uint8)
        porownanie[:, :, 1] = mapa_rgb
        porownanie[:, :, 2] = obr_best
        cv2.imwrite(str(Path(debug_dir) / "_debug_ksztalt.png"), porownanie)

    return najlepszy_kat


def wczytaj_skalar(sciezka):
    """Wczytuje dowolny obraz jako skalarny Float32 (RGB -> luminancja)."""
    img = sitk.ReadImage(str(sciezka))
    if img.GetNumberOfComponentsPerPixel() > 1:
        img_f = sitk.Cast(img, sitk.sitkVectorFloat32)
        r = sitk.VectorIndexSelectionCast(img_f, 0)
        g = sitk.VectorIndexSelectionCast(img_f, 1)
        b = sitk.VectorIndexSelectionCast(img_f, 2)
        img = r*0.2126 + g*0.7152 + b*0.0722
    return sitk.Cast(img, sitk.sitkFloat32)


# ── Glowna funkcja rejestracji ────────────────────────────────────────────────

def run_registration(rgb_path, ter_path, out_path):
    """
    Rejestruje obraz termalny do RGB i zapisuje nalozone nalozone obrazy.
    Zwraca sciezke do pliku wyjsciowego (str).
    """
    rgb_path = Path(rgb_path)
    ter_path = Path(ter_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Detekcja ──────────────────────────────────────────────────────────────
    print("== Detekcja znacznikow ========================================")
    c_rgb, r_rgb, k_rgb = wykryj_znacznik(rgb_path, 'rgb')
    c_ter, r_ter, k_ter = wykryj_znacznik(ter_path, 'termal')
    skala = r_rgb / r_ter
    print(f"\n  Skala r_rgb/r_ter = {skala:.4f}")

    # ── Szacowanie obrotu ─────────────────────────────────────────────────────
    print("\n== Szacowanie katu z ksztaltow konturow =======================")
    kat_cv_deg = estymuj_obrot_ksztalt(
        k_rgb, c_rgb, r_rgb, k_ter, c_ter, r_ter,
        debug_dir=out_path.parent)
    print(f"  Najlepszy kat (OpenCV CCW): {kat_cv_deg} stopni")

    # ── Przygotowanie obrazow SimpleITK ───────────────────────────────────────
    fixed  = wczytaj_skalar(rgb_path)
    moving = wczytaj_skalar(ter_path)

    sp_f = np.array(fixed.GetSpacing())
    moving.SetSpacing((sp_f * skala).tolist())
    moving.SetOrigin(fixed.GetOrigin())
    moving.SetDirection(fixed.GetDirection())

    fixed  = sitk.Normalize(fixed)
    moving = sitk.Normalize(moving)

    p_f = fixed.TransformIndexToPhysicalPoint(
        (int(round(c_rgb[0])), int(round(c_rgb[1]))))
    p_m = moving.TransformIndexToPhysicalPoint(
        (int(round(c_ter[0])), int(round(c_ter[1]))))
    t_base = (p_m[0] - p_f[0], p_m[1] - p_f[1])

    # ── Funkcje lokalne (domkniecia nad fixed/moving/p_f/t_base) ─────────────
    def zbuduj_tf(kat_rad):
        tf = sitk.Similarity2DTransform()
        tf.SetScale(1.0)
        tf.SetAngle(kat_rad)
        tf.SetCenter(p_f)
        tf.SetTranslation(t_base)
        return tf

    def szybka_reg(tf_start):
        r = sitk.ImageRegistrationMethod()
        r.SetMetricAsMattesMutualInformation(32)
        r.SetMetricSamplingStrategy(r.RANDOM)
        r.SetMetricSamplingPercentage(0.15)
        r.SetInterpolator(sitk.sitkLinear)
        r.SetOptimizerAsGradientDescent(
            learningRate=0.05, numberOfIterations=80,
            convergenceMinimumValue=1e-6, convergenceWindowSize=10)
        r.SetOptimizerScalesFromPhysicalShift()
        r.SetShrinkFactorsPerLevel([8])
        r.SetSmoothingSigmasPerLevel([4.0])
        r.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
        r.SetInitialTransform(tf_start, inPlace=True)
        r.Execute(fixed, moving)
        return tf_start, r.GetMetricValue()

    # ── Wybor najlepszego kata startowego ─────────────────────────────────────
    katy_rad = [
        math.radians(kat_cv_deg),
        math.radians(-kat_cv_deg),
        math.radians(kat_cv_deg + 180),
        math.radians(-kat_cv_deg + 180),
    ]

    print("\n== Wybor najlepszego kandydata katowego =======================")
    najlepszy_metric   = float('inf')
    najlepszy_tf_start = None
    najlepszy_kat_info = 0.0

    for kat_rad in katy_rad:
        tf_prob = zbuduj_tf(kat_rad)
        tf_out, metric = szybka_reg(tf_prob)
        print(f"  kat={math.degrees(kat_rad):+7.1f} st  metric={metric:.6f}")
        if metric < najlepszy_metric:
            najlepszy_metric   = metric
            najlepszy_tf_start = tf_out
            najlepszy_kat_info = math.degrees(kat_rad)

    print(f"\n  => Wybrany kat: {najlepszy_kat_info:.1f} stopni  "
          f"metric={najlepszy_metric:.6f}")

    # ── Faza 1: Similarity2D ──────────────────────────────────────────────────
    reg = sitk.ImageRegistrationMethod()
    reg.SetMetricAsMattesMutualInformation(64)
    reg.SetMetricSamplingStrategy(reg.RANDOM)
    reg.SetMetricSamplingPercentage(0.25)
    reg.SetInterpolator(sitk.sitkLinear)
    reg.SetOptimizerAsGradientDescent(
        learningRate=0.1, numberOfIterations=500,
        convergenceMinimumValue=1e-7, convergenceWindowSize=25)
    reg.SetOptimizerScalesFromPhysicalShift()
    reg.SetShrinkFactorsPerLevel([4, 2, 1])
    reg.SetSmoothingSigmasPerLevel([2.0, 1.0, 0.0])
    reg.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
    reg.SetInitialTransform(najlepszy_tf_start, inPlace=True)

    def _on_iter():
        i = reg.GetOptimizerIteration()
        if i % 50 == 0:
            pos = reg.GetOptimizerPosition()
            ad = float(np.degrees(pos[0])) if len(pos) > 0 else 0.0
            print(f"  iter {i:4d}  metric={reg.GetMetricValue():.6f}  kat={ad:.2f} st")

    reg.AddCommand(sitk.sitkIterationEvent, _on_iter)

    print("\n== Faza 1: Rejestracja Mattes MI (Similarity2D) ==============")
    tf_final = reg.Execute(fixed, moving)
    print(f"\nStop: {reg.GetOptimizerStopConditionDescription()}")
    print(f"Metric faza 1: {reg.GetMetricValue():.6f}")

    # ── Faza 2: doprecyzowanie Affine (6 DOF) ─────────────────────────────────
    tf_affine_start = sitk.AffineTransform(2)
    tf_affine_start.SetMatrix(tf_final.GetMatrix())
    tf_affine_start.SetCenter(tf_final.GetCenter())
    tf_affine_start.SetTranslation(tf_final.GetTranslation())

    reg2 = sitk.ImageRegistrationMethod()
    reg2.SetMetricAsMattesMutualInformation(64)
    reg2.SetMetricSamplingStrategy(reg2.RANDOM)
    reg2.SetMetricSamplingPercentage(0.40)
    reg2.SetInterpolator(sitk.sitkLinear)
    reg2.SetOptimizerAsGradientDescent(
        learningRate=0.02, numberOfIterations=300,
        convergenceMinimumValue=1e-8, convergenceWindowSize=30)
    reg2.SetOptimizerScalesFromPhysicalShift()
    reg2.SetShrinkFactorsPerLevel([2, 1])
    reg2.SetSmoothingSigmasPerLevel([0.5, 0.0])
    reg2.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
    reg2.SetInitialTransform(tf_affine_start, inPlace=False)

    def _on_iter2():
        i = reg2.GetOptimizerIteration()
        if i % 50 == 0:
            print(f"  [faza2] iter {i:4d}  metric={reg2.GetMetricValue():.6f}")

    reg2.AddCommand(sitk.sitkIterationEvent, _on_iter2)

    print("\n== Faza 2: Doprecyzowanie Affine (skala/scinanie) =============")
    tf_final2 = reg2.Execute(fixed, moving)
    print(f"\nStop: {reg2.GetOptimizerStopConditionDescription()}")
    print(f"Metric faza 2: {reg2.GetMetricValue():.6f}")

    # ── Resample i zapis ──────────────────────────────────────────────────────
    moving_reg = sitk.Resample(
        moving, fixed, tf_final2, sitk.sitkLinear, 0.0, moving.GetPixelID())

    f_u8 = sitk.Cast(sitk.RescaleIntensity(fixed, 0, 255), sitk.sitkUInt8)
    m_u8 = sitk.Cast(sitk.RescaleIntensity(moving_reg, 0, 255), sitk.sitkUInt8)
    overlay = sitk.Compose(f_u8, m_u8, sitk.Cast(f_u8 * 0.5, sitk.sitkUInt8))
    sitk.WriteImage(overlay, str(out_path))

    print(f"\nWynik: {out_path}")
    return str(out_path)


# ── Uruchomienie bezposrednie ─────────────────────────────────────────────────

if __name__ == '__main__':
    BASE = Path(r"C:/Users/groch/OneDrive/Pulpit/Inzynierka/nowe1")
    run_registration(
        BASE / "rgb_1.jpg",
        BASE / "thermal_1.png",
        BASE / "dopasowanie_claude.png",
    )
