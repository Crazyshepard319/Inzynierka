"""
Parametry ilosciowe regionu (znamienia) w obu modalnosciach.

RGB (maska znamienia + homografia px -> mm z naroznikow znacznika):
    pole [mm2], obwod [mm], srednica rownowazna [mm], max i min srednica Fereta [mm],
    kolistosc 4*pi*pole/obwod^2 (1 = kolo), asymetria (czesc pola, ktora nie pokrywa sie po odbiciu
    wzgledem osi glownej / prostopadlej), sredni kolor Lab znamienia.
Termowizja (maska przeniesiona z RGB + mapa °C):
    temperatura srednia (wazona ulamkiem pokrycia piksela), mediana, min, max, odchylenie, liczba pikseli
    (parametry_termiczne - nieuzywane w raporcie, bo pomiary temperatury z tej kamery nie sa wiarygodne).
"""
import cv2
import numpy as np

from . import geometria as geo


def _asymetria(kont_mm, rozdz=0.02):
    """Asymetria ksztaltu: XOR z odbiciem wzgledem osi glownej i prostopadlej, podzielony przez pole."""
    lo = kont_mm.min(0) - 1.0
    pts = (kont_mm - lo) / rozdz
    wh = np.ceil(pts.max(0) + 1.0 / rozdz).astype(int)
    m = np.zeros((wh[1], wh[0]), np.uint8)
    cv2.fillPoly(m, [np.round(pts * 16).astype(np.int32)], 1, shift=4)
    mo = cv2.moments(m, binaryImage=True)
    if mo["m00"] == 0:
        return float("nan"), float("nan")
    cx, cy = mo["m10"] / mo["m00"], mo["m01"] / mo["m00"]
    kat = 0.5 * np.arctan2(2 * mo["mu11"], mo["mu20"] - mo["mu02"])
    wyn = []
    for a in (kat, kat + np.pi / 2):                 # odbicie wzgledem prostej przez srodek pod katem a
        c, s = np.cos(2 * a), np.sin(2 * a)
        R = np.array([[c, s, cx - c * cx - s * cy], [s, -c, cy - s * cx + c * cy]])
        mr = cv2.warpAffine(m, R, (m.shape[1], m.shape[0]), flags=cv2.INTER_NEAREST)
        wyn.append(float(np.logical_xor(m > 0, mr > 0).sum() / (m > 0).sum()))
    return wyn[0], wyn[1]


def _lab(obraz_bgr):
    return cv2.cvtColor(obraz_bgr.astype(np.float32) / 255.0, cv2.COLOR_BGR2LAB)   # L 0..100, a/b w jednostkach Lab


def parametry_rgb(obraz_bgr, maska_znamienia, H_mm):
    """Parametry znamienia na zdjeciu RGB. H_mm: homografia px -> mm (narozniki.json)."""
    m = np.asarray(maska_znamienia) > 0
    ks = geo.kontury(m.astype(np.uint8))
    kont = max(ks, key=lambda k: cv2.contourArea(k.astype(np.float32)))
    srodek = np.argwhere(m).mean(0)[::-1]
    s = geo.mm_na_px(H_mm, srodek)
    kont_mm = geo.przenies_punkty(kont, H_mm)
    pole = float(m.sum()) * s * s                     # liczba pikseli x lokalna skala^2
    obwod = float(cv2.arcLength(kont_mm.astype(np.float32), True))
    otoczka = cv2.convexHull(kont_mm.astype(np.float32))[:, 0]
    d = np.sqrt(((otoczka[:, None] - otoczka[None]) ** 2).sum(-1))
    feret_min = float(min(cv2.minAreaRect(otoczka)[1]))
    a1, a2 = _asymetria(kont_mm)

    lab_z = _lab(obraz_bgr)[m].mean(0)
    return {
        "mm_na_px": s,
        "pole_mm2": pole,
        "obwod_mm": obwod,
        "srednica_rownowazna_mm": 2 * np.sqrt(pole / np.pi),
        "feret_max_mm": float(d.max()),
        "feret_min_mm": feret_min,
        "kolistosc": 4 * np.pi * pole / obwod ** 2 if obwod else float("nan"),
        "asymetria_os_glowna": a1,
        "asymetria_os_prostopadla": a2,
        "lab_znamie": lab_z.round(2).tolist(),
        "piksele_znamienia": int(m.sum()),
    }


def parametry_termiczne(T, ulamek_znamienia, mm_na_px):
    """Temperatury w masce znamienia przeniesionej z RGB (ulamek pokrycia piksela 0..1)."""
    w = np.asarray(ulamek_znamienia, np.float64)
    rdzen = w >= 0.5
    wynik = {"mm_na_px": mm_na_px, "piksele_znamienia": float(w.sum())}
    if w.sum() > 0:
        wynik["T_znamie_srednia"] = float((w * T).sum() / w.sum())
        if rdzen.any():
            v = T[rdzen]
            wynik.update(T_znamie_mediana=float(np.median(v)), T_znamie_min=float(v.min()),
                         T_znamie_max=float(v.max()), T_znamie_odchylenie=float(v.std()))
    return wynik
