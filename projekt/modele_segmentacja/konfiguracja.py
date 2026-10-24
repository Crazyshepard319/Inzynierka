"""
Sciezki uzywane przez modele segmentacji.

Ciezkie pliki (srodowisko Pythona, wagi, zbiory danych) leza POZA OneDrive,
w katalogu KATALOG_DANYCH. Mozna go zmienic zmienna srodowiskowa MODELE_DANE.
"""
import os
from pathlib import Path

KATALOG_DANYCH = Path(os.environ.get("MODELE_DANE", Path.home() / "modele_dane"))
PYTHON_MODELI = KATALOG_DANYCH / "srodowisko" / "Scripts" / "python.exe"   # Python 3.12 + PyTorch
WAGI = KATALOG_DANYCH / "wagi"            # wagi modeli: wagi/<klucz_modelu>/...
DANE = KATALOG_DANYCH / "dane"            # zbiory treningowe, np. dane/ISIC2018

KATALOG_MODULU = Path(__file__).resolve().parent
REPOZYTORIA = KATALOG_MODULU / "repozytoria"   # sklonowane repozytoria autorow
KATALOG_GLOWNY = KATALOG_MODULU.parent.parent  # folder Inzynierka (projekt/modele_segmentacja -> Inzynierka)
WYNIKI = KATALOG_GLOWNY / "wyniki" / "wyniki_segmentacji"   # wyniki z aplikacji testowej i treningu
