"""
Raport zbiorczy dla wszystkich par z bazy: jakosc rejestracji (badanie E1), segmentacja PanDerm wzgledem
adnotacji z CVAT, narozniki znacznika, kontrola skali i parametry znamion.
Czyta wyniki potoku (potok_pary.bat 1-94): wyniki/wyniki_obu/para_N/metryki.json.

    raport_zbiorczy.bat                     (albo: python raport_zbiorczy.py [--wyjscie FOLDER])

Wynik w wyniki/raport_zbiorczy/:
    raport_zbiorczy.html  podsumowanie, statystyki, wykresy, pary odrzucone i ostrzezenia, tabela par
                          (kolumny sortowane kliknieciem, numer pary prowadzi do jej raportu)
    pary.csv              jeden wiersz na pare (separator ;, przecinek dziesietny - pod polskiego Excela)
    statystyki.csv        n, srednia, odchylenie, mediana, min, max kazdej miary
    tabele.tex            tabele do pracy (LaTeX, pakiet booktabs)

Para bez metryki.json (albo z blad.txt nowszym niz metryki.json) trafia do par odrzuconych z powodem:
tresc blad.txt zapisanego przez potok albo, dla starszych przebiegow, zgodnosc znacznika z log-u rejestracji.
Statystyki licza sie tylko z par przeanalizowanych.
"""
import argparse
import csv
import html
import json
import re
from datetime import datetime
from pathlib import Path

import numpy as np

INZ = Path(__file__).resolve().parent.parent
PARY = INZ / "dane" / "pary"
WYNIKI_OBU = INZ / "wyniki" / "wyniki_obu"
REJESTRACJA = INZ / "wyniki" / "wyniki_dopasowania"
MIN_ZGODNOSC = 0.65            # jak dopasowanie3.MIN_ZGODNOSC

# klucz, opis, jednostka, sciezka w metryki.json, miejsca po przecinku, grupa
MIARY = [
    ("tre_sr", "TRE – średni błąd narożników", "mm", ("zgodnosc", "tre", "tre_srednie"), 2, "rej"),
    ("tre_max", "TRE – największy błąd narożnika", "mm", ("zgodnosc", "tre", "tre_max"), 2, "rej"),
    ("obrys_dice", "Dice obrysu znacznika", "", ("zgodnosc", "obrys", "dice"), 3, "rej"),
    ("obrys_iou", "IoU obrysu znacznika", "", ("zgodnosc", "obrys", "iou"), 3, "rej"),
    ("obrys_hd95", "HD95 obrysu znacznika", "mm", ("zgodnosc", "obrys", "hd95_mm"), 2, "rej"),
    ("obrys_assd", "ASSD obrysu znacznika", "mm", ("zgodnosc", "obrys", "assd_mm"), 2, "rej"),
    ("obrys_srodki", "Przesunięcie środków obrysu", "mm", ("zgodnosc", "obrys", "przesuniecie_srodkow_mm"), 2, "rej"),
    ("obrys_pola", "Stosunek pól obrysu (przeniesiony / CVAT)", "", ("zgodnosc", "obrys", "stosunek_pol"), 3, "rej"),
    ("otwor_dice", "Dice otworu znacznika", "", ("zgodnosc", "otwor", "dice"), 3, "rej"),
    ("otwor_hd95", "HD95 otworu znacznika", "mm", ("zgodnosc", "otwor", "hd95_mm"), 2, "rej"),
    ("zg_rgb", "Zgodność znacznika z wzorcem Π – zdjęcie", "", ("rejestracja", "zgodnosc_rgb"), 3, "znacznik"),
    ("zg_ter", "Zgodność znacznika z wzorcem Π – termowizja", "", ("rejestracja", "zgodnosc_termal"), 3, "znacznik"),
    ("nar_cvat", "Narożniki automatyczne vs CVAT (zdjęcie)", "mm", ("narozniki", "rgb_blad_vs_cvat_mm"), 2, "znacznik"),
    ("otwor_pole", "Pole otworu przeniesionego na termowizję", "mm²",
     ("kontrola_skali", "pole_otworu_przeniesionego_mm2"), 1, "znacznik"),
    ("otwor_stos", "Pole otworu przeniesionego / 289 mm²", "", ("kontrola_skali", "stosunek_pol_otworu"), 3, "znacznik"),
    ("mm_px_ter", "Rozmiar piksela termowizji na skórze", "mm", ("kontrola_skali", "mm_na_px_termal"), 3, "znacznik"),
    ("seg_dice", "Dice", "", ("segmentacja_vs_cvat", "dice"), 3, "seg"),
    ("seg_iou", "IoU", "", ("segmentacja_vs_cvat", "iou"), 3, "seg"),
    ("seg_hd95", "HD95", "mm", ("segmentacja_vs_cvat", "hd95_mm"), 2, "seg"),
    ("seg_assd", "ASSD", "mm", ("segmentacja_vs_cvat", "assd_mm"), 2, "seg"),
    ("seg_srodki", "Przesunięcie środków", "mm", ("segmentacja_vs_cvat", "przesuniecie_srodkow_mm"), 2, "seg"),
    ("seg_pola", "Stosunek pól (PanDerm / CVAT)", "", ("segmentacja_vs_cvat", "stosunek_pol"), 2, "seg"),
    ("pole", "Pole (PanDerm)", "mm²", ("pomiary_rgb", "pole_mm2"), 2, "znamie"),
    ("pole_cvat", "Pole (CVAT)", "mm²", ("segmentacja_vs_cvat", "pole_cvat_mm2"), 2, "znamie"),
    ("srednica", "Średnica równoważna", "mm", ("pomiary_rgb", "srednica_rownowazna_mm"), 2, "znamie"),
    ("feret_max", "Średnica Fereta maks.", "mm", ("pomiary_rgb", "feret_max_mm"), 2, "znamie"),
    ("feret_min", "Średnica Fereta min.", "mm", ("pomiary_rgb", "feret_min_mm"), 2, "znamie"),
    ("obwod", "Obwód", "mm", ("pomiary_rgb", "obwod_mm"), 2, "znamie"),
    ("kolistosc", "Kolistość", "", ("pomiary_rgb", "kolistosc"), 3, "znamie"),
    ("asym1", "Asymetria – oś główna", "", ("pomiary_rgb", "asymetria_os_glowna"), 3, "znamie"),
    ("asym2", "Asymetria – oś prostopadła", "", ("pomiary_rgb", "asymetria_os_prostopadla"), 3, "znamie"),
    ("px_ter", "Piksele znamienia na termowizji", "px", ("kontrola_skali", "piksele_znamienia_termal"), 0, "znamie"),
    ("pole_ter_rgb", "Pole znamienia: termowizja / zdjęcie", "", ("kontrola_skali", "pole_znamienia_termal_do_rgb"), 3,
     "znamie"),
]
GRUPY = {"rej": "Rejestracja (badanie E1): narożniki i obrys znacznika z CVAT, zdjęcie → T → termowizja",
         "znacznik": "Znacznik: wykrycie, narożniki automatyczne, kontrola skali",
         "seg": "Segmentacja znamienia: PanDerm względem obrysu z CVAT (zdjęcie)",
         "znamie": "Parametry znamion (opisowo)"}
