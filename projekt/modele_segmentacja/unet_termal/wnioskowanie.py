"""
Wnioskowanie U-Netu (model M3) przez cv2.dnn z pliku ONNX - bez PyTorch, wiec dziala w aplikacji.

    from modele_segmentacja.unet_termal import wczytaj
    model, opis = wczytaj(fold=3)        # para z foldu 3: model, ktory jej nie widzial w treningu
    maska = model.segmentuj(obraz_termal_bgr)        # uint8 0/255, rozmiar obrazu

Pliki modeli: <modele_dane>/wagi/unet_termal/fold1..5.onnx i wszystkie.onnx (trening.py).
"""
import threading
from pathlib import Path

import cv2
import numpy as np

from ..konfiguracja import WAGI
from .przetwarzanie import PROG, maska_z_prawdopodobienstwa, wejscie_sieci

KATALOG_WAG = WAGI / "unet_termal"
_pamiec, _blokada = {}, threading.Lock()


class SegmentacjaZnacznikaTermal:
    """Jeden model ONNX: obraz termowizyjny -> prawdopodobienstwo / maska znacznika."""

    def __init__(self, sciezka):
        self.sciezka = Path(sciezka)
        self.net = cv2.dnn.readNetFromONNX(np.fromfile(str(self.sciezka), np.uint8))   # polskie znaki w sciezce
        self._blokada = threading.Lock()

    def prawdopodobienstwo(self, obraz):
        """(240, 320) float32 0..1 w siatce wejscia sieci."""
        with self._blokada:
            self.net.setInput(wejscie_sieci(obraz))
            return self.net.forward()[0, 0].astype(np.float32)

    def segmentuj(self, obraz, prog=PROG):
        """Maska znacznika uint8 0/255 w rozmiarze obrazu (najwieksza skladowa, bez malych dziur)."""
        return maska_z_prawdopodobienstwa(self.prawdopodobienstwo(obraz), np.asarray(obraz).shape, prog)


def plik_modelu(fold=None, katalog=None):
    kat = Path(katalog) if katalog else KATALOG_WAG
    return kat / (f"fold{int(fold)}.onnx" if fold not in (None, "") else "wszystkie.onnx")


def wczytaj(fold=None, katalog=None):
    """(model, opis). fold = fold pary z bazy (dane/znamiona.csv): model, dla ktorego para byla testowa;
    None albo brak pliku foldu: model uczony na wszystkich parach."""
    kandydaci = ([(plik_modelu(fold, katalog), f"U-Net M3, model foldu {int(fold)} (para nie była w treningu)")]
                 if fold not in (None, "") else [])
    kandydaci.append((plik_modelu(None, katalog), "U-Net M3, model uczony na wszystkich parach"))
    for sciezka, opis in kandydaci:
        if sciezka.exists():
            with _blokada:
                if sciezka not in _pamiec:
                    _pamiec[sciezka] = SegmentacjaZnacznikaTermal(sciezka)
            return _pamiec[sciezka], opis
    raise FileNotFoundError(f"Brak modelu U-Net dla termowizji: {kandydaci[-1][0]}\n"
                            "Trening: projekt/modele_segmentacja/trenuj_unet_termal.bat")


def dostepny(katalog=None):
    return plik_modelu(None, katalog).exists()
