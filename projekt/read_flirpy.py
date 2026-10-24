"""
Nagranie FLIR .seq -> klatki obrazu (paleta inferno, normalizacja percentylowa 2-98 %).

Uzycie:
    python read_flirpy.py
        plik z FILEPATH ponizej, klatki PNG (frame_000.png, ...) jak dotad
    python read_flirpy.py <plik.seq | folder> [--wyjscie DIR] [--format jpg|png] [--numeruj] [--wszystkie]
        folder: kazdy plik .seq/.SEQ po kolei (wg nazwy);
        --numeruj: nazwy 1.jpg, 2.jpg, ... (od pierwszego wolnego numeru w DIR),
                   mapowanie nazw w <DIR>/../mapowanie_<nazwa DIR>.csv

Poprawki odczytu (flirpy czyta surowe dane z naglowkiem):
  - przesuniecie kolumn zalezy od kamery: FLIR A655sc (szer. 640) -> 66 px, kamera 320x240 -> 0
    (sprawdzone na nagraniach z 23.10.2026: przy 66 px widac szew w x = 66),
  - dolne wiersze telemetrii (wartosci 0/65535, np. 6 wierszy pod obrazem 320x240) sa obcinane,
    inaczej psuja normalizacje (2. percentyl = 0, caly obraz wychodzi jednolicie zolty).
"""
import argparse
import csv
import logging
import re
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# flirpy generuje dziwne ostrzeżenia/logi dla części plików SEQ (bug w bibliotece).
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API.*")
logging.getLogger().setLevel(logging.ERROR)
from flirpy.io.seq import Seq

INZ = Path(__file__).resolve().parent.parent      # folder Inzynierka
# nagranie do rozpakowania: nowe w dane/dane_termowizja/, stare w archiwum/dane/nagrania_termowizja/
FILEPATH = INZ / "archiwum" / "dane" / "nagrania_termowizja" / "Rec-000040.seq"
NUM_FRAMES_TO_SAVE = 10
SAVE_ALL_FRAMES = False  # jeśli True, to zapisze wszystkie klatki, jeśli False, to tylko NUM_FRAMES_TO_SAVE klatek
# przesuniecie kolumn (offset naglowka SEQ) wg szerokosci klatki; inne kamery: 0
HORIZONTAL_ROLL_PIXELS = {640: 66}                # FLIR A655sc
PERCENTILE_RANGE = (2, 98)


def utnij_telemetrie(klatka):
    """Obcina dolne wiersze, w ktorych > 30% wartosci to 0 albo 65535 (telemetria, nie obraz)."""
    h = klatka.shape[0]
    while h > 1:
        w = klatka[h - 1]
        if np.mean((w == 0) | (w == 65535)) <= 0.3:
            break
        h -= 1
    return klatka[:h]


def wczytaj_klatki(sciezka, ile=None):
    """Klatki nagrania jako tablica (N, H, W) float64, z poprawkami odczytu. ile=None: wszystkie."""
    seq = Seq(str(sciezka))
    n = len(seq) if ile is None else min(ile, len(seq))
    klatki = []
    for i in range(n):
        frm = seq[i]
        frm = frm.get_image() if hasattr(frm, "get_image") else np.array(frm)
        frm = utnij_telemetrie(np.asarray(frm))
        roll = HORIZONTAL_ROLL_PIXELS.get(frm.shape[1], 0)
        if roll:
            # Korekta zawijania obrazu (przesunięcie kolumn w poziomie).
            frm = np.roll(frm, roll, axis=1)
        klatki.append(frm.astype(np.float64))
    if hasattr(seq, "close"):
        try:
            seq.close()
        except Exception:
            pass
    return np.stack(klatki)


def zapisz_klatki(klatki, sciezki, quiet=False):
    """Normalizacja wspolna dla calego nagrania (percentyle 2-98) i zapis z paleta inferno."""
    lo, hi = PERCENTILE_RANGE
    vmin = float(np.nanpercentile(klatki, lo))
    vmax = float(np.nanpercentile(klatki, hi))
    for frm, out_path in zip(klatki, sciezki):
        frm = np.array(frm, dtype="float64")
        if not np.isfinite(frm).all():
            frm = np.nan_to_num(frm, nan=np.nanmedian(frm))
        if np.isclose(vmax, vmin):
            norm = np.full(frm.shape, 0.5, dtype="float32")
        else:
            norm = (frm - vmin) / (vmax - vmin + 1e-12)
        rgba = plt.get_cmap("inferno")(np.clip(norm, 0.0, 1.0))
        rgb = (rgba[..., :3] * 255 + 0.5).astype(np.uint8)          # JPG nie ma kanalu alfa
        kw = {"pil_kwargs": {"quality": 95}} if Path(out_path).suffix.lower() in (".jpg", ".jpeg") else {}
        plt.imsave(str(out_path), rgb, **kw)
        if not quiet:
            print(f"Zapisano: {out_path}  (used_vmin={vmin:.3f}, used_vmax={vmax:.3f})")
    return vmin, vmax


