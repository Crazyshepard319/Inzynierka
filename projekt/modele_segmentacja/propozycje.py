"""
Propozycje polozenia znamienia we wnetrzu znacznika Π - zanim zobaczy je model segmentacji.

Dlaczego: PanDerm uczono na zdjeciach ISIC, gdzie znamie zajmuje ok. polowy kadru. Wnetrze znacznika
ma 17 x 17 mm, a znamie zwykle 1-4 mm, wiec w pierwszym przebiegu (kadr = cale wnetrze) model czesto
oznacza duzy fragment skory (cien przy folii, wlosy, cala skore), a automatyczne przyblizenie
przybliza sie do tego blednego obszaru. Dlatego najpierw szukamy kandydatow na znamie klasycznie,
a model dostaje kadr ustawiony wokol kandydata tak jak w ISIC (znamie ~0,53 boku kadru).

Kandydaci = ciemne plamy wzgledem lokalnego tla skory:
  1. skala robocza ~20 px/mm (rozmiar w mm z pola otworu znacznika 17 x 17 mm),
  2. jasnosc L (Lab) po domknieciu morfologicznym elementem ~0,2 mm - znikaja wlosy,
  3. poza obszarem (folia) wartosc najblizszego piksela skory - cien przy folii nie odstaje od tla,
  4. tlo = mediana w oknie 8 mm (wiekszym niz znamie), D = tlo - L (o ile ciemniej niz otoczenie),
  5. lokalne maksima D (po wygladzeniu 0,25 mm) powyzej progu (mediana + 3 odchylenia odporne, min. 6),
  6. region kandydata = spojny obszar D > 0,5 maksimum (gdy zlewa sie z cieniem: 0,65, potem 0,8),
     odrzucane: pole < 0,15 mm2 lub > 40 mm2, styk z brzegiem obszaru > 3 mm (cien wzdluz folii),
     niezwarte (pole < 0,6 otoczki wypuklej) i wydluzone (boki prostokata > 3 : 1 - wlos, zmarszczka),
  7. ocena = suma D w regionie [L * mm2] ("objetosc" kontrastu), kolejnosc malejaco.

    from modele_segmentacja.propozycje import propozycje
    kandydaci = propozycje(obraz_bgr, znacznik, ile=3)     # [(maska uint8 0/255 rozmiaru zdjecia, ocena)]
"""
from dataclasses import dataclass

import cv2
import numpy as np

from .znacznik import _d

POLE_OTWORU_MM2 = 17.0 * 17.0      # otwor znacznika 17 x 17 mm (belka 35, ramiona 26, pasek 9 mm)
PX_MM_ROBOCZE = 20.0
OKNO_TLA_MM = 8.0
K_MAD, PROG_MIN = 3.0, 6.0
POZIOMY = (0.5, 0.65, 0.8)
POLE_MM2 = (0.15, 40.0)
STYK_MAX_MM = 3.0


@dataclass
class Mapa:
    D: np.ndarray            # o ile ciemniej niz lokalne tlo skory (jednostki L), kadr z.roi w skali roboczej
    obszar: np.ndarray       # obszar szukania w tej samej skali (bool)
    px_mm: float             # pikseli na mm w skali roboczej
    roi: tuple               # (x, y, w, h) kadru na zdjeciu


