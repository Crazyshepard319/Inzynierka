"""
Zdjecia HEIC (iPhone) -> JPG ponumerowane 1.jpg, 2.jpg, ... w kolejnosci wykonania (EXIF).

    python heic_do_jpg.py [folder] [--oryginaly DIR]

Domyslnie folder = Inzynierka/dane/dane_RGB. Oryginaly HEIC sa przenoszone (nie usuwane) do
archiwum/dane/oryginaly_heic/. Mapowanie nazw (numer -> oryginal, data wykonania) dopisywane
do <folder>/../mapowanie_<folder>.csv. Numeracja od pierwszego wolnego numeru w folderze, wiec
kolejne partie zdjec dopisuja sie na koncu; przerwane uruchomienie mozna powtorzyc.
JPG: jakosc 95, EXIF (data wykonania) i profil kolorow zachowane, orientacja zastosowana.

Wymaga: pip install pillow-heif
"""
import argparse
import csv
import re
from pathlib import Path

import pillow_heif
from PIL import Image, ImageOps

pillow_heif.register_heif_opener()
INZ = Path(__file__).resolve().parent.parent      # folder Inzynierka


def data_wykonania(sciezka):
    """(DateTimeOriginal, SubsecTimeOriginal) z EXIF; puste, gdy brak."""
    with Image.open(sciezka) as im:
        ex = im.getexif()
        sub = ex.get_ifd(0x8769)
        return str(sub.get(36867) or ex.get(306) or ""), str(sub.get(37521) or "")


def main():
    ap = argparse.ArgumentParser(description="HEIC -> JPG numerowane 1, 2, ... wg czasu wykonania")
    ap.add_argument("folder", nargs="?", default=str(INZ / "dane" / "dane_RGB"))
    ap.add_argument("--oryginaly", default=str(INZ / "archiwum" / "dane" / "oryginaly_heic"),
                    help="dokad przeniesc pliki HEIC po konwersji")
    a = ap.parse_args()
    folder, oryginaly = Path(a.folder), Path(a.oryginaly)

    pliki = [p for p in folder.iterdir() if p.suffix.lower() in (".heic", ".heif")]
    if not pliki:
        raise SystemExit(f"Brak plikow HEIC w {folder}")
    daty = {p: data_wykonania(p) for p in pliki}
    pliki.sort(key=lambda p: (*daty[p], p.name))
    oryginaly.mkdir(parents=True, exist_ok=True)
    nr = max((int(p.stem) for p in folder.glob("*") if re.fullmatch(r"\d+", p.stem)), default=0) + 1
    plik_map = folder.parent / f"mapowanie_{folder.name}.csv"
    nowy = not plik_map.exists()

    with open(plik_map, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        if nowy:
            w.writerow(["plik", "oryginal", "data_wykonania", "szerokosc", "wysokosc"])
        for p in pliki:
            cel, kopia = folder / f"{nr}.jpg", oryginaly / p.name
            if cel.exists() or kopia.exists():
                raise SystemExit(f"Juz istnieje {cel if cel.exists() else kopia} - przerywam, nic nie nadpisuje.")
            with Image.open(p) as im:
                im = ImageOps.exif_transpose(im)          # orientacja zastosowana na pikselach
                exif = im.getexif()
                exif[0x0112] = 1
                im.convert("RGB").save(cel, "JPEG", quality=95, exif=exif.tobytes(),
                                       icc_profile=im.info.get("icc_profile"))
                rozmiar = im.size
            p.rename(kopia)                                # oryginal przeniesiony dopiero po zapisie JPG
            w.writerow([cel.name, p.name, daty[p][0], *rozmiar])
            f.flush()
            print(f"{p.name} -> {cel.name}  ({daty[p][0]})")
            nr += 1
    print(f"Gotowe: {len(pliki)} zdjec. Oryginaly HEIC: {oryginaly}. Mapowanie: {plik_map}")


if __name__ == "__main__":
    main()
