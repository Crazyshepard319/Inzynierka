"""
Potok analizy jednej pary RGB - termowizja.

    python potok_pary.py 1                 # para 1, model rejestracji 'auto'
    python potok_pary.py 1 --model afiniczna

Kroki:
  1. wczytanie dane/pary/N/ (zdjecie, termowizja, mapa °C, maski i narozniki z CVAT)
  2. rejestracja dopasowanie3.run_registration -> macierz T (piksel RGB -> piksel termowizji);
     znacznik wykrywany automatycznie metoda klasyczna, maski z CVAT NIE sa uzywane
  3. przeniesienie przez T: obrys znamienia, obrys i otwor znacznika, 8 naroznikow (RGB -> termowizja)
  4. pomiary: RGB w mm (homografia z naroznikow znacznika 35 x 26 mm) i kolor; termowizja: °C, ΔT
  5. zgodnosc z wzorcem z CVAT (badanie E1): TRE naroznikow, Dice/IoU/HD95/ASSD obrysu i otworu
  6. raport: wyniki/wyniki_obu/para_N/raport.html + metryki.json + obrazy PNG
"""
import argparse
import contextlib
import io
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dopasowanie3 as dop                                   # noqa: E402
from analiza import geometria as geo, miary, pomiary, raport  # noqa: E402
from analiza.dane import INZ, wczytaj_pare                   # noqa: E402

GESTOSC = 4            # porownania obrysow w siatce termowizji 4x gestszej (dokladnosc ~0,07 mm)
EMISYJNOSC = 0.98      # uzyta w temperatury_par.py


def rejestracja(para, model):
    kat = INZ / "wyniki" / "wyniki_dopasowania" / f"para_{para.n}"
    kat.mkdir(parents=True, exist_ok=True)
    wyj = kat / "dopasowanie.png"
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        dop.run_registration(para.katalog / "rgb.jpg", para.katalog / "termal.jpg", wyj, model)
    tekst = log.getvalue()
    (kat / "rejestracja_log.txt").write_text(tekst, encoding="utf-8")
    M = np.loadtxt(kat / "dopasowanie_macierz.txt")
    wynik = {"macierz_T": M.tolist(), "folder": str(kat)}
    if m := re.search(r"=> wybrany model: (\w+)", tekst):
        wynik["model"] = m.group(1)
    if m := re.findall(r"Dice=([\d.]+)\s+sredni blad krawedzi=([\d.]+) px termal \(", tekst):
        wynik["dice_wewnetrzny"], wynik["blad_krawedzi_px"] = float(m[-1][0]), float(m[-1][1])
    return wynik, M, kat


def analizuj(n, model="auto"):
    p = wczytaj_pare(n)                                                    # 1
    rej, M, kat_dop = rejestracja(p, model)                                # 2
    ks_t = p.T.shape

    nar_T = geo.przenies_punkty(p.narozniki_rgb, M)                        # 3
    obrys_z_rgb = geo.wypelnij([nar_T[geo.OBRYS]], ks_t, GESTOSC)
    obrys_t = geo.wypelnij([p.narozniki_termal[geo.OBRYS]], ks_t, GESTOSC)
    otwor_z_rgb = geo.wypelnij([nar_T[geo.OTWOR]], ks_t, GESTOSC)
    otwor_t = geo.wypelnij([p.narozniki_termal[geo.OTWOR]], ks_t, GESTOSC)
    znamie_gesta = geo.przenies_maske(p.maska_znamie_rgb, M, ks_t, GESTOSC)
    ulamek = geo.ulamek_pokrycia(znamie_gesta, GESTOSC)

    s_t = geo.mm_na_px(p.H_termal, p.narozniki_termal.mean(0))             # 4
    p_rgb = pomiary.parametry_rgb(p.rgb, p.maska_znamie_rgb, p.H_rgb, p.maska_znacznik_rgb)
    p_ter = pomiary.parametry_termiczne(p.T, ulamek, s_t, p.maska_znacznik_termal)
    folia = cv2.dilate(p.maska_znacznik_termal, np.ones((5, 5), np.uint8)) > 0
    otwor_1x = geo.wypelnij([p.narozniki_termal[geo.OTWOR]], ks_t) & ~folia

    zg = {"tre": miary.tre(nar_T, p.narozniki_termal, p.H_termal),         # 5
          "obrys": miary.zgodnosc_masek(obrys_z_rgb, obrys_t, s_t / GESTOSC),
          "otwor": miary.zgodnosc_masek(otwor_z_rgb, otwor_t, s_t / GESTOSC)}

    w = {"info": p.info, "rejestracja": rej, "zgodnosc": zg, "pomiary_rgb": p_rgb, "pomiary_termiczne": p_ter,
         "pierscien_mm": pomiary.PIERSCIEN_MM, "emisyjnosc": EMISYJNOSC,
         "T_otwor_srednia": float(p.T[otwor_1x].mean()) if otwor_1x.any() else None,
         "pole_znamienia_termal_do_rgb": float(ulamek.sum() * s_t ** 2 / p_rgb["pole_mm2"])}
    obrazy = rysuj(p, M, nar_T, znamie_gesta, p_rgb["_pierscien"], p_ter["_pierscien"], kat_dop)
    return w, obrazy


