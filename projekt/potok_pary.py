"""
Potok analizy par RGB - termowizja z bazy (dane/pary/N/) - te same etapy co w aplikacji.
Wymaga PyTorch (PanDerm), wiec uruchamiamy go Pythonem srodowiska modeli, np. przez potok_pary.bat:

    potok_pary.bat 1            # para 1
    potok_pary.bat 1 3 10-20    # kilka par i zakres
    potok_pary.bat 1-94 --z_zapisanych   # zapisana rejestracja i maska PanDerm (bez GPU) - np. po zmianach w kodzie

Etapy (analiza/system.py):
  1. wejscie: zdjecie, termowizja; adnotacje z CVAT tylko do oceny
  2. rejestracja dopasowanie3.run_registration -> macierz T (piksel RGB -> piksel termowizji);
     znacznik wykrywany automatycznie, model przeksztalcenia z dopasowanie3.MODEL
  3. segmentacja: narozniki znacznika automatycznie (wzorzec Π dopasowany do maski z rejestracji)
     -> skala w mm; znamie modelem PanDerm we wnetrzu znacznika; znacznik na termowizji U-Netem (M3)
  4. przeniesienie przez T: obrys znamienia, obrys i otwor znacznika, 8 naroznikow (RGB -> termowizja)
  5. pomiary: wymiary w mm i kolor znamienia, kontrola skali; zgodnosc masek znacznika miedzy
     modalnosciami (badanie E2); ocena wzgledem CVAT (badanie E1, segmentacja PanDerm i U-Netu vs adnotacja)
  6. raport: wyniki/wyniki_obu/para_N/raport.html + metryki.json + obrazy PNG; wpis w bazie dane/baza.sqlite
Gdy para sie nie uda, powod trafia do wyniki/wyniki_obu/para_N/blad.txt (czyta go raport_zbiorczy.py)
i do bazy (analiza ze statusem 'blad').
"""
import argparse
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analiza.dane import INZ                                # noqa: E402
from analiza.system import Analiza, BladEtapu, analizuj, analizuj_z_zapisanych   # noqa: E402


def numery(argumenty):
    wynik = []
    for a in argumenty:
        if "-" in a:
            od, do = map(int, a.split("-"))
            wynik += range(od, do + 1)
        else:
            wynik.append(int(a))
    return wynik


class _Log:
    def write(self, t):
        print(t, end="", flush=True)

    def flush(self):
        pass


def _zapisz_blad(plik, tekst, an=None, n=None):
    plik.parent.mkdir(parents=True, exist_ok=True)
    plik.write_text(tekst, encoding="utf-8")
    if an is not None:
        an.zapisz_w_bazie(status="blad", blad=tekst)
        return
    try:
        from analiza import baza
        with baza.Baza() as b:
            b.zapisz_blad(n, tekst)
    except Exception as e:                                   # noqa: BLE001
        print(f"[baza] nie zapisano bledu: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Potok analizy par RGB - termowizja")
    ap.add_argument("pary", nargs="+", help="numery par, np. 1 3 10-20")
    ap.add_argument("--z_zapisanych", action="store_true",
                    help="zapisana rejestracja i maska PanDerm zamiast liczenia od nowa (bez PyTorch)")
    a = ap.parse_args()
    etapy = analizuj_z_zapisanych if a.z_zapisanych else analizuj
    for n in numery(a.pary):
        print(f"\n=== Para {n} ===")
        blad = INZ / "wyniki" / "wyniki_obu" / f"para_{n}" / "blad.txt"     # powod dla raport_zbiorczy.py
        an = None
        try:
            an = Analiza.z_pary(n)
            etapy(an, log=_Log())
            sciezka = an.zapisz_raport()
        except BladEtapu as e:
            print(f"Para {n}: BLAD - {e}")
            _zapisz_blad(blad, str(e), an, n)
            continue
        except Exception as e:
            traceback.print_exc()
            _zapisz_blad(blad, f"{type(e).__name__}: {e}", an, n)
            continue
        blad.unlink(missing_ok=True)
        w = an.wyniki
        zg, rgb, ks, seg = w["zgodnosc"], w["pomiary_rgb"], w["kontrola_skali"], w["segmentacja_vs_cvat"]
        print(f"Para {n}: model {w['rejestracja'].get('model')}; znamie {rgb['pole_mm2']:.2f} mm2, "
              f"srednica {rgb['srednica_rownowazna_mm']:.2f} mm; pole otworu przeniesiony/termowizja "
              f"{ks['stosunek_pol_otworu']:.3f}")
        e2 = w.get("zgodnosc_modalnosci")
        if e2:
            print(f"  E2 (zdjecie -> T vs U-Net): Dice folii {e2['obrys']['dice']:.3f}, "
                  f"Dice otworu {e2['otwor']['dice']:.3f}, HD95 otworu {e2['otwor'].get('hd95_mm', float('nan')):.2f} mm")
        if zg:
            print(f"  wzgledem CVAT: TRE {zg['tre']['tre_srednie']:.2f} mm (max {zg['tre']['tre_max']:.2f}), "
                  f"Dice obrysu {zg['obrys']['dice']:.3f}; PanDerm Dice {seg['dice']:.3f}, "
                  f"pole PanDerm/CVAT {seg['stosunek_pol']:.2f}")
        print(f"  raport: {sciezka}")


if __name__ == "__main__":
    main()
