"""
Modele segmentacji znamion ze wspolnym interfejsem.

    from modele_segmentacja import dostepne_modele, wczytaj_model
    model = wczytaj_model("panderm_upernet")
    wynik = model.segmentuj(obraz_bgr, roi=(x, y, w, h))   # -> WynikSegmentacji

Nowy model = nowy folder w modele/ z plikiem __init__.py, w ktorym jest
klasa Model(ModelSegmentacji) - zostanie wykryty automatycznie.
"""
import importlib
import pkgutil

from . import modele as _modele
from .interfejs import (ModelSegmentacji, WynikSegmentacji, maska_w_termalu,
                        metryki, najwieksza_skladowa)


class _BladImportu(ModelSegmentacji):
    def __init__(self, klucz, blad):
        super().__init__()
        self.klucz = self.nazwa = klucz
        self._blad = blad

    def dostepnosc(self):
        return False, f"blad importu: {self._blad}"


def dostepne_modele():
    """Wszystkie modele z folderu modele/ (bez wczytywania wag)."""
    lista = []
    for m in sorted(pkgutil.iter_modules(_modele.__path__), key=lambda m: m.name):
        if not m.ispkg:
            continue
        try:
            lista.append(importlib.import_module(f"{_modele.__name__}.{m.name}").Model())
        except Exception as e:
            lista.append(_BladImportu(m.name, e))
    return lista


def wczytaj_model(klucz):
    """Model o danym kluczu (nazwie folderu), z wczytanymi wagami."""
    for m in dostepne_modele():
        if m.klucz == klucz:
            return m.wczytaj()
    raise KeyError(f"Nie ma modelu '{klucz}'")
