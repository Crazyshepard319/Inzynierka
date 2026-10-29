"""
Model M3: U-Net segmentujacy znacznik Π (folie) na obrazie termowizyjnym.

Znamienia na termowizji nie widac, wiec modelem dedykowanym tej modalnosci jest segmentacja znacznika.
Model nie bierze udzialu w rejestracji (T liczy dopasowanie3.py z detektora klasycznego), dlatego
porownanie jego maski z maska znacznika przeniesiona ze zdjecia przez T jest niezalezna weryfikacja
zgodnosci obszaru miedzy modalnosciami (badanie E2, analiza/system.py).

    przetwarzanie.py   wejscie sieci i maska z prawdopodobienstwa (numpy + OpenCV)
    architektura.py    U-Net (PyTorch)
    dane.py            zbior z dane/pary + znamiona.csv, augmentacja
    trening.py         walidacja krzyzowa po znamionach, eksport ONNX
    wnioskowanie.py    cv2.dnn + ONNX (bez PyTorch) - uzywa aplikacja i potok
    ocena.py           ocena na parach z CVAT: U-Net (modele foldow) i detektor klasyczny
"""
from .wnioskowanie import SegmentacjaZnacznikaTermal, dostepny, plik_modelu, wczytaj

__all__ = ["SegmentacjaZnacznikaTermal", "dostepny", "plik_modelu", "wczytaj"]