OPIS = {m[0]: m for m in MIARY}


# ── wczytanie ────────────────────────────────────────────────────────────────

def _wartosc(d, sciezka):
    for k in sciezka:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return float(d) if isinstance(d, (int, float)) else None


def _powod_z_logu(n):
    """Powod odrzucenia pary bez blad.txt: zgodnosc znacznika z log-u rejestracji."""
    log = REJESTRACJA / f"para_{n}" / "rejestracja_log.txt"
    if not log.exists():
        return "brak wyników rejestracji"
    t = log.read_text(encoding="utf-8", errors="replace")
    czesci = []
    for nazwa, klucz in (("zdjęcie", "rgb"), ("termowizja", "termal")):
        m = re.search(rf"\[{klucz}\].*?zgodnosc z wzorcem Pi=([\d.]+)", t)
        if m and float(m.group(1)) < MIN_ZGODNOSC:
            czesci.append(f"znacznik na obrazie „{nazwa}” wykryty niepewnie (zgodność z Π {float(m.group(1)):.2f} "
                          f"< {MIN_ZGODNOSC:.2f})")
    powod = "potok przerwał analizę (brak metryki.json)"
    return powod + (": " + "; ".join(czesci) if czesci else "")


def wczytaj():
    """(wiersze par przeanalizowanych, lista odrzuconych (para, powod))."""
    numery = sorted(int(k.name) for k in PARY.iterdir() if k.is_dir() and k.name.isdigit())
    wiersze, odrzucone = [], []
    for n in numery:
        kat = WYNIKI_OBU / f"para_{n}"
        plik, blad = kat / "metryki.json", kat / "blad.txt"
        if blad.exists() and (not plik.exists() or blad.stat().st_mtime >= plik.stat().st_mtime):
            odrzucone.append((n, "błąd w potoku: " + blad.read_text(encoding="utf-8", errors="replace").strip()))
            continue
        if not plik.exists():
            odrzucone.append((n, _powod_z_logu(n)))
            continue
        d = json.loads(plik.read_text(encoding="utf-8"))
        info = d.get("info", {})
        w = {"para": n, "znamie": info.get("znamie", ""), "fold": info.get("fold", ""),
             "model": d.get("rejestracja", {}).get("model", ""), "raport": f"../wyniki_obu/para_{n}/raport.html"}
        for klucz, _, _, sciezka, _, _ in MIARY:
            w[klucz] = _wartosc(d, sciezka)
        w["ostrzezenia"] = ostrzezenia(w)
        wiersze.append(w)
    return wiersze, odrzucone


def ostrzezenia(w):
    o = []
    for k, nazwa in (("zg_rgb", "zdjęciu"), ("zg_ter", "termowizji")):
        if w[k] is not None and w[k] < MIN_ZGODNOSC:
            o.append(f"znacznik na {nazwa} wykryty niepewnie ({_l(w[k], 2)})")
    if w["tre_sr"] is not None and w["tre_sr"] > 2:
        o.append(f"duży błąd rejestracji (TRE {_l(w['tre_sr'], 2)} mm)")
    if w["seg_dice"] is not None and w["seg_dice"] < 0.5:
        o.append(f"segmentacja niezgodna z CVAT (Dice {_l(w['seg_dice'], 2)})")
    elif w["seg_dice"] is not None and w["seg_dice"] < 0.7:
        o.append(f"słaba segmentacja (Dice {_l(w['seg_dice'], 2)})")
    if w["otwor_stos"] is not None and abs(w["otwor_stos"] - 1) > 0.1:
        o.append(f"kontrola skali: pole otworu {_l(100 * w['otwor_stos'], 0)}% wzorca")
    return o


