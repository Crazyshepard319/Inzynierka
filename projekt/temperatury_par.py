"""
Mapy temperatur [°C] i surowe wartosci detektora dla wszystkich par:
dane/Termowizja/<nagranie>.SEQ -> dane/pary/N/termal_C.npy + dane/pary/N/termal_surowe.npy

    python temperatury_par.py [--emisyjnosc 0.98]
    python temperatury_par.py --tylko_surowe      # tylko termal_surowe.npy (intensywnosc pikseli znamienia)

termal_C.npy = float32 (240 x 320), termal_surowe.npy = uint16 (240 x 320) - surowa wartosc detektora
pierwszej klatki (ta sama, z ktorej powstal termal.jpg), uzywana jako intensywnosc pikseli znamienia
(analiza/pomiary.piksele_znamienia). Obie piksel w piksel jak termal.jpg (te same poprawki odczytu co
read_flirpy.py). Ktore nagranie nalezy do pary - z dane/mapowanie_dane_termowizja.csv.
Kontrola: korelacja rang temperatury z jasnoscia termal.jpg (paleta inferno rosnie z temperatura)
musi byc bliska 1 - inaczej mapa i obraz nie pasuja do siebie.
Podsumowanie: dane/temperatury.csv (temperatura skory poza znacznikiem, jesli jest maska z CVAT).
Wymaga flirpy (jest w venvie inzynierka).
"""
import argparse
import csv
import re
from pathlib import Path

import cv2
import numpy as np

from read_flirpy import EMISYJNOSC_SKORY, temperatura_c, wczytaj_klatki

INZ = Path(__file__).resolve().parent.parent
DANE = INZ / "dane"


def _rangi(x):
    r = np.empty(x.size)
    r[np.argsort(x, kind="stable")] = np.arange(x.size)
    return r


def main():
    ap = argparse.ArgumentParser(description="Mapy temperatur °C dla par")
    ap.add_argument("--emisyjnosc", type=float, default=EMISYJNOSC_SKORY)
    ap.add_argument("--tylko_surowe", action="store_true", help="tylko termal_surowe.npy (bez map °C i temperatury.csv)")
    a = ap.parse_args()

    with open(DANE / "mapowanie_dane_termowizja.csv", encoding="utf-8-sig") as f:
        nagranie = {r["plik"]: r["nagranie"] for r in csv.DictReader(f, delimiter=";")}
    pary = sorted(int(p.name) for p in (DANE / "pary").iterdir() if p.is_dir() and re.fullmatch(r"\d+", p.name))
    wiersze, problemy = [], []
    for n in pary:
        kat = DANE / "pary" / str(n)
        seq = DANE / "Termowizja" / nagranie[f"{n}.jpg"]
        surowe = np.rint(wczytaj_klatki(seq, 1)[0]).astype(np.uint16)
        np.save(kat / "termal_surowe.npy", surowe)
        szary = cv2.cvtColor(cv2.imread(str(kat / "termal.jpg")), cv2.COLOR_BGR2GRAY).astype(np.float64)
        if a.tylko_surowe:
            if surowe.shape != szary.shape:
                problemy.append(f"para {n}: surowe {surowe.shape} != termal.jpg {szary.shape}")
            else:
                rho = float(np.corrcoef(_rangi(surowe.ravel()), _rangi(szary.ravel()))[0, 1])
                if rho < 0.95:
                    problemy.append(f"para {n}: korelacja rang surowych z termal.jpg {rho:.3f} < 0,95")
            print(f"para {n}: {seq.name} -> termal_surowe.npy  ({surowe.min()}..{surowe.max()})")
            continue
        t, meta = temperatura_c(seq, a.emisyjnosc)
        np.save(kat / "termal_C.npy", t)
        if szary.shape != t.shape:
            problemy.append(f"para {n}: mapa {t.shape} != termal.jpg {szary.shape}")
        else:
            rho = float(np.corrcoef(_rangi(t.ravel()), _rangi(szary.ravel()))[0, 1])
            if rho < 0.95:
                problemy.append(f"para {n}: korelacja rang z termal.jpg {rho:.3f} < 0,95")
        skora = np.ones(t.shape, bool)
        mz = kat / "maska_znacznik_termal.png"
        if mz.exists():                                    # bez folii i pasa 3 px wokol niej
            skora = cv2.dilate(cv2.imread(str(mz), cv2.IMREAD_GRAYSCALE), np.ones((7, 7), np.uint8)) == 0
        v = t[skora & np.isfinite(t)]
        wiersze.append({"para": n, "nagranie": seq.name, "emisyjnosc": round(float(meta["Emissivity"]), 3),
                        "T_skory_p5": round(float(np.percentile(v, 5)), 2),
                        "T_skory_mediana": round(float(np.median(v)), 2),
                        "T_skory_p95": round(float(np.percentile(v, 95)), 2),
                        "korelacja_z_jpg": round(rho, 4) if szary.shape == t.shape else ""})
        print(f"para {n}: {seq.name} -> termal_C.npy  skora {wiersze[-1]['T_skory_mediana']:.2f} °C "
              f"(p5 {wiersze[-1]['T_skory_p5']:.2f}, p95 {wiersze[-1]['T_skory_p95']:.2f})")

    if wiersze:
        with open(DANE / "temperatury.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(wiersze[0]), delimiter=";")
            w.writeheader()
            w.writerows(wiersze)
        print(f"\nGotowe: {len(wiersze)} map. Podsumowanie: {DANE / 'temperatury.csv'}")
    else:
        print(f"\nGotowe: termal_surowe.npy dla {len(pary)} par.")
    print("Problemy:", "brak" if not problemy else "")
    for p in problemy:
        print("  -", p)


if __name__ == "__main__":
    main()
