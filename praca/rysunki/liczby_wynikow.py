"""
Liczby do rozdzialow 5-7 i streszczen z wynikow systemu + dane do wykresow (wykresy_wyniki.py).

    python praca\\rysunki\\liczby_wynikow.py            (z folderu Inzynierka; Python z numpy, np. srodowisko aplikacji)

Uzyj po kazdym przeliczeniu wynikow (potok_pary.bat 1-94 --z_zapisanych, porownaj_rejestracje.py, ocen_unet_termal.bat):
  1. zbiera wyniki do praca/rysunki/dane_wynikow/ (pary.csv, porownanie_rejestracji.csv, unet_ocena.csv),
  2. wypisuje wszystkie liczby uzyte w tekscie wzoru z miejscem uzycia (podrozdzial) - porownaj z tekstem,
  3. potem: python praca\\rysunki\\wykresy_wyniki.py  (odswiezy wykresy rozdz. 6).
Statystyki bez scipy: test Wilcoxona (przyblizenie normalne, n > 20) i wspolczynnik Spearmana z rang.
"""
import csv
import json
import math
import re
import shutil
from pathlib import Path

import numpy as np

INZ = Path(__file__).resolve().parents[2]                 # folder Inzynierka
WYNIKI = INZ / "wyniki"
DANE = Path(__file__).resolve().parent / "dane_wynikow"


def _g(d, *klucze):
    for k in klucze:
        d = (d or {}).get(k)
    return d