def _pierwszy_wolny_numer(katalog):
    nr = [int(p.stem) for p in Path(katalog).glob("*") if re.fullmatch(r"\d+", p.stem)]
    return max(nr, default=0) + 1


def konwertuj(zrodlo, wyjscie, fmt="jpg", numeruj=False, wszystkie=False):
    """Plik .seq albo folder plikow .seq -> obrazy w folderze wyjscie."""
    zrodlo, wyjscie = Path(zrodlo), Path(wyjscie)
    pliki = ([zrodlo] if zrodlo.is_file() else
             sorted(p for p in zrodlo.iterdir() if p.suffix.lower() == ".seq"))
    if not pliki:
        raise SystemExit(f"Brak plikow .seq w {zrodlo}")
    wyjscie.mkdir(parents=True, exist_ok=True)
    nr = _pierwszy_wolny_numer(wyjscie) if numeruj else None
    mapowanie = []
    for p in pliki:
        klatki = wczytaj_klatki(p, None if wszystkie else (1 if numeruj else NUM_FRAMES_TO_SAVE))
        if numeruj:
            nazwy = [f"{nr}.{fmt}"] if len(klatki) == 1 else [f"{nr}_{k:03d}.{fmt}" for k in range(len(klatki))]
        else:
            nazwy = [f"{p.stem}_frame_{k:03d}.{fmt}" for k in range(len(klatki))]
        vmin, vmax = zapisz_klatki(klatki, [wyjscie / n for n in nazwy], quiet=True)
        for n in nazwy:
            mapowanie.append((n, p.name, klatki.shape[2], klatki.shape[1], f"{vmin:.0f}", f"{vmax:.0f}"))
        print(f"{p.name} -> {', '.join(nazwy)}  ({klatki.shape[2]}x{klatki.shape[1]}, vmin={vmin:.0f}, vmax={vmax:.0f})")
        if numeruj:
            nr += 1
    if numeruj:
        plik_map = wyjscie.parent / f"mapowanie_{wyjscie.name}.csv"
        nowy = not plik_map.exists()
        with open(plik_map, "a", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            if nowy:
                w.writerow(["plik", "nagranie", "szerokosc", "wysokosc", "vmin_surowe", "vmax_surowe"])
            w.writerows(mapowanie)
        print(f"Mapowanie nazw: {plik_map}")
    print(f"Gotowe: {len(mapowanie)} obrazow w {wyjscie}")


def main():
    ap = argparse.ArgumentParser(description="FLIR .seq -> obrazy (inferno, percentyle 2-98)")
    ap.add_argument("zrodlo", nargs="?", help="plik .seq albo folder z plikami .seq (domyslnie FILEPATH)")
    ap.add_argument("--wyjscie", help="folder na obrazy")
    ap.add_argument("--format", default=None, choices=["jpg", "png"], help="domyslnie png dla FILEPATH, jpg dla argumentu")
    ap.add_argument("--numeruj", action="store_true", help="nazwy 1.jpg, 2.jpg, ... + plik mapowania")
    ap.add_argument("--wszystkie", action="store_true", help="wszystkie klatki (domyslnie: 1 przy --numeruj, inaczej 10)")
    a = ap.parse_args()

    if a.zrodlo is None:                       # tryb jak dotad: FILEPATH -> frame_NNN.png
        seq = Path(FILEPATH)
        # klatki obok nagrania, gdy jest w dane/ (np. dane_termowizja/znamie_01/Rec-0000NN/),
        # inaczej (np. nagranie z archiwum) do dane/dane_termowizja/<nagranie>/
        out_dir = Path(a.wyjscie) if a.wyjscie else (
            seq.with_suffix("") if (INZ / "dane") in seq.parents else INZ / "dane" / "dane_termowizja" / seq.stem)
        out_dir.mkdir(parents=True, exist_ok=True)
        klatki = wczytaj_klatki(seq, None if SAVE_ALL_FRAMES else NUM_FRAMES_TO_SAVE)
        print(f"Ustawiony rozmiar klatki: {klatki.shape[1:]}")
        fmt = a.format or "png"
        zapisz_klatki(klatki, [out_dir / f"frame_{i:03d}.{fmt}" for i in range(len(klatki))])
        return

    zrodlo = Path(a.zrodlo)
    wyjscie = Path(a.wyjscie) if a.wyjscie else INZ / "dane" / "dane_termowizja"
    konwertuj(zrodlo, wyjscie, a.format or "jpg", a.numeruj, a.wszystkie)


if __name__ == "__main__":
    main()
