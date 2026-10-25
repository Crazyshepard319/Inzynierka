"""
Ocena segmentacji znamienia na wszystkich parach z adnotacjami CVAT (dane/pary/N/maska_znamie_rgb.png).

Dwie metody, ten sam model i ten sam obszar (wnetrze znacznika z rejestracji):
    kandydaci     - jak w aplikacji: propozycje.py wskazuje kandydatow na znamie, model segmentuje kazdego
                    w kadrze jak w ISIC, zostaje wynik o najwiekszym kontrascie brzegu
    cale_wnetrze  - dawny sposob: kadr = cale wnetrze znacznika + automatyczne przyblizenie

Uruchomienie (GPU, srodowisko modeli): ocen_segmentacje.bat  [--metody kandydaci] [--pary 1 2 3]
albo z folderu projekt:  <modele_dane>\\srodowisko\\Scripts\\python.exe -m modele_segmentacja.ocen_segmentacje

Wynik: wyniki/wyniki_segmentacji/ocena_<model>_<data>/ocena.csv (Dice, IoU, precyzja, czulosc,
stosunek pol, czas) i maski <metoda>/<para>.png; na koncu podsumowanie dla kazdej metody.
"""
import argparse
import csv
import time
from datetime import datetime

import numpy as np

from . import metryki, wczytaj_model
from .interfejs import wczytaj_obraz, zapisz_obraz
from .konfiguracja import KATALOG_GLOWNY, WYNIKI
from .znacznik import BrakZnacznika, segmentuj_w_znaczniku, wykryj_znacznik, znacznik_z_maski

PARY = KATALOG_GLOWNY / "dane" / "pary"
REJESTRACJA = KATALOG_GLOWNY / "wyniki" / "wyniki_dopasowania"
METODY = ("kandydaci", "cale_wnetrze")


def znacznik_pary(n, obraz):
    mz = wczytaj_obraz(REJESTRACJA / f"para_{n}" / "dopasowanie_maska_rgb.png", 0)
    if mz is not None:
        try:
            return znacznik_z_maski(mz, obraz.shape[:2], mz.shape[1] / obraz.shape[1], opis="maska z rejestracji")
        except BrakZnacznika:
            pass
    return wykryj_znacznik(obraz)


def main():
    ap = argparse.ArgumentParser(description="Dice segmentacji znamienia wzgledem adnotacji CVAT")
    ap.add_argument("--model", default="panderm_upernet")
    ap.add_argument("--metody", nargs="+", default=list(METODY), choices=METODY)
    ap.add_argument("--pary", nargs="*", type=int, help="numery par (domyslnie wszystkie z adnotacja)")
    a = ap.parse_args()

    pary = a.pary or sorted(int(k.name) for k in PARY.iterdir()
                            if k.name.isdigit() and (k / "maska_znamie_rgb.png").exists())
    model = wczytaj_model(a.model)
    t0 = time.perf_counter()
    model.wczytaj()
    print(f"Model {model.nazwa} wczytany w {time.perf_counter() - t0:.1f} s "
          f"({getattr(model, 'urzadzenie', '')}); par: {len(pary)}", flush=True)
    wyj = WYNIKI / f"ocena_{a.model}_{datetime.now():%Y%m%d_%H%M%S}"
    for m in a.metody:
        (wyj / m).mkdir(parents=True, exist_ok=True)

    wiersze = []
    for i, n in enumerate(pary, 1):
        obraz = wczytaj_obraz(PARY / str(n) / "rgb.jpg")
        wzor = wczytaj_obraz(PARY / str(n) / "maska_znamie_rgb.png", 0)
        try:
            z = znacznik_pary(n, obraz)
        except BrakZnacznika as e:
            print(f"[{i}/{len(pary)}] para {n}: brak znacznika ({e})", flush=True)
            for m in a.metody:
                wiersze.append(dict(para=n, metoda=m, dice=0.0, iou=0.0, precyzja=0.0, czulosc=0.0,
                                    stosunek_pol="", czas_s="", uwagi="brak znacznika"))
            continue
        opis = []
        for m in a.metody:
            wynik = segmentuj_w_znaczniku(model, obraz, z, ile_propozycji=None if m == "cale_wnetrze" else 3)
            mt = metryki(wynik.maska, wzor)
            zapisz_obraz(wyj / m / f"{n}.png", wynik.maska)
            wiersze.append(dict(para=n, metoda=m, **{k: round(v, 4) for k, v in mt.items()},
                                stosunek_pol=round(np.count_nonzero(wynik.maska) / max(1, np.count_nonzero(wzor)), 2),
                                czas_s=round(wynik.czas_s, 2), uwagi=wynik.info.get("metoda", "")))
            opis.append(f"{m} Dice {mt['dice']:.2f}")
        print(f"[{i}/{len(pary)}] para {n}: " + ", ".join(opis), flush=True)

    with open(wyj / "ocena.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(wiersze[0]), delimiter=";")
        w.writeheader()
        w.writerows(wiersze)
    print(f"\nWyniki: {wyj / 'ocena.csv'}")
    for m in a.metody:
        d = np.array([r["dice"] for r in wiersze if r["metoda"] == m])
        print(f"  {m:13s} Dice: srednia {d.mean():.3f}, mediana {np.median(d):.3f}, "
              f"< 0,5 na {int((d < 0.5).sum())}/{len(d)} parach")


if __name__ == "__main__":
    main()
