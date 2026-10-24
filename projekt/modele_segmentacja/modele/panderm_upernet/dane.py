"""
Zbior ISIC 2018 Task 1 (segmentacja znamion) - pobranie i przygotowanie.

Uzycie (srodowisko z modele_dane):
    python -m modele_segmentacja.modele.panderm_upernet.dane pobierz
    python -m modele_segmentacja.modele.panderm_upernet.dane przygotuj

Przygotowanie odtwarza wczytywanie danych z kodu autorow
(repozytoria/PanDerm/segmentation/datasets/dataset_seg.py): obraz -> 224x224
INTER_CUBIC, maska -> 224x224 INTER_NEAREST, ten sam podzial train/val/test.
Robimy to raz (zamiast przy kazdej epoce), wiec trening nie dekoduje 11 GB JPEG-ow.
"""
import json
import os
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

from ...konfiguracja import DANE

KATALOG = DANE / "ISIC2018"
ZIP = KATALOG / "zip"
GOTOWE = KATALOG / "224"
ROZMIAR = 224
URL = "https://isic-challenge-data.s3.amazonaws.com/2018/"

# plik zip -> folder docelowy (nazwy folderow jak w dataset_seg.py autorow)
PLIKI = {
    "ISIC2018_Task1-2_Training_Input.zip": "Training_Data",
    "ISIC2018_Task1_Training_GroundTruth.zip": "Training_GroundTruth",
    "ISIC2018_Task1-2_Validation_Input.zip": "Validation_Data",
    "ISIC2018_Task1_Validation_GroundTruth.zip": "Validation_GroundTruth",
    "ISIC2018_Task1-2_Test_Input.zip": "Test_Data",
    "ISIC2018_Task1_Test_GroundTruth.zip": "Test_GroundTruth",
}


# ── pobieranie (rownolegle zakresy HTTP, z wznawianiem) ──────────────────────

def pobierz_plik(url, cel, watki=12, kawalek=32 << 20):
    import requests
    cel = Path(cel)
    rozmiar = int(requests.head(url, allow_redirects=True, timeout=30).headers["Content-Length"])
    stan_plik = cel.with_suffix(cel.suffix + ".stan")
    if cel.exists() and cel.stat().st_size == rozmiar and not stan_plik.exists():
        print(f"  {cel.name}: juz pobrany")
        return
    n = (rozmiar + kawalek - 1) // kawalek
    gotowe = set(json.loads(stan_plik.read_text())) if stan_plik.exists() else set()
    if not cel.exists() or cel.stat().st_size != rozmiar:
        with open(cel, "wb") as f:
            f.truncate(rozmiar)
        gotowe = set()
    blokada = threading.Lock()
    t0, pobrane = time.time(), [0]

    def zapisz_stan():
        stan_plik.write_text(json.dumps(sorted(gotowe)))

    def pobierz_kawalek(i):
        a = i * kawalek
        b = min(rozmiar, a + kawalek) - 1
        for proba in range(20):
            try:
                r = requests.get(url, headers={"Range": f"bytes={a}-{b}"}, timeout=60)
                r.raise_for_status()
                if len(r.content) != b - a + 1:
                    raise IOError("niepelny kawalek")
                with open(cel, "r+b") as f:
                    f.seek(a)
                    f.write(r.content)
                break
            except Exception as e:
                if proba == 19:
                    raise
                time.sleep(3 + proba)
        with blokada:
            gotowe.add(i)
            pobrane[0] += b - a + 1
            zapisz_stan()
            v = pobrane[0] / max(1e-6, time.time() - t0)
            reszta = (n - len(gotowe)) * kawalek / max(v, 1)
            print(f"\r  {cel.name}: {len(gotowe)}/{n} czesci  {v / 2**20:.1f} MB/s  "
                  f"pozostalo ~{reszta / 60:.0f} min   ", end="", flush=True)

    with ThreadPoolExecutor(watki) as ex:
        list(ex.map(pobierz_kawalek, [i for i in range(n) if i not in gotowe]))
    stan_plik.unlink()
    print(f"\n  {cel.name}: OK ({rozmiar / 2**30:.2f} GB)")


def pobierz():
    ZIP.mkdir(parents=True, exist_ok=True)
    # najpierw male pliki (maski, walidacja), na koncu duze
    for nazwa in sorted(PLIKI, key=lambda n: ("Input" in n, "Training" in n)):
        pobierz_plik(URL + nazwa, ZIP / nazwa)


# ── przygotowanie 224x224 ────────────────────────────────────────────────────

def przygotuj(watki=8):
    for nazwa, folder in PLIKI.items():
        zrodlo = ZIP / nazwa
        if not zrodlo.exists() or zrodlo.with_suffix(".zip.stan").exists():
            print(f"  {nazwa}: brak albo niedokonczone pobieranie - najpierw 'pobierz'")
            continue
        cel = GOTOWE / folder
        cel.mkdir(parents=True, exist_ok=True)
        maski = "GroundTruth" in folder
        z = zipfile.ZipFile(zrodlo)
        czlony = [c for c in z.namelist()
                  if c.lower().endswith(".png" if maski else ".jpg") and "/._" not in c]
        blokada = threading.Lock()

        def jeden(c):
            wyj = cel / (Path(c).stem + ".png")
            if wyj.exists():
                return
            with blokada:                      # ZipFile nie jest bezpieczny watkowo
                dane = z.read(c)
            img = cv2.imdecode(np.frombuffer(dane, np.uint8), cv2.IMREAD_COLOR)
            if maski:   # jak u autorow: INTER_NEAREST, kanal 0, niezerowe = znamie
                img = cv2.resize(img, (ROZMIAR, ROZMIAR), interpolation=cv2.INTER_NEAREST)
                img = (img[..., 0] > 0).astype(np.uint8) * 255
            else:       # jak u autorow: INTER_CUBIC
                img = cv2.resize(img, (ROZMIAR, ROZMIAR), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(str(wyj), img)

        t0 = time.time()
        with ThreadPoolExecutor(watki) as ex:
            for k, _ in enumerate(ex.map(jeden, czlony), 1):
                if k % 100 == 0 or k == len(czlony):
                    print(f"\r  {folder}: {k}/{len(czlony)}  ({time.time() - t0:.0f} s)", end="", flush=True)
        print()


if __name__ == "__main__":
    polecenie = sys.argv[1] if len(sys.argv) > 1 else ""
    if polecenie == "pobierz":
        pobierz()
    elif polecenie == "przygotuj":
        przygotuj()
    else:
        print(__doc__)
