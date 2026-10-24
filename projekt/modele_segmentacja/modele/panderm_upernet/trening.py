"""
Douczanie PanDerm + UperNet na ISIC 2018 Task 1 wg procedury autorow
(repozytoria/PanDerm/segmentation: run.sh, workers/train.py, workers/test.py,
models/__init__.py, datasets/dataset_seg.py).

Zgodne z autorami:
  - dane: oficjalny podzial ISIC 2018 (2594 trening / 100 walidacja / 1000 test), 224x224
  - augmentacja: ColorJitter(0.2,0.2,0.2,0.2), RandomGrayscale(0.2),
    RandomAutocontrast(0.2), RandomInvert(0.2), normalizacja (x-0.5)/0.5
  - strata CrossEntropy, AdamW lr=1e-4 wd=0.05, CosineAnnealingLR(T_max=epoki), 100 epok
  - batch 2 (u autorow 2 GPU x 1), seed 0
  - wybor modelu: max Jaccard na walidacji; metryki z najwieksza spojna skladowa
Roznice (wymuszone przez karte 8 GB, patrz README):
  - AdamW 8-bitowy (bitsandbytes) zamiast 32-bitowego - 32-bitowy potrzebuje ~8,4 GB
  - obliczenia w bfloat16 (autocast); wagi i aktualizacje w float32

Uzycie (z folderu Inzynierka/projekt, srodowisko modele_dane):
    python -m modele_segmentacja.modele.panderm_upernet.trening            # pelny trening
    python -m modele_segmentacja.modele.panderm_upernet.trening --wznow    # kontynuacja po przerwaniu
    python -m modele_segmentacja.modele.panderm_upernet.trening --tylko_test
    python -m modele_segmentacja.modele.panderm_upernet.trening --proba    # szybki test (kilka krokow)
"""
import argparse
import csv
import json
import random
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from ...interfejs import metryki, najwieksza_skladowa
from . import KATALOG_WAG, WAGI_BAZOWE
from .architektura import PanDermUperNet, wczytaj_backbone_panderm, wczytaj_wytrenowany
from .dane import GOTOWE

NORM = transforms.Normalize(mean=[0.5] * 3, std=[0.5] * 3)


class ZbiorISIC(Dataset):
    def __init__(self, czesc, trening=False, procent=100):
        folder = {"train": "Training", "val": "Validation", "test": "Test"}[czesc]
        self.obrazy = sorted((GOTOWE / f"{folder}_Data").glob("*.png"))
        self.maski = [GOTOWE / f"{folder}_GroundTruth" / f"{p.stem}_segmentation.png" for p in self.obrazy]
        if not self.obrazy:
            raise FileNotFoundError(f"Brak danych w {GOTOWE / (folder + '_Data')} - uruchom dane.py")
        if trening:     # --percent autorow
            n = int(procent * len(self.obrazy) / 100)
            self.obrazy, self.maski = self.obrazy[:n], self.maski[:n]
        self.trening = trening
        self.aug = transforms.Compose([
            transforms.ColorJitter(0.2, 0.2, 0.2, 0.2),
            transforms.RandomGrayscale(p=0.2),
            transforms.RandomAutocontrast(p=0.2),
            transforms.RandomInvert(p=0.2),
        ]) if trening else None

    def __len__(self):
        return len(self.obrazy)

    def __getitem__(self, i):
        obraz = Image.fromarray(cv2.imread(str(self.obrazy[i]))[..., ::-1].copy())
        if self.aug is not None:
            obraz = self.aug(obraz)
        x = NORM(transforms.functional.to_tensor(obraz))
        y = torch.from_numpy((cv2.imread(str(self.maski[i]), cv2.IMREAD_GRAYSCALE) > 127).astype(np.int64))
        return x, y, self.obrazy[i].stem


