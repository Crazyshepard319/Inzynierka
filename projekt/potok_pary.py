"""
Potok analizy jednej pary RGB - termowizja z bazy (dane/pary/N/), na wzorcu z CVAT.

    python potok_pary.py 1                       # para 1, model rejestracji 'auto'
    python potok_pary.py 1 --model afiniczna
    python potok_pary.py 1 --narozniki auto      # skala z naroznikow wykrytych automatycznie

Etapy (analiza/system.py, te same co w aplikacji):
  1. wejscie: zdjecie, termowizja, adnotacje z CVAT (maski i narozniki znacznika, maska znamienia)
  2. rejestracja dopasowanie3.run_registration -> macierz T (piksel RGB -> piksel termowizji);
     znacznik wykrywany automatycznie metoda klasyczna, adnotacje z CVAT NIE sa uzywane
  3. segmentacja: narozniki znacznika (CVAT albo automatycznie) -> skala w mm; znamie z CVAT
  4. przeniesienie przez T: obrys znamienia, obrys i otwor znacznika, 8 naroznikow (RGB -> termowizja)
  5. pomiary: wymiary w mm i kolor znamienia, kontrola skali (otwor 240 mm2);
     zgodnosc z wzorcem z CVAT (badanie E1): TRE naroznikow, Dice/IoU/HD95/ASSD obrysu i otworu
  6. raport: wyniki/wyniki_obu/para_N/raport.html + metryki.json + obrazy PNG
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analiza.system import MODELE_REJESTRACJI, analizuj_pare   # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Potok analizy jednej pary RGB - termowizja")
    ap.add_argument("para", type=int)
    ap.add_argument("--model", default="auto", choices=MODELE_REJESTRACJI)
    ap.add_argument("--narozniki", default="cvat", choices=["cvat", "auto"])
    a = ap.parse_args()
    an = analizuj_pare(a.para, a.model, a.narozniki)
    sciezka = an.zapisz_raport()
    w = an.wyniki
    zg, rgb, ks = w["zgodnosc"], w["pomiary_rgb"], w["kontrola_skali"]
    print(f"Para {a.para}: model {w['rejestracja'].get('model')}, TRE {zg['tre']['tre_srednie']:.2f} mm "
          f"(max {zg['tre']['tre_max']:.2f}), Dice obrysu {zg['obrys']['dice']:.3f}, otworu {zg['otwor']['dice']:.3f}")
    print(f"  znamie: {rgb['pole_mm2']:.2f} mm2, srednica {rgb['srednica_rownowazna_mm']:.2f} mm, "
          f"na termowizji {ks['piksele_znamienia_termal']:.1f} px; pole otworu przeniesiony/termowizja {ks['stosunek_pol_otworu']:.3f}")
    print(f"  raport: {sciezka}")


if __name__ == "__main__":
    main()