# ── obrazy do raportu ────────────────────────────────────────────────────────

def _napis(img, tekst, xy, skala=0.6):
    for kol, g in (((0, 0, 0), 4), ((255, 255, 255), 1)):
        cv2.putText(img, tekst, xy, cv2.FONT_HERSHEY_SIMPLEX, skala, kol, g, cv2.LINE_AA)


def _brzegi(maska):
    """Wszystkie brzegi maski (zewnetrzne i wewnetrzne, np. obie krawedzie pierscienia)."""
    ks, _ = cv2.findContours(np.asarray(maska).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return [k[:, 0, :].astype(np.float64) for k in ks if len(k) >= 3]


def _kadr(img, pkt, margines=0.25):
    x0, y0 = pkt.min(0)
    x1, y1 = pkt.max(0)
    m = margines * max(x1 - x0, y1 - y0)
    x0, y0 = int(max(0, x0 - m)), int(max(0, y0 - m))
    x1, y1 = int(min(img.shape[1], x1 + m)), int(min(img.shape[0], y1 + m))
    return img[y0:y1, x0:x1].copy(), np.array([x0, y0])


def rysuj(p, M, nar_T, znamie_gesta, pierscien_rgb, pierscien_t, kat_dop):
    ob = {}
    # zdjecie: kadr wokol znacznika
    k, o = _kadr(p.rgb, p.narozniki_rgb)
    sk = 700 / k.shape[1]
    k = cv2.resize(k, None, fx=sk, fy=sk, interpolation=cv2.INTER_AREA)
    tr = lambda pts: np.round((np.asarray(pts) - o) * sk).astype(np.int32)
    cv2.polylines(k, [tr(p.narozniki_rgb)], True, (0, 200, 0), 2, cv2.LINE_AA)
    for kont in geo.kontury(p.maska_znamie_rgb):
        cv2.polylines(k, [tr(kont)], True, (0, 0, 255), 2, cv2.LINE_AA)
    for kont in _brzegi(pierscien_rgb):
        cv2.polylines(k, [tr(kont)], True, (0, 230, 255), 1, cv2.LINE_AA)
    for i, q in enumerate(tr(p.narozniki_rgb)):
        cv2.circle(k, tuple(int(v) for v in q), 5, (0, 200, 0), -1, cv2.LINE_AA)
        _napis(k, str(i), (int(q[0]) + 7, int(q[1]) - 7))
    ob["rgb"] = k

    # termowizja 3x: znacznik z CVAT (fiolet), przeniesione z RGB (zielony, czerwony), bledy naroznikow
    z = 3
    t = cv2.resize(p.termal, None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC)
    d = lambda pts: np.round((np.asarray(pts) + 0.5) * z - 0.5).astype(np.int32)
    cv2.polylines(t, [d(p.narozniki_termal)], True, (255, 0, 255), 2, cv2.LINE_AA)
    cv2.polylines(t, [d(nar_T)], True, (0, 220, 0), 2, cv2.LINE_AA)
    for kont in geo.kontury(znamie_gesta.astype(np.uint8)):
        cv2.polylines(t, [d((kont + 0.5) / GESTOSC - 0.5)], True, (0, 0, 255), 2, cv2.LINE_AA)
    for a, b in zip(d(nar_T), d(p.narozniki_termal)):
        cv2.line(t, tuple(int(v) for v in a), tuple(int(v) for v in b), (255, 255, 255), 2, cv2.LINE_AA)
    ob["termal"] = t

    # nalozenie: termowizja w geometrii zdjecia, 50 %, kadr wokol znacznika
    H, W = p.rgb.shape[:2]
    Minv = np.linalg.inv(M)
    tw = cv2.warpPerspective(p.termal, Minv, (W, H), flags=cv2.INTER_LINEAR)
    pole = cv2.warpPerspective(np.full(p.termal.shape[:2], 255, np.uint8), Minv, (W, H)) > 127
    nal = p.rgb.copy()
    nal[pole] = (0.5 * p.rgb[pole] + 0.5 * tw[pole]).astype(np.uint8)
    k, o = _kadr(nal, p.narozniki_rgb)
    sk = 900 / k.shape[1]
    ob["nakladka"] = cv2.resize(k, None, fx=sk, fy=sk, interpolation=cv2.INTER_AREA)

    # powiekszenie wokol znamienia na mapie °C
    ys, xs = np.nonzero(znamie_gesta)
    cy, cx = ys.mean() / GESTOSC, xs.mean() / GESTOSC
    s_t = geo.mm_na_px(p.H_termal, p.narozniki_termal.mean(0))
    r = int(np.ceil(6.0 / s_t))                                       # +- 6 mm
    y0, y1 = int(max(0, cy - r)), int(min(p.T.shape[0], cy + r + 1))
    x0, x1 = int(max(0, cx - r)), int(min(p.T.shape[1], cx + r + 1))
    okno = p.T[y0:y1, x0:x1]
    folia = (cv2.dilate(p.maska_znacznik_termal, np.ones((5, 5), np.uint8)) > 0)[y0:y1, x0:x1]
    v = okno[~folia] if (~folia).any() else okno.ravel()
    lo, hi = np.percentile(v, 1), np.percentile(v, 99)
    u8 = np.clip((okno - lo) / max(hi - lo, 1e-3) * 255, 0, 255).astype(np.uint8)
    zz = 24
    zm = cv2.resize(cv2.applyColorMap(u8, cv2.COLORMAP_INFERNO), None, fx=zz, fy=zz, interpolation=cv2.INTER_NEAREST)
    dz = lambda pts: np.round((np.asarray(pts) - [x0, y0] + 0.5) * zz).astype(np.int32)
    for kont in _brzegi(pierscien_t[y0:y1, x0:x1]):
        cv2.polylines(zm, [dz(kont + [x0, y0])], True, (255, 255, 255), 2, cv2.LINE_AA)
    for kont in geo.kontury(znamie_gesta.astype(np.uint8)):
        cv2.polylines(zm, [dz((kont + 0.5) / GESTOSC - 0.5)], True, (0, 0, 255), 2, cv2.LINE_AA)
    _napis(zm, f"{lo:.1f} - {hi:.1f} C", (10, 36), 1.1)
    ob["znamie"] = zm

    for nazwa, img in ob.items():
        cv2.imwrite(str(kat_dop.parent.parent / "wyniki_obu" / f"para_{p.n}" / f"{nazwa}.png"), img)
    return ob


def _bez_tablic(x):
    if isinstance(x, dict):
        return {k: _bez_tablic(v) for k, v in x.items() if not k.startswith("_")}
    if isinstance(x, (list, tuple)):
        return [_bez_tablic(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    return x


def main():
    ap = argparse.ArgumentParser(description="Potok analizy jednej pary RGB - termowizja")
    ap.add_argument("para", type=int)
    ap.add_argument("--model", default="auto", choices=["auto", "afiniczna", "homografia"])
    a = ap.parse_args()
    kat = INZ / "wyniki" / "wyniki_obu" / f"para_{a.para}"
    kat.mkdir(parents=True, exist_ok=True)
    w, obrazy = analizuj(a.para, a.model)
    (kat / "metryki.json").write_text(json.dumps(_bez_tablic(w), indent=1, ensure_ascii=False), encoding="utf-8")
    raport.zapisz(kat / "raport.html", w, obrazy)
    zg, rgb, ter = w["zgodnosc"], w["pomiary_rgb"], w["pomiary_termiczne"]
    print(f"Para {a.para}: model {w['rejestracja'].get('model')}, TRE {zg['tre']['tre_srednie']:.2f} mm "
          f"(max {zg['tre']['tre_max']:.2f}), Dice obrysu {zg['obrys']['dice']:.3f}, otworu {zg['otwor']['dice']:.3f}")
    print(f"  znamie: {rgb['pole_mm2']:.2f} mm2, srednica {rgb['srednica_rownowazna_mm']:.2f} mm, "
          f"T {ter.get('T_znamie_srednia', float('nan')):.2f} °C, skora {ter.get('T_skora_srednia', float('nan')):.2f} °C, "
          f"ΔT {ter.get('delta_T', float('nan')):+.2f} °C")
    print(f"  raport: {kat / 'raport.html'}")


if __name__ == "__main__":
    main()
