"""
Ocena segmentacji znacznika na termowizji wzgledem adnotacji z CVAT (wymaga tylko numpy i OpenCV).

    ocen_unet_termal.bat                 (albo: python -m modele_segmentacja.unet_termal.ocena [--pary 1-94])

Porownywane metody (ta sama maska wzorcowa: dane/pary/N/maska_znacznik_termal.png):
  unet        U-Net M3, model foldu pary (para byla w nim testowa - wynik walidacji krzyzowej),
  klasyczny   detektor z rejestracji (dopasowanie3.wykryj_znacznik_termal; maska z
              wyniki/wyniki_dopasowania/para_N/dopasowanie_maska_termal.png, a gdy jej nie ma - liczona).
Miary: Dice, IoU, HD95 i ASSD [mm], stosunek pol (metoda / CVAT); mm/px z homografii narozników CVAT.
Wynik: wyniki/wyniki_segmentacji/unet_termal/ocena_<data>/ocena.csv, podsumowanie.txt, tabela.tex
"""
import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

PROJEKT = Path(__file__).resolve().parents[2]
if str(PROJEKT) not in sys.path:
    sys.path.insert(0, str(PROJEKT))

from analiza import geometria as geo, miary                     # noqa: E402
from analiza.dane import INZ, PARY, imread                       # noqa: E402
from modele_segmentacja.konfiguracja import WYNIKI               # noqa: E402
from modele_segmentacja.unet_termal import wczytaj               # noqa: E402

METODY = ("unet", "klasyczny")
MIARY = (("dice", "Dice", 3), ("iou", "IoU", 3), ("hd95_mm", "HD95 [mm]", 2), ("assd_mm", "ASSD [mm]", 2),
         ("stosunek_pol", "Stosunek pól (metoda / CVAT)", 3))


def numery(teksty):
    wynik = []
    for t in teksty:
        od, _, do = t.partition("-")
        wynik += range(int(od), int(do or od) + 1)
    return wynik


def foldy():
    with open(INZ / "dane" / "znamiona.csv", encoding="utf-8-sig") as f:
        return {int(r["para"]): int(r["fold"]) for r in csv.DictReader(f, delimiter=";")}


def maska_klasyczna(n, sciezka_termal):
    p = INZ / "wyniki" / "wyniki_dopasowania" / f"para_{n}" / "dopasowanie_maska_termal.png"
    m = imread(p, cv2.IMREAD_GRAYSCALE)
    if m is not None:
        return m, "z rejestracji"
    import dopasowanie3 as dop
    return dop.wykryj_znacznik_termal(sciezka_termal)["maska"], "policzona"


def _l(x, m):
    return "–" if x is None or not np.isfinite(x) else f"{x:.{m}f}".replace(".", ",")


