"""
Porownanie metod rejestracji na parach z adnotacjami z CVAT (badanie E4 z planu pracy).

    "%USERPROFILE%\\modele_dane\\srodowisko\\Scripts\\python.exe" projekt\\porownaj_rejestracje.py 1-94

Metody (ten sam start - znacznik Π wykryty jak w dopasowanie3.py):
  d3        dopasowanie3.py: ECC na maskach znacznika (afiniczne / homografia)
  mi_ot     dopasowanie2_pi.py: SimpleITK, informacja wzajemna Mattesa w otoczeniu znacznika
  mi_caly   dopasowanie2_pi.py: SimpleITK, informacja wzajemna na calym obrazie (jak archiwum/dopasowanie2.py)
  start     sam start z dopasowania ksztaltow (podobienstwo), bez optymalizacji
Miara: TRE - srednia i maksymalna odleglosc 8 naroznikow z CVAT przeniesionych przez T od naroznikow
z CVAT na termowizji, w mm. Wynik: wyniki/wyniki_dopasowania/porownanie_rejestracji.csv
"""
import contextlib
import io
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dopasowanie2_pi as d2                            # noqa: E402
from analiza import geometria as geo, miary            # noqa: E402
from analiza.dane import INZ                           # noqa: E402
from analiza.system import Analiza                     # noqa: E402

NAGLOWEK = ("para;d3_tre_mm;d3_max_mm;d3_model;mi_otoczenie_tre_mm;mi_otoczenie_max_mm;mi_caly_tre_mm;"
            "mi_caly_max_mm;start_tre_mm;czas_d3_s;czas_mi_ot_s;czas_mi_caly_s;zgodnosc_rgb;zgodnosc_termal")


def numery(argumenty):
    wynik = []
    for a in argumenty:
        od, _, do = a.partition("-")
        wynik += range(int(od), int(do or od) + 1)
    return wynik


def main():
    pary = numery(sys.argv[1:] or ["1-94"])
    wyj = INZ / "wyniki" / "wyniki_dopasowania" / "porownanie_rejestracji.csv"
    tre = lambda M, wz: miary.tre(geo.przenies_punkty(wz["narozniki_rgb"], M), wz["narozniki_termal"], wz["H_termal"])
    wiersze = [NAGLOWEK]
    for n in pary:
        a = Analiza.z_pary(n)
        wz = a.wzorzec
        if wz is None:
            print(f"para {n}: brak adnotacji z CVAT - pomijam")
            continue
        t0 = time.time()
        a.rejestruj()
        t1 = time.time()
        with contextlib.redirect_stdout(io.StringIO()):
            Mo, info = d2.rejestruj_mi(a.rgb_path, a.ter_path, otoczenie=True, log=lambda t: None)
            t2 = time.time()
            Mc, _ = d2.rejestruj_mi(a.rgb_path, a.ter_path, otoczenie=False, log=lambda t: None)
            t3 = time.time()
        r3, ro, rc, rs = tre(a.M, wz), tre(Mo, wz), tre(Mc, wz), tre(info["start"], wz)
        wiersze.append(f"{n};{r3['tre_srednie']:.3f};{r3['tre_max']:.3f};{a.rej.get('model')};{ro['tre_srednie']:.3f};"
                       f"{ro['tre_max']:.3f};{rc['tre_srednie']:.3f};{rc['tre_max']:.3f};{rs['tre_srednie']:.3f};"
                       f"{t1 - t0:.1f};{t2 - t1:.1f};{t3 - t2:.1f};{a.rej.get('zgodnosc_rgb')};{a.rej.get('zgodnosc_termal')}")
        print(wiersze[-1], flush=True)
    wyj.write_text("\n".join(wiersze) + "\n", encoding="utf-8")
    kol = [list(map(float, (w.split(";")[i] for w in wiersze[1:]))) for i in (1, 4, 6)]
    for nazwa, v in zip(("dopasowanie3 (ECC)", "SimpleITK MI w otoczeniu", "SimpleITK MI caly obraz"), kol):
        v = np.array(v)
        print(f"{nazwa:26s} TRE mediana {np.median(v):.2f} mm, <=1 mm: {(v <= 1).sum()}, <=2 mm: {(v <= 2).sum()} / {len(v)}")
    print(f"-> {wyj}")


if __name__ == "__main__":
    main()