# ── statystyki ───────────────────────────────────────────────────────────────

def _l(x, miejsca):
    """Liczba z przecinkiem dziesietnym."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    return f"{x:.{miejsca}f}".replace(".", ",").replace("-", "−")


def statystyki(wiersze):
    s = {}
    for klucz, *_ in MIARY:
        v = np.array([w[klucz] for w in wiersze if w[klucz] is not None], np.float64)
        if v.size == 0:
            continue
        s[klucz] = {"n": int(v.size), "srednia": float(v.mean()), "odch": float(v.std(ddof=1)) if v.size > 1 else 0.0,
                    "mediana": float(np.median(v)), "min": float(v.min()), "max": float(v.max()),
                    "q1": float(np.percentile(v, 25)), "q3": float(np.percentile(v, 75)), "wartosci": v}
    return s


def podsumowanie(wiersze, odrzucone, s):
    n = len(wiersze) + len(odrzucone)
    tre = s["tre_sr"]["wartosci"] if "tre_sr" in s else np.array([])
    dice = s["seg_dice"]["wartosci"] if "seg_dice" in s else np.array([])
    modele = {}
    for w in wiersze:
        modele[w["model"]] = modele.get(w["model"], 0) + 1
    return {"n": n, "ok": len(wiersze), "odrzucone": len(odrzucone),
            "tre_mediana": float(np.median(tre)) if tre.size else None,
            "tre_le1": int((tre <= 1).sum()), "tre_le2": int((tre <= 2).sum()), "n_tre": int(tre.size),
            "dice_srednia": float(dice.mean()) if dice.size else None,
            "dice_mediana": float(np.median(dice)) if dice.size else None,
            "dice_ge08": int((dice >= 0.8).sum()), "dice_lt05": int((dice < 0.5).sum()), "n_dice": int(dice.size),
            "modele": modele}


# ── wykresy (SVG bez dodatkowych bibliotek) ─────────────────────────────────

KOLOR, SZARY, AKCENT = "#2b6cb0", "#8a8f98", "#c05621"


def _os(lo, hi, kroki=5):
    """Ladne podzialki osi."""
    if hi <= lo:
        hi = lo + 1
    surowy = (hi - lo) / kroki
    rzad = 10 ** np.floor(np.log10(surowy))
    krok = min((m * rzad for m in (1, 2, 2.5, 5, 10) if m * rzad >= surowy), default=surowy)
    a, b = np.floor(lo / krok) * krok, np.ceil(hi / krok) * krok
    return [float(v) for v in np.arange(a, b + krok / 2, krok)], krok


def _miejsca(krok):
    return max(0, int(-np.floor(np.log10(krok)))) if krok < 1 else 0


def _poza(v, pary, lo, hi, miejsca=2):
    """Opis wartosci poza zakresem osi: 'para 78 (24,69)'."""
    poza = [(n, x) for n, x in zip(pary, v) if x < lo or x > hi]
    return ", ".join(f"para {n} ({_l(x, miejsca)})" for n, x in sorted(poza, key=lambda t: -abs(t[1])))


def svg_histogram(v, pary, tytul, os_x, krok_kosza, zakres=None, odniesienie=None):
    """Histogram; zakres=(lo, hi) przycina os - wartosci spoza sa wypisane pod wykresem."""
    W, H, L, R, T, B = 640, 318, 56, 20, 40, 66
    lo_d, hi_d = (float(v.min()), float(v.max())) if zakres is None else zakres
    w_osi = v[(v >= lo_d) & (v <= hi_d)]
    lo = np.floor(w_osi.min() / krok_kosza) * krok_kosza
    hi = np.ceil(w_osi.max() / krok_kosza + 1e-9) * krok_kosza
    hi = hi + krok_kosza if hi <= w_osi.max() else hi
    kosze = np.arange(lo, hi + krok_kosza / 2, krok_kosza)
    licz, _ = np.histogram(w_osi, kosze)
    ticks, krok = _os(lo, hi, 6)
    lo, hi = ticks[0], ticks[-1]
    yt, _ = _os(0, max(1, int(licz.max())), 4)
    X = lambda x: L + (x - lo) / (hi - lo) * (W - L - R)
    Y = lambda y: H - B - y / yt[-1] * (H - T - B)
    e = [f"<svg viewBox='0 0 {W} {H}' class='wykres' role='img' aria-label='{html.escape(tytul)}'>",
         f"<text x='{L}' y='22' class='tyt'>{html.escape(tytul)}</text>"]
    for t in yt:
        e.append(f"<line x1='{L}' x2='{W - R}' y1='{Y(t):.1f}' y2='{Y(t):.1f}' class='siatka'/>"
                 f"<text x='{L - 8}' y='{Y(t) + 4:.1f}' text-anchor='end'>{int(t)}</text>")
    for a, b, c in zip(kosze[:-1], kosze[1:], licz):
        if c:
            e.append(f"<rect x='{X(a) + 1:.1f}' y='{Y(c):.1f}' width='{max(1, X(b) - X(a) - 2):.1f}' "
                     f"height='{Y(0) - Y(c):.1f}' fill='{KOLOR}' fill-opacity='0.75'><title>{_l(a, 2)}–{_l(b, 2)}: "
                     f"{c} par</title></rect>")
    for t in ticks:
        e.append(f"<text x='{X(t):.1f}' y='{H - B + 18}' text-anchor='middle'>{_l(t, _miejsca(krok))}</text>")
    e.append(f"<line x1='{L}' x2='{W - R}' y1='{Y(0):.1f}' y2='{Y(0):.1f}' class='os'/>")
    med = float(np.median(v))
    if lo <= med <= hi:
        e.append(f"<line x1='{X(med):.1f}' x2='{X(med):.1f}' y1='{T}' y2='{Y(0):.1f}' stroke='{AKCENT}' "
                 f"stroke-width='2' stroke-dasharray='5 4'/><text x='{X(med) + 6:.1f}' y='{T + 12}' fill='{AKCENT}'>"
                 f"mediana {_l(med, 2)}</text>")
    if odniesienie is not None and lo <= odniesienie[0] <= hi:
        x0, opis = odniesienie
        e.append(f"<line x1='{X(x0):.1f}' x2='{X(x0):.1f}' y1='{T}' y2='{Y(0):.1f}' stroke='{SZARY}' "
                 f"stroke-dasharray='2 3'/><text x='{X(x0) + 6:.1f}' y='{T + 28}' fill='{SZARY}'>{opis}</text>")
    e.append(f"<text x='{(L + W - R) / 2}' y='{H - B + 38}' text-anchor='middle'>{html.escape(os_x)}</text>"
             f"<text x='14' y='{(T + H - B) / 2}' transform='rotate(-90 14 {(T + H - B) / 2})' "
             f"text-anchor='middle'>liczba par</text>")
    poza = _poza(v, pary, lo_d, hi_d)
    if poza:
        e.append(f"<text x='{L}' y='{H - 6}' fill='{AKCENT}'>poza osią: {html.escape(poza)}</text>")
    return "".join(e) + "</svg>"


def svg_pudelka(serie, tytul, os_x):
    """serie: [(etykieta, wartosci, pary)] - wykresy pudelkowe poziomo; wasy do 1,5 IQR (Tukey),
    pozostale wartosci jako punkty; os do najdluzszego wasa, dalsze punkty wypisane przy prawej krawedzi."""
    W, L, R, T, wiersz = 640, 210, 96, 40, 40
    H = T + wiersz * len(serie) + 44
    wasy = []
    for _, v, _ in serie:
        q1, q3 = np.percentile(v, [25, 75])
        wasy.append((float(v[v >= q1 - 1.5 * (q3 - q1)].min()), float(v[v <= q3 + 1.5 * (q3 - q1)].max())))
    ticks, krok = _os(0, 1.15 * max(g for _, g in wasy), 6)
    X = lambda x: L + x / ticks[-1] * (W - L - R)
    e = [f"<svg viewBox='0 0 {W} {H}' class='wykres' role='img' aria-label='{html.escape(tytul)}'>",
         f"<text x='16' y='22' class='tyt'>{html.escape(tytul)}</text>"]
    yb = T + wiersz * len(serie)
    for t in ticks:
        e.append(f"<line x1='{X(t):.1f}' x2='{X(t):.1f}' y1='{T}' y2='{yb}' class='siatka'/>"
                 f"<text x='{X(t):.1f}' y='{yb + 18}' text-anchor='middle'>{_l(t, _miejsca(krok))}</text>")
    for i, ((etyk, v, pary), (wd, wg)) in enumerate(zip(serie, wasy)):
        y = T + wiersz * i + wiersz / 2
        q1, med, q3 = np.percentile(v, [25, 50, 75])
        e.append(f"<text x='{L - 10}' y='{y + 4:.1f}' text-anchor='end'>{html.escape(etyk)}</text>"
                 f"<line x1='{X(wd):.1f}' x2='{X(wg):.1f}' y1='{y:.1f}' y2='{y:.1f}' stroke='{SZARY}'/>"
                 f"<rect x='{X(q1):.1f}' y='{y - 11:.1f}' width='{max(1, X(q3) - X(q1)):.1f}' height='22' "
                 f"fill='{KOLOR}' fill-opacity='0.18' stroke='{KOLOR}'><title>mediana {_l(med, 2)}, "
                 f"kwartyle {_l(q1, 2)}–{_l(q3, 2)}</title></rect>"
                 f"<line x1='{X(med):.1f}' x2='{X(med):.1f}' y1='{y - 11:.1f}' y2='{y + 11:.1f}' stroke='{AKCENT}' "
                 f"stroke-width='2.5'/>")
        dalej = []
        for n, x in zip(pary, v):
            if wd <= x <= wg:
                continue
            if x <= ticks[-1]:
                e.append(f"<circle cx='{X(x):.1f}' cy='{y:.1f}' r='3' fill='none' stroke='{KOLOR}'>"
                         f"<title>para {n}: {_l(x, 2)}</title></circle>")
            else:
                dalej.append((n, x))
        if dalej:
            dalej.sort(key=lambda t: -t[1])
            opis = f"{dalej[0][0]}: {_l(dalej[0][1], 1)}" + (f" (+{len(dalej) - 1})" if len(dalej) > 1 else "")
            e.append(f"<text x='{W - R + 6}' y='{y + 4:.1f}' font-size='11' fill='{AKCENT}'>"
                     f"→ {html.escape(opis)}<title>poza osią: "
                     f"{html.escape(', '.join(f'para {n}: {_l(x, 2)}' for n, x in dalej))}</title></text>")
    e.append(f"<text x='{(L + W - R) / 2}' y='{H - 6}' text-anchor='middle'>{html.escape(os_x)}</text></svg>")
    return "".join(e)


def svg_bland_altman(a, b, pary, tytul, jednostka):
    """Bland-Altman: x = srednia (a+b)/2, y = roznica a-b; linie: srednia roznica i +-1,96 SD."""
    sr, rz = (a + b) / 2, a - b
    bias, sd = float(rz.mean()), float(rz.std(ddof=1))
    W, H, L, R, T, B = 640, 320, 64, 150, 40, 48
    xt, xk = _os(0, float(sr.max()), 6)
    ylo, yhi = min(float(rz.min()), bias - 1.96 * sd), max(float(rz.max()), bias + 1.96 * sd)
    yt, yk = _os(ylo, yhi, 5)
    X = lambda x: L + (x - xt[0]) / (xt[-1] - xt[0]) * (W - L - R)
    Y = lambda y: H - B - (y - yt[0]) / (yt[-1] - yt[0]) * (H - T - B)
    e = [f"<svg viewBox='0 0 {W} {H}' class='wykres' role='img' aria-label='{html.escape(tytul)}'>",
         f"<text x='{L}' y='22' class='tyt'>{html.escape(tytul)}</text>"]
    for t in yt:
        e.append(f"<line x1='{L}' x2='{W - R}' y1='{Y(t):.1f}' y2='{Y(t):.1f}' class='siatka'/>"
                 f"<text x='{L - 8}' y='{Y(t) + 4:.1f}' text-anchor='end'>{_l(t, _miejsca(yk))}</text>")
    for t in xt:
        e.append(f"<text x='{X(t):.1f}' y='{H - B + 18}' text-anchor='middle'>{_l(t, _miejsca(xk))}</text>")
    for y0, opis, kol, kreska in ((bias, f"średnia {_l(bias, 2)}", AKCENT, ""),
                                  (bias + 1.96 * sd, f"+1,96 SD {_l(bias + 1.96 * sd, 2)}", SZARY, "5 4"),
                                  (bias - 1.96 * sd, f"−1,96 SD {_l(bias - 1.96 * sd, 2)}", SZARY, "5 4")):
        e.append(f"<line x1='{L}' x2='{W - R}' y1='{Y(y0):.1f}' y2='{Y(y0):.1f}' stroke='{kol}' stroke-width='1.5' "
                 f"stroke-dasharray='{kreska}'/><text x='{W - R + 6}' y='{Y(y0) + 4:.1f}' fill='{kol}'>{opis}</text>")
    for x, y, n in zip(sr, rz, pary):
        e.append(f"<circle cx='{X(x):.1f}' cy='{Y(y):.1f}' r='3.5' fill='{KOLOR}' fill-opacity='0.7'>"
                 f"<title>para {n}: średnia {_l(x, 2)}, różnica {_l(y, 2)} {jednostka}</title></circle>")
    e.append(f"<text x='{(L + W - R) / 2}' y='{H - 8}' text-anchor='middle'>średnia dwóch pomiarów [{jednostka}]</text>"
             f"<text x='14' y='{(T + H - B) / 2}' transform='rotate(-90 14 {(T + H - B) / 2})' text-anchor='middle'>"
             f"różnica [{jednostka}]</text></svg>")
    return "".join(e), bias, sd


# ── zapis ────────────────────────────────────────────────────────────────────

def zapisz_csv(wiersze, s, kat):
    pola = ["para", "znamie", "fold", "model"] + [m[0] for m in MIARY] + ["ostrzezenia"]
    with open(kat / "pary.csv", "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f, delimiter=";")
        wr.writerow(pola)
        for w in wiersze:
            wr.writerow([w["para"], w["znamie"], w["fold"], w["model"]]
                        + [("" if w[m[0]] is None else f"{w[m[0]]:.6g}".replace(".", ",")) for m in MIARY]
                        + [" | ".join(w["ostrzezenia"])])
    with open(kat / "statystyki.csv", "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f, delimiter=";")
        wr.writerow(["miara", "opis", "jednostka", "n", "srednia", "odchylenie", "mediana", "min", "max"])
        for klucz, opis, jedn, *_ in MIARY:
            if klucz in s:
                t = s[klucz]
                wr.writerow([klucz, opis, jedn, t["n"]] + [f"{t[k]:.6g}".replace(".", ",")
                                                          for k in ("srednia", "odch", "mediana", "min", "max")])


def _tex(t):
    return (t.replace("\\", "\\textbackslash{}").replace("%", "\\%").replace("&", "\\&").replace("_", "\\_")
            .replace("±", "$\\pm$").replace("mm²", "mm$^2$").replace("Π", "$\\Pi$").replace("→", "$\\to$"))


def zapisz_tex(s, pod, kat):
    tabele = [
        ("rej", "Jakość rejestracji (badanie E1): narożniki i obrys znacznika zaznaczone ręcznie na zdjęciu, "
                "przeniesione macierzą T, względem zaznaczonych ręcznie na termowizji", "tab:e1"),
        ("znacznik", "Wykrycie znacznika, narożniki wyznaczane automatycznie i kontrola skali", "tab:znacznik"),
        ("seg", "Segmentacja znamienia modelem PanDerm względem obrysu z CVAT", "tab:segmentacja"),
        ("znamie", "Parametry znamion zmierzone przez system", "tab:znamiona"),
    ]
    o = [f"% Tabele z raport_zbiorczy.py ({datetime.now():%d.%m.%Y %H:%M}); wymagaja \\usepackage{{booktabs}}.",
         f"% Pary przeanalizowane: {pod['ok']} z {pod['n']}.", ""]
    for grupa, podpis, etykieta in tabele:
        o += ["\\begin{table}[htbp]", "\\centering",
              f"\\caption{{{_tex(podpis)} ($n = {pod['ok']}$ par)}}", f"\\label{{{etykieta}}}",
              "\\begin{tabular}{lrrrr}", "\\toprule",
              "Miara & Średnia $\\pm$ odch. & Mediana & Min & Maks \\\\", "\\midrule"]
        for klucz, opis, jedn, _, miejsca, g in MIARY:
            if g != grupa or klucz not in s:
                continue
            t = s[klucz]
            nazwa = _tex(opis + (f" [{jedn}]" if jedn else ""))
            o.append(f"{nazwa} & {_l(t['srednia'], miejsca)} $\\pm$ {_l(t['odch'], miejsca)} & "
                     f"{_l(t['mediana'], miejsca)} & {_l(t['min'], miejsca)} & {_l(t['max'], miejsca)} \\\\"
                     .replace("−", "$-$"))
        o += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    (kat / "tabele.tex").write_text("\n".join(o), encoding="utf-8")


CSS = """
body{font-family:Segoe UI,Arial,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;color:#1f2328;
background:#fff;line-height:1.45}
h1{font-size:24px}h2{font-size:19px;margin-top:32px;border-bottom:1px solid #d0d7de;padding-bottom:4px}
table{border-collapse:collapse;font-size:13px;margin:8px 0}th,td{border:1px solid #d0d7de;padding:4px 7px}
th{background:#f6f8fa;text-align:left}td.l{text-align:right;font-variant-numeric:tabular-nums}
.par th{cursor:pointer;position:sticky;top:0}.par tr.zle td{background:#fff5f0}
.wykres{width:100%;max-width:640px;font-size:12px;fill:#1f2328}.wykres .tyt{font-size:14px;font-weight:600}
.wykres .siatka{stroke:#e5e7eb}.wykres .os{stroke:#8a8f98}
.siatka2{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:16px}
.uwaga{color:#57606a;font-size:13px}.ostrz{color:#9a3412}.par td.ostrz{min-width:320px}
.przewijana{overflow-x:auto}.par{font-size:12px}
"""

SORT_JS = """
document.querySelectorAll('table.par th').forEach((th,i)=>th.addEventListener('click',()=>{
const tb=th.closest('table').tBodies[0],r=[...tb.rows],d=th.dataset.d==='1'?-1:1;th.dataset.d=d===1?'1':'0';
const v=x=>{const t=x.cells[i].dataset.v??x.cells[i].textContent;const n=parseFloat(t);return isNaN(n)?t:n};
r.sort((a,b)=>{const x=v(a),y=v(b);return (x>y?1:x<y?-1:0)*d});r.forEach(x=>tb.appendChild(x));}));
"""


def zapisz_html(wiersze, odrzucone, s, pod, kat):
    e = html.escape
    p = pod
    czesci = [f"<!doctype html><html lang='pl'><head><meta charset='utf-8'><title>Raport zbiorczy</title>"
              f"<style>{CSS}</style></head><body>",
              f"<h1>Raport zbiorczy – {p['ok']} z {p['n']} par</h1>",
              f"<p class='uwaga'>Wygenerowano {datetime.now():%d.%m.%Y %H:%M} z wyniki/wyniki_obu/para_N/metryki.json "
              f"(potok_pary.bat). Statystyki z {p['ok']} przeanalizowanych par.</p>",
              "<h2>Podsumowanie</h2><ul>",
              f"<li>Przeanalizowane pary: <b>{p['ok']}/{p['n']}</b>; odrzucone: {p['odrzucone']} (lista niżej).</li>"]
    if p["tre_mediana"] is not None:
        czesci.append(f"<li>Rejestracja (E1): mediana TRE <b>{_l(p['tre_mediana'], 2)} mm</b>; TRE ≤ 1 mm na "
                      f"{p['tre_le1']}/{p['n_tre']} parach, ≤ 2 mm na {p['tre_le2']}/{p['n_tre']}.</li>")
    if p["dice_srednia"] is not None:
        czesci.append(f"<li>Segmentacja PanDerm vs CVAT: Dice średnio <b>{_l(p['dice_srednia'], 3)}</b>, mediana "
                      f"{_l(p['dice_mediana'], 3)}; Dice ≥ 0,8 na {p['dice_ge08']}/{p['n_dice']}, &lt; 0,5 na "
                      f"{p['dice_lt05']}/{p['n_dice']}.</li>")
    czesci.append("<li>Model przekształcenia: " + ", ".join(f"{e(k)} {v}" for k, v in sorted(p["modele"].items()))
                  + "</li></ul>")

    czesci.append("<h2>Pary odrzucone i ostrzeżenia</h2>")
    if odrzucone:
        czesci.append("<table><tr><th>Para</th><th>Powód odrzucenia</th></tr>" + "".join(
            f"<tr><td class='l'>{n}</td><td>{e(pw)}</td></tr>" for n, pw in odrzucone) + "</table>")
    z_ostrz = [w for w in wiersze if w["ostrzezenia"]]
    if z_ostrz:
        czesci.append(f"<p>Pary przeanalizowane z ostrzeżeniem: {len(z_ostrz)}.</p><table><tr><th>Para</th>"
                      "<th>Ostrzeżenia</th></tr>" + "".join(
                          f"<tr><td class='l'><a href='{w['raport']}'>{w['para']}</a></td>"
                          f"<td class='ostrz'>{e('; '.join(w['ostrzezenia']))}</td></tr>" for w in z_ostrz) + "</table>")

    czesci.append("<h2>Statystyki</h2>")
    for grupa, tytul in GRUPY.items():
        czesci.append(f"<h3>{e(tytul)}</h3><table><tr><th>Miara</th><th>n</th><th>Średnia ± odch.</th>"
                      "<th>Mediana</th><th>Min</th><th>Maks</th></tr>")
        for klucz, opis, jedn, _, m, g in MIARY:
            if g == grupa and klucz in s:
                t = s[klucz]
                czesci.append(f"<tr><td>{e(opis)}{' [' + e(jedn) + ']' if jedn else ''}</td><td class='l'>{t['n']}</td>"
                              f"<td class='l'>{_l(t['srednia'], m)} ± {_l(t['odch'], m)}</td>"
                              f"<td class='l'>{_l(t['mediana'], m)}</td><td class='l'>{_l(t['min'], m)}</td>"
                              f"<td class='l'>{_l(t['max'], m)}</td></tr>")
        czesci.append("</table>")

    czesci.append("<h2>Wykresy</h2><div class='siatka2'>")
    def kolumna(k):
        ww = [w for w in wiersze if w[k] is not None]
        return np.array([w[k] for w in ww]), [w["para"] for w in ww]
    if "tre_sr" in s:
        v, pary = kolumna("tre_sr")
        czesci.append(svg_histogram(v, pary, "Błąd rejestracji w narożnikach (TRE średni na parę)", "TRE [mm]", 0.1,
                                    (0, 3.0), (2.0, "2 mm")))
    if "seg_dice" in s:
        v, pary = kolumna("seg_dice")
        czesci.append(svg_histogram(v, pary, "Segmentacja PanDerm względem CVAT", "Dice", 0.05))
    etykiety = {"tre_sr": "TRE średni", "tre_max": "TRE największy", "nar_cvat": "Narożniki auto vs CVAT",
                "obrys_hd95": "HD95 obrysu znacznika", "otwor_hd95": "HD95 otworu znacznika",
                "seg_hd95": "HD95 znamienia (vs CVAT)"}
    serie = [(etykiety[k], *kolumna(k)) for k in etykiety if k in s]
    if serie:
        czesci.append(svg_pudelka(serie, "Błędy położenia w milimetrach", "mm"))
    pary_seg = [w for w in wiersze if w["pole"] is not None and w["pole_cvat"] is not None]
    if len(pary_seg) > 2:
        svg, bias, sd = svg_bland_altman(np.array([w["pole"] for w in pary_seg]),
                                         np.array([w["pole_cvat"] for w in pary_seg]), [w["para"] for w in pary_seg],
                                         "Pole znamienia: PanDerm − CVAT (Bland–Altman)", "mm²")
        czesci.append(svg)
    if "otwor_stos" in s:
        v, pary = kolumna("otwor_stos")
        czesci.append(svg_histogram(100 * (v - 1), pary, "Pole otworu przeniesionego na termowizję względem 289 mm²",
                                    "różnica pola [%]", 1.0, (-15, 15), (0.0, "289 mm²")))
    czesci.append("</div><p class='uwaga'>Najedź na punkt lub słupek, żeby zobaczyć numer pary i wartość. "
                  "Wykres pudełkowy: pudełko = kwartyle, kreska = mediana, wąsy do 1,5 rozstępu kwartylowego, "
                  "kółka = wartości odstające; za prawą krawędzią para z największą wartością poza osią "
                  "(w nawiasie liczba pozostałych).</p>")

    kol = ["tre_sr", "tre_max", "obrys_dice", "otwor_dice", "nar_cvat", "zg_rgb", "zg_ter", "otwor_stos",
           "seg_dice", "seg_hd95", "seg_pola", "pole", "srednica", "px_ter"]
    czesci.append("<h2>Wszystkie pary</h2><p class='uwaga'>Posortowane od największego błędu rejestracji; kliknij "
                  "nagłówek, żeby posortować inaczej. Numer pary otwiera jej raport. Wszystkie kolumny: pary.csv.</p>"
                  "<div class='przewijana'><table class='par'><thead><tr><th>Para</th><th>Znamię</th><th>Model</th>"
                  + "".join(f"<th title='{e(OPIS[k][1])}'>{e(_krotko(k))}</th>" for k in kol)
                  + "<th>Ostrzeżenia</th></tr></thead><tbody>")
    for w in sorted(wiersze, key=lambda w: -(w["tre_sr"] or 0)):
        czesci.append(f"<tr class='{'zle' if w['ostrzezenia'] else ''}'><td class='l' data-v='{w['para']}'>"
                      f"<a href='{w['raport']}'>{w['para']}</a></td><td class='l'>{w['znamie']}</td>"
                      f"<td>{e(w['model'])}</td>"
                      + "".join(f"<td class='l' data-v='{'' if w[k] is None else w[k]}'>{_l(w[k], OPIS[k][4])}</td>"
                                for k in kol)
                      + f"<td class='ostrz'>{e('; '.join(w['ostrzezenia']))}</td></tr>")
    czesci.append("</tbody></table></div>")
    czesci.append("<h2>Objaśnienie miar</h2><ul class='uwaga'>"
                  "<li><b>TRE</b> – odległość 8 narożników znacznika zaznaczonych w CVAT na zdjęciu i przeniesionych "
                  "macierzą T od narożników zaznaczonych w CVAT na termowizji (ocena samej rejestracji).</li>"
                  "<li><b>Dice, IoU</b> – pokrycie dwóch obszarów (1 = identyczne). <b>HD95</b> – odległość brzegów "
                  "w najgorszych miejscach (95. percentyl), <b>ASSD</b> – średnia odległość brzegów.</li>"
                  "<li><b>Obrys / otwór znacznika</b> – wielokąt z narożników CVAT ze zdjęcia przeniesiony przez T "
                  "względem wielokąta z narożników CVAT na termowizji.</li>"
                  "<li><b>Zgodność z wzorcem Π</b> – IoU kształtu wykrytej maski znacznika z wzorcem; poniżej 0,65 "
                  "wykrycie jest niepewne.</li>"
                  "<li><b>Pole otworu przeniesionego / 289 mm²</b> – otwór znacznika z automatycznych narożników "
                  "zdjęcia przeniesiony przez T i zmierzony w mm termowizji; 1 = zgodnie z rzeczywistym rozmiarem."
                  "</li><li><b>Bland–Altman</b> – różnica dwóch pomiarów względem ich średniej; linia ciągła = średnia "
                  "różnica (błąd systematyczny), przerywane = granice zgodności ±1,96 odchylenia.</li></ul>")
    czesci.append(f"<script>{SORT_JS}</script></body></html>")
    (kat / "raport_zbiorczy.html").write_text("".join(czesci), encoding="utf-8")


def _krotko(k):
    return {"tre_sr": "TRE śr. [mm]", "tre_max": "TRE maks. [mm]", "obrys_dice": "Dice obrysu",
            "otwor_dice": "Dice otworu", "nar_cvat": "Narożniki vs CVAT [mm]", "zg_rgb": "Zgodn. Π zdjęcie",
            "zg_ter": "Zgodn. Π termow.", "otwor_stos": "Otwór / 289", "seg_dice": "Dice znamienia",
            "seg_hd95": "HD95 znamienia [mm]", "seg_pola": "Pole PanDerm / CVAT", "pole": "Pole [mm²]",
            "srednica": "Średnica [mm]", "px_ter": "Piksele termowizji"}.get(k, k)


def main():
    ap = argparse.ArgumentParser(description="Raport zbiorczy wszystkich par (wyniki potoku)")
    ap.add_argument("--wyjscie", default=str(INZ / "wyniki" / "raport_zbiorczy"))
    a = ap.parse_args()
    kat = Path(a.wyjscie)
    kat.mkdir(parents=True, exist_ok=True)
    wiersze, odrzucone = wczytaj()
    if not wiersze:
        raise SystemExit(f"Brak wyników w {WYNIKI_OBU} - najpierw uruchom potok_pary.bat")
    s = statystyki(wiersze)
    pod = podsumowanie(wiersze, odrzucone, s)
    zapisz_csv(wiersze, s, kat)
    zapisz_tex(s, pod, kat)
    zapisz_html(wiersze, odrzucone, s, pod, kat)
    print(f"Pary: {pod['ok']}/{pod['n']} przeanalizowane, odrzucone: {[n for n, _ in odrzucone]}")
    if pod["tre_mediana"] is not None:
        print(f"TRE: mediana {pod['tre_mediana']:.2f} mm, <= 2 mm na {pod['tre_le2']}/{pod['n_tre']}")
    if pod["dice_srednia"] is not None:
        print(f"Segmentacja: Dice srednio {pod['dice_srednia']:.3f}, mediana {pod['dice_mediana']:.3f}")
    print(f"-> {kat / 'raport_zbiorczy.html'}")


if __name__ == "__main__":
    main()