def main():
    ap = argparse.ArgumentParser(description="Ocena segmentacji znacznika na termowizji (U-Net M3 i detektor klasyczny)")
    ap.add_argument("--pary", nargs="*", default=None, help="np. 1-94 (domyslnie wszystkie z adnotacjami)")
    ap.add_argument("--wagi", default=None, help="katalog modeli ONNX (domyslnie modele_dane/wagi/unet_termal)")
    ap.add_argument("--wyjscie", default=None)
    a = ap.parse_args()
    fold = foldy()
    lista = numery(a.pary) if a.pary else sorted(int(k.name) for k in PARY.iterdir() if k.name.isdigit())
    kat = Path(a.wyjscie) if a.wyjscie else WYNIKI / "unet_termal" / f"ocena_{datetime.now():%Y%m%d_%H%M%S}"
    kat.mkdir(parents=True, exist_ok=True)
    wiersze = []
    for n in lista:
        k = PARY / str(n)
        wz = imread(k / "maska_znacznik_termal.png", cv2.IMREAD_GRAYSCALE)
        if wz is None or not (k / "narozniki.json").exists():
            continue
        nar = json.loads((k / "narozniki.json").read_text(encoding="utf-8"))["termowizja"]
        s = geo.mm_na_px(nar["homografia_px_na_mm"], np.mean(nar["punkty_px"], axis=0))
        termal = imread(k / "termal.jpg", cv2.IMREAD_UNCHANGED)
        model, opis = wczytaj(fold.get(n), a.wagi)
        maski = {"unet": model.segmentuj(termal)}
        maski["klasyczny"], zrodlo = maska_klasyczna(n, k / "termal.jpg")
        w = {"para": n, "fold": fold.get(n, ""), "model_unet": Path(model.sciezka).name, "maska_klasyczna": zrodlo,
             "mm_na_px": round(s, 4)}
        for met in METODY:
            z = miary.zgodnosc_masek(maski[met] > 0, wz > 0, s)
            for klucz, _, _ in MIARY:
                w[f"{met}_{klucz}"] = z.get(klucz, float("nan"))
        wiersze.append(w)
        print(f"para {n:3d} (fold {w['fold']}): U-Net Dice {w['unet_dice']:.3f}, HD95 {w['unet_hd95_mm']:.2f} mm | "
              f"klasyczny Dice {w['klasyczny_dice']:.3f}, HD95 {w['klasyczny_hd95_mm']:.2f} mm", flush=True)
    if not wiersze:
        raise SystemExit("Brak par z maska_znacznik_termal.png i narozniki.json")
    with open(kat / "ocena.csv", "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, list(wiersze[0]), delimiter=";")
        wr.writeheader()
        for w in wiersze:
            wr.writerow({k: (_l(v, 4) if isinstance(v, float) else v) for k, v in w.items()})
    linie = [f"Ocena segmentacji znacznika na termowizji wzgledem CVAT ({len(wiersze)} par, {datetime.now():%d.%m.%Y %H:%M})",
             "U-Net: model foldu pary (walidacja krzyzowa po znamionach); klasyczny: detektor z rejestracji.", ""]
    tex = ["% Tabela z modele_segmentacja/unet_termal/ocena.py; wymaga \\usepackage{booktabs}.",
           "\\begin{table}[htbp]", "\\centering",
           f"\\caption{{Segmentacja znacznika na obrazie termowizyjnym względem adnotacji z CVAT ($n = {len(wiersze)}$ par): "
           "U-Net (walidacja krzyżowa po znamionach) i detektor klasyczny z rejestracji}",
           "\\label{tab:znacznik-termal}", "\\begin{tabular}{lrrrr}", "\\toprule",
           "Miara & \\multicolumn{2}{c}{U-Net} & \\multicolumn{2}{c}{Detektor klasyczny} \\\\",
           " & średnia $\\pm$ odch. & mediana & średnia $\\pm$ odch. & mediana \\\\", "\\midrule"]
    for klucz, nazwa, m in MIARY:
        komorki, opis_l = [], [f"{nazwa:28s}"]
        for met in METODY:
            v = np.array([w[f"{met}_{klucz}"] for w in wiersze], float)
            v = v[np.isfinite(v)]
            sr, sd, me = (v.mean(), v.std(ddof=1) if len(v) > 1 else 0.0, np.median(v)) if len(v) else (np.nan,) * 3
            komorki += [f"{_l(sr, m)} $\\pm$ {_l(sd, m)}", _l(me, m)]
            opis_l.append(f"{met}: {_l(sr, m)} ± {_l(sd, m)} (mediana {_l(me, m)}, min {_l(v.min() if len(v) else np.nan, m)}, "
                          f"maks {_l(v.max() if len(v) else np.nan, m)})")
        linie.append("  ".join(opis_l))
        tex.append(f"{nazwa} & " + " & ".join(komorki) + " \\\\")
    for met in METODY:
        d = np.array([w[f"{met}_dice"] for w in wiersze], float)
        linie.append(f"{met}: Dice >= 0,9 na {int((d >= 0.9).sum())}/{len(d)} parach, < 0,8 na {int((d < 0.8).sum())}")
    tex += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    (kat / "podsumowanie.txt").write_text("\n".join(linie) + "\n", encoding="utf-8")
    (kat / "tabela.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")
    print("\n" + "\n".join(linie) + f"\n-> {kat}")


if __name__ == "__main__":
    main()