def zbierz_pary():
    wiersze = []
    pliki = sorted(WYNIKI.glob("wyniki_obu/para_*/metryki.json"), key=lambda p: int(re.findall(r"\d+", p.parent.name)[0]))
    for f in pliki:
        d = json.loads(f.read_text(encoding="utf-8"))
        ks, rgb, pt = d["kontrola_skali"], d["pomiary_rgb"], d.get("piksele_termal") or {}
        wiersze.append({
            "para": int(f.parent.name[5:]), "znamie": d["info"].get("znamie"), "fold": d["info"].get("fold"),
            "model": _g(d, "rejestracja", "model"),
            "tre": _g(d, "zgodnosc", "tre", "tre_srednie"), "tre_max": _g(d, "zgodnosc", "tre", "tre_max"),
            "e1_obrys_dice": _g(d, "zgodnosc", "obrys", "dice"), "e1_otwor_dice": _g(d, "zgodnosc", "otwor", "dice"),
            "e2_folia_dice": _g(d, "zgodnosc_modalnosci", "obrys", "dice"),
            "e2_otwor_dice": _g(d, "zgodnosc_modalnosci", "otwor", "dice"),
            "e2_otwor_hd95": _g(d, "zgodnosc_modalnosci", "otwor", "hd95_mm"),
            "e2_otwor_srodki": _g(d, "zgodnosc_modalnosci", "otwor", "przesuniecie_srodkow_mm"),
            "panderm_dice": _g(d, "segmentacja_vs_cvat", "dice"), "panderm_iou": _g(d, "segmentacja_vs_cvat", "iou"),
            "panderm_hd95": _g(d, "segmentacja_vs_cvat", "hd95_mm"), "panderm_assd": _g(d, "segmentacja_vs_cvat", "assd_mm"),
            "panderm_pola": _g(d, "segmentacja_vs_cvat", "stosunek_pol"),
            "pole_mm2": rgb["pole_mm2"], "pole_cvat_mm2": _g(d, "segmentacja_vs_cvat", "pole_cvat_mm2"),
            "srednica": rgb["srednica_rownowazna_mm"], "feret_max": rgb["feret_max_mm"], "kolistosc": rgb["kolistosc"],
            "mm_px_ter": ks["mm_na_px_termal"], "pole_ter_do_rgb": ks["pole_znamienia_termal_do_rgb"],
            "piks_w_masce": pt.get("piksele_w_masce"), "piks_czesc": pt.get("piksele_czesciowe"),
            "int_med": pt.get("intensywnosc_mediana"), "int_sd": pt.get("intensywnosc_odchylenie"),
            "int_min": pt.get("intensywnosc_min"), "int_max": pt.get("intensywnosc_max"),
            "zg_rgb": _g(d, "rejestracja", "zgodnosc_rgb"), "zg_ter": _g(d, "rejestracja", "zgodnosc_termal")})
    DANE.mkdir(parents=True, exist_ok=True)
    with open(DANE / "pary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(wiersze[0]), delimiter=";")
        w.writeheader()
        w.writerows(wiersze)
    return wiersze


def kopiuj(zrodlo, nazwa):
    if zrodlo is not None and zrodlo.exists():
        shutil.copy(zrodlo, DANE / nazwa)
        with open(zrodlo, encoding="utf-8-sig") as f:
            return list(csv.DictReader(f, delimiter=";"))
    print(f"  (brak pliku dla {nazwa})")
    return []


def kol(wiersze, k):
    v = []
    for w in wiersze:
        x = w.get(k)
        try:
            v.append(float(str(x).replace(",", ".")))
        except (TypeError, ValueError):
            v.append(np.nan)
    return np.array(v)                                   # z NaN, gdy brak wartosci (opis() je pomija)


def rangi(x):
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(1, len(x) + 1)
    return r


def spearman(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(rangi(a[m]), rangi(b[m]))[0, 1])


def wilcoxon(a, b):
    """Test Wilcoxona dla par wiazanych, przyblizenie normalne (dwustronne). Zwraca (p, ile razy a < b)."""
    a, b = np.asarray(a), np.asarray(b)
    m = np.isfinite(a) & np.isfinite(b)
    a, b = a[m], b[m]
    d = a - b
    d = d[d != 0]
    n = len(d)
    r = rangi(np.abs(d))
    w = r[d > 0].sum()
    mu, sd = n * (n + 1) / 4, math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (w - mu) / sd
    return math.erfc(abs(z) / math.sqrt(2)), int((a < b).sum())


def f(x, c=2):
    return f"{x:.{c}f}".replace(".", ",")


def opis(v, c=2):
    v = v[np.isfinite(v)]
    return (f"mediana {f(np.median(v), c)} (min. {f(v.min(), c)}, maks. {f(v.max(), c)}); "
            f"średnia {f(v.mean(), c)} ± {f(v.std(ddof=1), c)}; n = {len(v)}")


def main():
    P = zbierz_pary()
    oceny = sorted((WYNIKI / "wyniki_segmentacji" / "unet_termal").glob("ocena_*/ocena.csv"))
    U = kopiuj(oceny[-1] if oceny else None, "unet_ocena.csv")
    E4 = kopiuj(WYNIKI / "wyniki_dopasowania" / "porownanie_rejestracji.csv", "porownanie_rejestracji.csv")
    pary = {w["para"] for w in P}
    E4 = [w for w in E4 if int(w["para"]) in pary]
    print(f"Dane zapisane w {DANE}\n")

    k = lambda n, c=2: opis(kol(P, n), c)
    tre = np.array([float(w["tre"]) for w in P])
    print("== 6.1 / 6.2  E1 (rejestracja względem CVAT) ==")
    print(f"  par przeanalizowanych: {len(P)} z 94")
    print(f"  TRE [mm]: {k('tre')}")
    print(f"  TRE ≤ 1 mm: {(tre <= 1).sum()}/{len(tre)} ({100 * (tre <= 1).mean():.0f}%)")
    print(f"  największe TRE: " + ", ".join(f"para {P[i]['para']} – {f(tre[i])} mm" for i in np.argsort(-tre)[:4]))
    print(f"  maks. błąd narożnika [mm]: {k('tre_max')}")
    print(f"  model: homografia {sum(w['model'] == 'homografia' for w in P)}, afiniczne {sum(w['model'] == 'afiniczna' for w in P)} (rozdz. 5.2)")
    print(f"  piksel termowizji [mm]: {k('mm_px_ter', 3)}")
    if E4:
        print("\n== 6.2  E4 (porównanie metod) ==")
        for kl, n in (("d3_tre_mm", "ECC na maskach (system)"), ("mi_otoczenie_tre_mm", "MI – otoczenie"),
                      ("mi_caly_tre_mm", "MI – cały obraz"), ("start_tre_mm", "dopasowanie wstępne")):
            v = kol(E4, kl)
            q1, q3 = np.percentile(v, [25, 75])
            print(f"  {n}: mediana {f(np.median(v))} mm (Q1–Q3 {f(q1)}–{f(q3)}), ≤ 1 mm: {(v <= 1).sum()}/{len(v)}")
        p, ile = wilcoxon(kol(E4, "d3_tre_mm"), kol(E4, "mi_otoczenie_tre_mm"))
        print(f"  Wilcoxon ECC vs MI-otoczenie: p = {p:.1e}; ECC lepsze w {ile}/{len(E4)} parach")
        for kl, n in (("czas_d3_s", "ECC"), ("czas_mi_ot_s", "MI – otoczenie"), ("czas_mi_caly_s", "MI – cały")):
            v = kol(E4, kl)
            print(f"  czas {n}: mediana {f(np.median(v), 1)} s, maks. {f(v.max(), 1)} s")
    if U:
        print("\n== 6.3  segmentacja znacznika na termowizji (M3 i detektor klasyczny) ==")
        for m in ("unet", "klasyczny"):
            for miara, c in (("dice", 3), ("iou", 3), ("hd95_mm", 2), ("assd_mm", 2), ("stosunek_pol", 3)):
                print(f"  {m} {miara}: {opis(kol(U, f'{m}_{miara}'), c)}")
        ud = kol(U, "unet_dice")
        print(f"  U-Net Dice ≥ 0,9: {(ud >= 0.9).sum()}/{len(ud)}")
        p, _ = wilcoxon(kol(U, "unet_dice"), kol(U, "klasyczny_dice"))
        print(f"  Wilcoxon U-Net vs klasyczny (Dice): p = {p:.1e}")
    print("\n== 6.3  segmentacja znamienia (M1 PanDerm) ==")
    for n, c in (("panderm_dice", 3), ("panderm_iou", 3), ("panderm_hd95", 2), ("panderm_assd", 2), ("panderm_pola", 2)):
        print(f"  {n}: {k(n, c)}")
    pdice = np.array([float(w["panderm_dice"]) for w in P])
    print(f"  Dice ≥ 0,8: {(pdice >= 0.8).sum()}/{len(P)}; najsłabsze: "
          + ", ".join(f"para {P[i]['para']} – {f(pdice[i], 2)}" for i in np.argsort(pdice)[:3]))
    print("\n== 6.4  E2 (zgodność masek między modalnościami, bez adnotacji) ==")
    e2f, e2o = kol(P, "e2_folia_dice"), kol(P, "e2_otwor_dice")
    print(f"  Dice folii: {k('e2_folia_dice', 3)}; ≥ 0,9: {(e2f >= 0.9).sum()}/{len(e2f)}")
    print(f"  Dice otworu: {k('e2_otwor_dice', 3)}")
    print(f"  HD95 otworu [mm]: {k('e2_otwor_hd95')};  przesunięcie środków otworu [mm]: {k('e2_otwor_srodki')}")
    print(f"  Spearman Dice folii (E2) – TRE (E1): ρ = {f(spearman(e2f, tre))}")
    zle = tre > 1
    print(f"  Dice otworu < 0,93: {(e2o < 0.93).sum()} par, z nich TRE > 1 mm: {((e2o < 0.93) & zle).sum()} (wszystkich z TRE > 1 mm: {zle.sum()})")
    print("\n== 6.5  znamiona i piksele ==")
    for n, c in (("pole_mm2", 2), ("pole_cvat_mm2", 2), ("srednica", 2), ("feret_max", 2), ("kolistosc", 3),
                 ("pole_ter_do_rgb", 3), ("piks_w_masce", 0), ("piks_czesc", 0), ("int_sd", 1)):
        print(f"  {n}: {k(n, c)}")
    rozst = kol(P, "int_max") - kol(P, "int_min")
    print(f"  rozstęp intensywności: {opis(rozst, 0)}")
    print(f"  pikseli w maskach łącznie: {int(np.nansum(kol(P, 'piks_w_masce')))}")
    print("\nPorównaj z liczbami w rozdz. 5–7, Streszczeniu i Abstract (wzor/*.tex); następnie uruchom wykresy_wyniki.py.")


if __name__ == "__main__":
    main()