def mapa_ciemnosci(obraz, z):
    """Mapa D (o ile ciemniej niz lokalne tlo skory) we wnetrzu znacznika z, w skali roboczej."""
    px_mm = np.sqrt(max(cv2.countNonZero(z.wnetrze), 1) / POLE_OTWORU_MM2)
    x, y, w, h = z.roi
    s = min(1.0, PX_MM_ROBOCZE / px_mm)
    wyc = obraz[y:y + h, x:x + w]
    if s < 1:
        wyc = cv2.resize(wyc, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    ob = cv2.resize(z.obszar[y:y + h, x:x + w], (wyc.shape[1], wyc.shape[0]),
                    interpolation=cv2.INTER_NEAREST) > 0
    pm = px_mm * s
    L = cv2.cvtColor(wyc, cv2.COLOR_BGR2LAB)[..., 0].astype(np.float32)
    L = cv2.morphologyEx(L, cv2.MORPH_CLOSE, _d._kolo(max(1, 0.2 * pm)))          # bez wlosow
    _, etyk = cv2.distanceTransformWithLabels((~ob).astype(np.uint8), cv2.DIST_L2, 5,
                                              labelType=cv2.DIST_LABEL_PIXEL)
    wart = np.zeros(etyk.max() + 1, np.float32)
    wart[etyk[ob]] = L[ob]
    L = wart[etyk]                                  # poza obszarem: najblizszy piksel skory
    s2 = 5.0 / pm                                   # tlo liczone w skali 5 px/mm
    male = cv2.resize(L, None, fx=s2, fy=s2, interpolation=cv2.INTER_AREA)
    tlo = cv2.medianBlur(np.clip(male, 0, 255).astype(np.uint8), int(OKNO_TLA_MM * 5) | 1).astype(np.float32)
    tlo = cv2.resize(tlo, (L.shape[1], L.shape[0]), interpolation=cv2.INTER_LINEAR)
    D = cv2.GaussianBlur(tlo - L, (0, 0), 0.1 * pm)
    D[~ob] = 0
    return Mapa(D, ob, pm, (x, y, w, h))


def _w_skali_mapy(mapa, maska):
    x, y, w, h = mapa.roi
    return cv2.resize(maska[y:y + h, x:x + w], (mapa.D.shape[1], mapa.D.shape[0]),
                      interpolation=cv2.INTER_NEAREST) > 0


def kontrast_brzegu(mapa, maska):
    """Srednie D w masce minus srednie D w pasie 0,4 mm tuz za jej brzegiem (jednostki L).
    Najwieksze, gdy brzeg maski lezy na brzegu ciemnej plamy: maska za mala ma za brzegiem dalej
    ciemne znamie, a maska za duza obejmuje jasna skore."""
    m = _w_skali_mapy(mapa, maska) & mapa.obszar
    if not m.any():
        return float("-inf")
    pas = (cv2.dilate(m.astype(np.uint8), _d._kolo(max(1, 0.4 * mapa.px_mm))) > 0) & ~m & mapa.obszar
    return float(mapa.D[m].mean() - (mapa.D[pas].mean() if pas.any() else 0.0))


def _moze_byc_znamieniem(mj, brzeg, pm):
    pole = mj.sum() / pm ** 2
    if not POLE_MM2[0] <= pole <= POLE_MM2[1]:
        return False
    if (brzeg & mj).sum() / pm > STYK_MAX_MM:        # dlugi styk z brzegiem obszaru: cien folii
        return False
    pk = cv2.findNonZero(mj.astype(np.uint8))
    if mj.sum() < 0.6 * max(cv2.contourArea(cv2.convexHull(pk)), 1):          # niezwarty (L, pas)
        return False
    (_, _), (a1, a2), _ = cv2.minAreaRect(pk)
    return max(a1, a2) <= 3 * max(min(a1, a2), 1)  # wydluzony: wlos, zmarszczka


def propozycje(obraz, z, ile=3, mapa=None):
    """Kandydaci na znamie we wnetrzu znacznika z (znacznik.Znacznik), najlepsi najpierw.
    Zwraca liste (maska uint8 0/255 rozmiaru zdjecia, ocena)."""
    mapa = mapa or mapa_ciemnosci(obraz, z)
    D, ob, pm = mapa.D, mapa.obszar, mapa.px_mm
    Dg = cv2.GaussianBlur(D, (0, 0), 0.25 * pm)
    v = Dg[ob]
    if v.size == 0:
        return []
    med = float(np.median(v))
    prog = max(PROG_MIN, med + K_MAD * 1.4826 * float(np.median(np.abs(v - med))))
    szczyty = (Dg >= cv2.dilate(Dg, _d._kolo(max(1, 0.5 * pm)))) & (Dg > prog) & ob
    ys, xs = np.nonzero(szczyty)
    brzeg = cv2.distanceTransform(ob.astype(np.uint8), cv2.DIST_L2, 5) < 0.3 * pm
    zajete = np.zeros(D.shape, bool)
    kand = []
    for i in np.argsort(-Dg[ys, xs])[:40]:
        py, px = ys[i], xs[i]
        if zajete[py, px]:
            continue
        mj = None
        for poziom in POZIOMY:                        # region zlewa sie z cieniem -> wyzszy prog
            b = ((D > max(prog, poziom * Dg[py, px])) & ob).astype(np.uint8)
            b = cv2.morphologyEx(b, cv2.MORPH_OPEN, _d._kolo(max(1, 0.1 * pm)))
            _, lab = cv2.connectedComponents(b, connectivity=8)
            if lab[py, px] == 0:
                break
            mj = lab == lab[py, px]
            if _moze_byc_znamieniem(mj, brzeg, pm):
                kand.append((float(D[mj].sum() / pm ** 2), mj))
                break
        if mj is not None:
            zajete |= mj
    kand.sort(key=lambda k: -k[0])
    x, y, w, h = mapa.roi
    wynik = []
    for ocena, mj in kand[:ile]:
        pel = np.zeros(obraz.shape[:2], np.uint8)
        pel[y:y + h, x:x + w] = cv2.resize(mj.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST) * 255
        wynik.append((pel, ocena))
    return wynik
