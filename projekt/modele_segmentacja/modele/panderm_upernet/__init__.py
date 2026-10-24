"""
PanDerm (ViT-L) + UperNet - adapter do wspolnego interfejsu.

Wagi douczone na ISIC 2018 (trening.py) leza w:
    <modele_dane>/wagi/panderm_upernet/model_najlepszy.pth
Mozna tam tez polozyc checkpoint autorow (*.ckpt), gdyby link zostal naprawiony.
PyTorch jest importowany dopiero przy wczytaniu, wiec rejestr modeli dziala
takze w srodowisku bez PyTorch (model jest wtedy oznaczony jako niedostepny).
"""
from pathlib import Path

import cv2
import numpy as np

from ...interfejs import ModelSegmentacji
from ...konfiguracja import WAGI

KATALOG_WAG = WAGI / "panderm_upernet"
WAGI_BAZOWE = WAGI / "panderm" / "panderm_ll_data6_checkpoint-499.pth"
ROZMIAR = 224


def _wolna_pamiec_gpu_gb(torch):
    """Wolna pamiec karty wg nvidia-smi. Pod Windows (sterownik WDDM)
    torch.cuda.mem_get_info nie widzi pamieci innych procesow, np. treningu."""
    import subprocess
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
        zajete, razem = map(float, o.splitlines()[0].split(","))
        return (razem - zajete) / 1024
    except Exception:
        return torch.cuda.mem_get_info()[0] / 2**30


def plik_wag():
    """Nasz najlepszy checkpoint albo dowolny *.ckpt autorow w katalogu wag."""
    nasz = KATALOG_WAG / "model_najlepszy.pth"
    if nasz.exists():
        return nasz
    inne = sorted(KATALOG_WAG.glob("*.ckpt")) if KATALOG_WAG.exists() else []
    return inne[0] if inne else None


class Model(ModelSegmentacji):
    klucz = "panderm_upernet"
    nazwa = "PanDerm + UperNet"
    opis = ("Model bazowy PanDerm (ViT-L, 2 mln zdjec dermatologicznych) z glowica UperNet, "
            "douczony na ISIC 2018 Task 1 wg procedury autorow. Wejscie 224x224.")
    # kadrowanie jak w ISIC 2018 Task 1 (zmierzone na 2594 maskach treningowych):
    # dluzszy bok ramki znamienia = 0.53 boku obrazu (mediana), zdjecia 3:2 sciskane do 224x224
    kadr_docelowy = 0.53
    proporcje_kadru = 1.5

    def dostepnosc(self):
        try:
            import torch  # noqa: F401
        except ImportError:
            return False, ("brak PyTorch w tym srodowisku Pythona - uruchom przez uruchom_tester.bat "
                           "albo interpreterem modele_dane\\srodowisko")
        if plik_wag() is None:
            return False, f"brak wytrenowanych wag w {KATALOG_WAG} - uruchom trening (trening.py)"
        return True, ""

    def _wczytaj(self):
        import time
        from datetime import datetime
        import torch
        from .architektura import PanDermUperNet, wczytaj_wytrenowany
        self._torch = torch
        self._siec = None                                   # zwolnij poprzednia wersje
        self._urz = self._wybierz_urzadzenie(torch)
        self._plik = plik_wag()
        self._mtime = self._plik.stat().st_mtime
        for proba in range(3):
            try:
                self._siec = wczytaj_wytrenowany(PanDermUperNet(), self._plik).to(self._urz).eval()
                break
            except Exception:
                if proba == 2:
                    raise
                time.sleep(5)               # plik moze byc wlasnie zapisywany przez trening
        self.wersja_wag = f"wagi z {datetime.fromtimestamp(self._mtime):%d.%m %H:%M}"

    def nieaktualny(self):
        if not self._wczytany:
            return False
        p = plik_wag()
        return p is not None and (p != self._plik or p.stat().st_mtime != self._mtime)

    def _wybierz_urzadzenie(self, torch, potrzeba_gb=2.5):
        """GPU, jesli ma dosc wolnej pamieci; inaczej CPU (np. gdy na GPU trwa trening -
        przepelnienie pamieci karty spowolniloby trening kilkadziesiat razy)."""
        if torch.cuda.is_available():
            wolne = _wolna_pamiec_gpu_gb(torch)
            if wolne >= potrzeba_gb:
                self.urzadzenie = "GPU"
                return "cuda"
            self.urzadzenie = f"CPU (GPU zajete, wolne {wolne:.1f} GB)"
        else:
            self.urzadzenie = "CPU"
        import os
        torch.set_num_threads(max(1, (os.cpu_count() or 2) // 2))   # polowa rdzeni - reszta dla treningu
        return "cpu"

    def _prawdopodobienstwo(self, wycinek_bgr):
        torch = self._torch
        h, w = wycinek_bgr.shape[:2]
        # jak w evaluate.ipynb autorow: RGB, 224x224 INTER_CUBIC, normalizacja (x-0.5)/0.5
        rgb = cv2.resize(wycinek_bgr[..., ::-1], (ROZMIAR, ROZMIAR), interpolation=cv2.INTER_CUBIC)
        x = torch.from_numpy(rgb.astype(np.float32) / 255).permute(2, 0, 1)[None]
        x = ((x - 0.5) / 0.5).to(self._urz)
        with torch.no_grad():
            p = torch.softmax(self._siec(x), dim=1)[0, 1].float().cpu().numpy()
        return cv2.resize(p, (w, h), interpolation=cv2.INTER_LINEAR)
