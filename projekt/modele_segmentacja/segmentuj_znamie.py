"""
Segmentacja znamienia na jednym zdjeciu modelem z modele/ (domyslnie PanDerm, model M1).

Z kodu (srodowisko z PyTorch, np. potok_pary.py uruchomiony Pythonem srodowiska modeli):
    from modele_segmentacja.segmentuj_znamie import segmentuj
    maska = segmentuj(obraz_bgr, maska_znacznika)          # uint8 0/255, rozmiar zdjecia

Z wiersza polecen (tak wywoluje go aplikacja, ktorej srodowisko nie ma PyTorch):
    python -m modele_segmentacja.segmentuj_znamie zdjecie.jpg maska.png
           [--maska-znacznika dopasowanie_maska_rgb.png] [--model panderm_upernet]

Obszar szukania = wnetrze znacznika Π: z maski znacznika z rejestracji (dopasowanie3, dowolna skala)
albo, gdy jej nie ma lub nie daje wnetrza, z detekcji znacznik.wykryj_znacznik.
We wnetrzu propozycje.py wskazuje kandydatow (ciemne plamy), model segmentuje kazdego w kadrze jak w ISIC
i zostaje wynik o najwiekszym kontrascie brzegu (znacznik.segmentuj_w_znaczniku).
"""
import argparse
import sys
import time

import cv2

from . import wczytaj_model
from .interfejs import wczytaj_obraz, zapisz_obraz
from .znacznik import BrakZnacznika, segmentuj_w_znaczniku, wykryj_znacznik, znacznik_z_maski

MODEL = "panderm_upernet"
_wczytane = {}                     # model wczytany raz na proces (potok wielu par)


class BladSegmentacji(RuntimeError):
    pass


def segmentuj(obraz, maska_znacznika=None, model=MODEL, log=print):
    """Maska znamienia (uint8 0/255, rozmiar obrazu) we wnetrzu znacznika."""
    z = None
    if maska_znacznika is not None:
        try:
            z = znacznik_z_maski(maska_znacznika, obraz.shape[:2], maska_znacznika.shape[1] / obraz.shape[1],
                                 opis="maska z rejestracji")
        except BrakZnacznika as e:
            log(f"Maska znacznika z rejestracji nie daje wnetrza ({e}) - szukam znacznika na zdjeciu")
    if z is None:
        try:
            z = wykryj_znacznik(obraz)
        except BrakZnacznika as e:
            raise BladSegmentacji(f"Nie znaleziono znacznika: {e}") from None
    log(f"Obszar szukania: wnetrze znacznika ({z.opis}), prostokat {z.roi}")
    if model not in _wczytane:
        t0 = time.perf_counter()
        _wczytane[model] = wczytaj_model(model)
        log(f"Model {_wczytane[model].nazwa} wczytany w {time.perf_counter() - t0:.1f} s")
    wynik = segmentuj_w_znaczniku(_wczytane[model], obraz, z)
    if not wynik.maska.any():
        raise BladSegmentacji("Model nie znalazl znamienia we wnetrzu znacznika")
    log(f"Segmentacja {wynik.czas_s:.1f} s ({wynik.info.get('metoda', '')}), maska {int((wynik.maska > 0).sum())} px")
    return wynik.maska


def main():
    ap = argparse.ArgumentParser(description="Segmentacja znamienia we wnetrzu znacznika")
    ap.add_argument("zdjecie")
    ap.add_argument("wyjscie", help="maska PNG (0/255)")
    ap.add_argument("--maska-znacznika", help="maska folii z rejestracji (dowolna skala)")
    ap.add_argument("--model", default=MODEL)
    a = ap.parse_args()
    obraz = wczytaj_obraz(a.zdjecie)
    if obraz is None:
        sys.exit(f"Nie mozna otworzyc zdjecia: {a.zdjecie}")
    mz = wczytaj_obraz(a.maska_znacznika, cv2.IMREAD_GRAYSCALE) if a.maska_znacznika else None
    try:
        maska = segmentuj(obraz, mz, a.model, log=lambda t: print(t, flush=True))
    except BladSegmentacji as e:
        sys.exit(str(e))
    if not zapisz_obraz(a.wyjscie, maska):
        sys.exit(f"Nie udalo sie zapisac maski: {a.wyjscie}")
    print(f"-> {a.wyjscie}")


if __name__ == "__main__":
    main()