def ocena(model, loader, amp, zapisz_csv=None):
    """Dice i Jaccard na obraz (argmax + najwieksza skladowa), jak validation/test_step autorow."""
    model.eval()
    wiersze = []
    with torch.no_grad():
        for x, y, nazwy in loader:
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=amp):
                logity = model(x.cuda(non_blocking=True))
            pred = logity.argmax(1).cpu().numpy().astype(np.uint8)
            for p, t, n in zip(pred, y.numpy(), nazwy):
                if t.max() == 0:                      # jak u autorow (test_step)
                    t = t.copy()
                    t[t.shape[0] // 2, t.shape[1] // 2] = 1
                m = metryki(najwieksza_skladowa(p), t)
                wiersze.append((n, m["dice"], m["iou"]))
    model.train()
    if zapisz_csv:
        with open(zapisz_csv, "w", newline="") as f:
            csv.writer(f).writerows([("nazwa", "dice", "jaccard")] + wiersze)
    d = np.array([w[1:] for w in wiersze])
    return float(d[:, 0].mean()), float(d[:, 1].mean())


def nie_usypiaj(wlacz=True):
    """Windows: nie usypiaj komputera w trakcie treningu."""
    if sys.platform == "win32":
        import ctypes
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if wlacz else 0))


def main():
    ap = argparse.ArgumentParser(description="Douczanie PanDerm + UperNet (ISIC 2018)")
    ap.add_argument("--epoki", type=int, default=100)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--wd", type=float, default=0.05)
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--procent", type=float, default=100, help="procent danych treningowych (--percent autorow)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--optymalizator", choices=["adamw8bit", "adamw"], default="adamw8bit")
    ap.add_argument("--bez_amp", action="store_true", help="liczenie w float32 (wolniej)")
    ap.add_argument("--przebieg", default="", help="nazwa folderu przebiegu (domyslnie data)")
    ap.add_argument("--wznow", action="store_true", help="kontynuuj ostatni przebieg")
    ap.add_argument("--tylko_test", action="store_true", help="tylko ocena na zbiorze testowym")
    ap.add_argument("--proba", action="store_true", help="szybka proba: 20 krokow + mala walidacja")
    a = ap.parse_args()
    amp = not a.bez_amp

    torch.manual_seed(a.seed); np.random.seed(a.seed); random.seed(a.seed)
    torch.backends.cuda.matmul.allow_tf32 = True      # torch.set_float32_matmul_precision("high")
    torch.backends.cudnn.allow_tf32 = True
    if not torch.cuda.is_available():
        sys.exit("Trening wymaga karty NVIDIA z CUDA.")

    przebiegi = KATALOG_WAG / "przebiegi"
    if a.wznow and not a.przebieg:
        istniejace = sorted(p for p in przebiegi.glob("*") if (p / "ostatni.pth").exists())
        if not istniejace:
            sys.exit("Brak przebiegu do wznowienia.")
        katalog = istniejace[-1]
    else:
        katalog = przebiegi / (a.przebieg or ("proba_" if a.proba else "") + datetime.now().strftime("%Y%m%d_%H%M%S"))
    katalog.mkdir(parents=True, exist_ok=True)
    # proba nie moze nadpisac prawdziwych wag, ktore wczytuje adapter
    najlepszy = (katalog if a.proba else KATALOG_WAG) / "model_najlepszy.pth"
    print(f"Przebieg: {katalog}")

    test = DataLoader(ZbiorISIC("test"), batch_size=8, num_workers=a.workers)
    if a.tylko_test:
        model = wczytaj_wytrenowany(PanDermUperNet(), najlepszy).cuda()
        d, j = ocena(model, test, amp, katalog / "test_na_obraz.csv")
        print(f"TEST (1000 obrazow): Dice={d:.4f}  Jaccard={j:.4f}")
        (katalog / "wynik_test.json").write_text(json.dumps({"Dsc": d, "Jac": j}, indent=2))
        return

    zb_tr = ZbiorISIC("train", trening=True, procent=a.procent)
    zb_val = ZbiorISIC("val")
    if a.proba:
        zb_val.obrazy, zb_val.maski = zb_val.obrazy[:16], zb_val.maski[:16]
    tren = DataLoader(zb_tr, batch_size=a.batch, shuffle=True, drop_last=True, num_workers=a.workers,
                      pin_memory=True, persistent_workers=a.workers > 0)
    wal = DataLoader(zb_val, batch_size=8, num_workers=a.workers)
    print(f"Dane: trening {len(zb_tr)}, walidacja {len(zb_val)}, test {len(test.dataset)}")

    model = PanDermUperNet().cuda()
    params = [p for p in model.parameters() if p.requires_grad]
    if a.optymalizator == "adamw8bit":
        import bitsandbytes as bnb
        opt = bnb.optim.AdamW8bit(params, lr=a.lr, weight_decay=a.wd)
    else:
        opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=a.wd)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.epoki)

    start, best_jac = 0, -1.0
    if a.wznow and (katalog / "ostatni.pth").exists():
        st = torch.load(katalog / "ostatni.pth", map_location="cpu", weights_only=False)
        model.load_state_dict(st["model"]); opt.load_state_dict(st["opt"]); sched.load_state_dict(st["sched"])
        start, best_jac = st["epoka"] + 1, st["best_jac"]
        print(f"Wznowienie od epoki {start + 1}, najlepszy Jaccard dotad {best_jac:.4f}")
    else:
        ok, _ = wczytaj_backbone_panderm(model, WAGI_BAZOWE)
        print(f"Wagi bazowe PanDerm: wczytano {len(ok)} tensorow backbone")
        (katalog / "konfiguracja.json").write_text(json.dumps(vars(a), indent=2))

    log = katalog / "log.csv"
    if not log.exists():
        log.write_text("epoka,strata,val_dice,val_jaccard,lr,czas_s\n")
    nie_usypiaj(True)
    model.train()
    try:
        for ep in range(start, a.epoki):
            t0, suma, n = time.time(), 0.0, 0
            for k, (x, y, _) in enumerate(tren, 1):
                with torch.autocast("cuda", dtype=torch.bfloat16, enabled=amp):
                    strata = F.cross_entropy(model(x.cuda(non_blocking=True)), y.cuda(non_blocking=True))
                opt.zero_grad(set_to_none=True)
                strata.backward()
                opt.step()
                suma, n = suma + strata.item(), n + 1
                if k % 50 == 0 or k == len(tren):
                    v = (time.time() - t0) / k
                    print(f"\r  epoka {ep + 1}/{a.epoki}  krok {k}/{len(tren)}  strata {suma / n:.4f}  "
                          f"~{v * (len(tren) - k) / 60:.1f} min do konca epoki   ", end="", flush=True)
                if a.proba and k >= 20:
                    break
            lr = opt.param_groups[0]["lr"]
            sched.step()
            dice, jac = ocena(model, wal, amp)
            czas = time.time() - t0
            with open(log, "a") as f:
                f.write(f"{ep + 1},{suma / n:.5f},{dice:.5f},{jac:.5f},{lr:.3e},{czas:.0f}\n")
            lepszy = jac > best_jac
            if lepszy:
                best_jac = jac
                torch.save(model.state_dict(), najlepszy)
                if najlepszy.parent != katalog:
                    shutil.copy(najlepszy, katalog / "model_najlepszy.pth")
            if not a.proba:      # proba nie zostawia punktu wznowienia (~2,6 GB)
                torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                            "epoka": ep, "best_jac": best_jac}, katalog / "ostatni.pth")
            pozostalo = czas * (a.epoki - ep - 1) / 3600
            print(f"\n  epoka {ep + 1}: strata {suma / n:.4f}  walidacja Dice {dice:.4f} Jaccard {jac:.4f}"
                  f"{'  <- najlepszy, zapisano' if lepszy else ''}   ({czas / 60:.1f} min, zostalo ~{pozostalo:.1f} h)")
            if a.proba:
                break
    finally:
        nie_usypiaj(False)

    if a.proba:
        shutil.rmtree(katalog, ignore_errors=True)
        print("Proba zakonczona - trening dziala (pliki proby usuniete).")
        return
    print("Ocena najlepszego modelu na zbiorze testowym (1000 obrazow)...")
    model = wczytaj_wytrenowany(PanDermUperNet(), najlepszy).cuda()
    d, j = ocena(model, test, amp, katalog / "test_na_obraz.csv")
    print(f"TEST: Dice={d:.4f}  Jaccard={j:.4f}")
    (katalog / "wynik_test.json").write_text(json.dumps({"Dsc": d, "Jac": j}, indent=2))


if __name__ == "__main__":
    main()
