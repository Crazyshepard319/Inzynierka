"""
Segmentacja znamienia na jednym zdjeciu modelem z modele/ (domyslnie PanDerm, model M1).
Aplikacja (aplikacja.py, krok 3) uruchamia ten skrypt w srodowisku modeli (Python z PyTorch),
bo srodowisko aplikacji nie ma PyTorch:

    python -m modele_segmentacja.segmentuj_znamie zdjecie.jpg maska.png
           [--maska-znacznika dopasowanie_maska_rgb.png] [--model panderm_upernet]

Obszar szukania = wnetrze znacznika Π: z maski znacznika z rejestracji (dopasowanie3, skala robocza)
albo, gdy jej nie ma lub nie daje wnetrza, z detekcji znacznik.wykryj_znacznik.
Wynik: maska uint8 0/255 w rozmiarze zdjecia. Kod wyjscia 0 = sukces.
"""
import argparse
import sys
import time

import cv2

from . import wczytaj_model
from .interfejs import wczytaj_obraz, zapisz_obraz
from .znacznik import BrakZnacznika, segmentuj_w_znaczniku, wykryj_znacznik, znacznik_z_maski


def main():
    ap = argparse.ArgumentParser(description="Segmentacja znamienia we wnetrzu znacznika")
    ap.add_argument("zdjecie")
    ap.add_argument("wyjscie", help="maska PNG (0/255)")
    ap.add_argument("--maska-znacznika", help="maska folii z rejestracji (dowolna skala)")
    ap.add_argument("--model", default="panderm_upernet")
    a = ap.parse_args()

    obraz = wczytaj_obraz(a.zdjecie)
    if obraz is None:
        sys.exit(f"Nie mozna otworzyc zdjecia: {a.zdjecie}")
    z = None
    if a.maska_znacznika:
        m = wczytaj_obraz(a.maska_znacznika, cv2.IMREAD_GRAYSCALE)
        if m is None:
            print(f"Brak maski znacznika {a.maska_znacznika} - szukam znacznika na zdjeciu")
        else:
            try:
                z = znacznik_z_maski(m, obraz.shape[:2], m.shape[1] / obraz.shape[1], opis="maska z rejestracji")
            except BrakZnacznika as e:
                print(f"Maska znacznika z rejestracji nie daje wnetrza ({e}) - szukam znacznika na zdjeciu")
    if z is None:
        try:
            z = wykryj_znacznik(obraz)
        except BrakZnacznika as e:
            sys.exit(f"Nie znaleziono znacznika: {e}")
    print(f"Obszar szukania: wnetrze znacznika ({z.opis}), prostokat {z.roi}", flush=True)

    t0 = time.perf_counter()
    model = wczytaj_model(a.model)
    print(f"Model {model.nazwa} wczytany w {time.perf_counter() - t0:.1f} s", flush=True)
    wynik = segmentuj_w_znaczniku(model, obraz, z)
    if not wynik.maska.any():
        sys.exit("Model nie znalazl znamienia we wnetrzu znacznika")
    if not zapisz_obraz(a.wyjscie, wynik.maska):
        sys.exit(f"Nie udalo sie zapisac maski: {a.wyjscie}")
    print(f"Segmentacja {wynik.czas_s:.1f} s, maska {int((wynik.maska > 0).sum())} px -> {a.wyjscie}")


if __name__ == "__main__":
    main()
