"""
Trening U-Netu segmentujacego znacznik Π na termowizji (model M3).

    trenuj_unet_termal.bat                     # 5 foldow + model koncowy na wszystkich parach
    trenuj_unet_termal.bat --epoki 20          # krocej
    trenuj_unet_termal.bat --proba             # szybki test (2 epoki, jeden fold)
    python -m modele_segmentacja.unet_termal.trening --npz zbior.npz --wyjscie FOLDER   # poza Windows

Walidacja krzyzowa po znamionach (dane/znamiona.csv): model foldu k uczy sie na parach z pozostalych
foldow, a pary foldu k sa jego zbiorem testowym. Liczba epok jest stala (bez wyboru najlepszej epoki na
zbiorze testowym), wiec wynik testu jest nieobciazony. Model koncowy (wszystkie.onnx) uczy sie na
wszystkich parach - uzywa go system dla obrazow spoza bazy; dla par z bazy system bierze model foldu,
w ktorym para byla testowa (para nie byla w treningu).

Strata: entropia krzyzowa binarna + (1 - miekki Dice). AdamW, lr 2e-3, wd 1e-4, cosinus do zera,
paczka 8, augmentacja z dane.py. Wynik:
    <wagi>/fold1..5.onnx, wszystkie.onnx (+ .pth)          modele dla aplikacji (cv2.dnn, bez PyTorch)
    <wyniki>/trening_<data>/log_fold*.csv, ocena_oof.csv, trening.json
"""
import argparse
import csv
import inspect
import json
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from ..konfiguracja import WAGI, WYNIKI
from .architektura import UNet, ZSigmoida, liczba_parametrow
from .dane import paczka, wczytaj_npz, wczytaj_z_par
from .przetwarzanie import WEJSCIE, maska_z_prawdopodobienstwa

KATALOG_WAG = WAGI / "unet_termal"
KATALOG_WYNIKOW = WYNIKI / "unet_termal"


def strata(logity, y):
    bce = F.binary_cross_entropy_with_logits(logity, y)
    p = torch.sigmoid(logity)
    wsp = (p * y).sum(dim=(1, 2, 3))
    dice = (2 * wsp + 1) / (p.sum(dim=(1, 2, 3)) + y.sum(dim=(1, 2, 3)) + 1)
    return bce + (1 - dice).mean()


def dice_iou(a, b):
    a, b = a > 0, b > 0
    s, w = a.sum() + b.sum(), (a & b).sum()
    return (2 * w / s if s else float("nan")), (w / (a | b).sum() if s else float("nan"))


@torch.no_grad()
def przewiduj(model, zbior, idx, urz):
    """Prawdopodobienstwa (len(idx), 240, 320) dla obrazow bez augmentacji."""
    model.eval()
    wynik = []
    for i in idx:
        x, _ = paczka(zbior, [i])
        wynik.append(torch.sigmoid(model(torch.from_numpy(x).to(urz)))[0, 0].float().cpu().numpy())
    return np.array(wynik)


def trenuj(zbior, idx_tr, epoki, a, urz, ziarno, opis, idx_test=None, log_csv=None):
    torch.manual_seed(ziarno)
    rng = np.random.default_rng(ziarno)
    model = UNet().to(urz)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    na_epoke = int(np.ceil(len(idx_tr) / a.batch))
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epoki * na_epoke)
    wiersze = []
    t0 = time.time()
    for ep in range(1, epoki + 1):
        model.train()
        kolejnosc = rng.permutation(idx_tr)
        suma = 0.0
        for j in range(na_epoke):
            x, y = paczka(zbior, kolejnosc[j * a.batch:(j + 1) * a.batch], rng)
            x, y = torch.from_numpy(x).to(urz), torch.from_numpy(y).to(urz)
            loss = strata(model(x), y)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sched.step()
            suma += loss.item()
        w = {"epoka": ep, "strata": suma / na_epoke, "lr": sched.get_last_lr()[0], "czas_s": time.time() - t0}
        if idx_test is not None and len(idx_test) and (ep % 10 == 0 or ep == epoki):   # tylko podglad, bez wyboru epoki
            p = przewiduj(model, zbior, idx_test, urz)
            w["dice_test"] = float(np.mean([dice_iou(maska_z_prawdopodobienstwa(pi, pi.shape), zbior.maski[i])[0]
                                            for pi, i in zip(p, idx_test)]))
        wiersze.append(w)
        if ep == 1 or ep % 10 == 0 or ep == epoki:
            print(f"[{opis}] epoka {ep}/{epoki}  strata {w['strata']:.4f}"
                  + (f"  Dice test {w['dice_test']:.3f}" if "dice_test" in w else "")
                  + f"  ({w['czas_s']:.0f} s)", flush=True)
    if log_csv:
        klucze = sorted({k for w in wiersze for k in w}, key=["epoka", "strata", "dice_test", "lr", "czas_s"].index)
        with open(log_csv, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, klucze, delimiter=";")
            wr.writeheader()
            wr.writerows(wiersze)
    return model


def eksportuj(model, kat, nazwa, konfig):
    """<nazwa>.pth (wagi + konfiguracja) i <nazwa>.onnx (z sigmoida) + sprawdzenie w cv2.dnn."""
    model = model.cpu().eval()
    torch.save({"stan": model.state_dict(), "kanaly": model.kanaly, **konfig}, kat / f"{nazwa}.pth")
    x = torch.randn(1, 1, WEJSCIE[1], WEJSCIE[0])
    sciezka = kat / f"{nazwa}.onnx"
    kw = {"dynamo": False} if "dynamo" in inspect.signature(torch.onnx.export).parameters else {}
    eksport = ZSigmoida(model).eval()          # nowy modul jest w trybie treningu - BatchNorm musi byc w eval
    torch.onnx.export(eksport, x, str(sciezka), input_names=["obraz"], output_names=["prawdopodobienstwo"],
                      opset_version=13, do_constant_folding=True, **kw)
    net = cv2.dnn.readNetFromONNX(np.fromfile(str(sciezka), np.uint8))
    net.setInput(x.numpy())
    with torch.no_grad():
        roznica = float(np.abs(net.forward() - eksport.eval()(x).numpy()).max())
    print(f"  zapisano {sciezka.name} (cv2.dnn vs PyTorch: maks. roznica {roznica:.1e})")
    if roznica > 1e-3:
        raise RuntimeError(f"Model ONNX liczy inaczej niz PyTorch (roznica {roznica})")
    return roznica


def main():
    ap = argparse.ArgumentParser(description="Trening U-Netu: znacznik Π na termowizji (model M3)")
    ap.add_argument("--foldy", type=int, nargs="*", default=[1, 2, 3, 4, 5])
    ap.add_argument("--bez_koncowego", action="store_true", help="bez modelu na wszystkich parach")
    ap.add_argument("--epoki", type=int, default=60)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--ziarno", type=int, default=0)
    ap.add_argument("--npz", help="zbior z jednego pliku .npz zamiast dane/pary")
    ap.add_argument("--wagi", default=str(KATALOG_WAG))
    ap.add_argument("--wyniki", default=str(KATALOG_WYNIKOW))
    ap.add_argument("--urzadzenie", default="auto", help="auto / cpu / cuda")
    ap.add_argument("--proba", action="store_true", help="szybki test: 2 epoki, fold 1, bez modelu koncowego")
    a = ap.parse_args()
    if a.proba:
        a.epoki, a.foldy, a.bez_koncowego = 2, a.foldy[:1], True
    urz = torch.device("cuda" if a.urzadzenie == "auto" and torch.cuda.is_available() else
                       ("cpu" if a.urzadzenie == "auto" else a.urzadzenie))
    zbior = wczytaj_npz(a.npz) if a.npz else wczytaj_z_par()
    kat_w = Path(a.wagi)
    kat_w.mkdir(parents=True, exist_ok=True)
    kat_r = Path(a.wyniki) / f"trening_{datetime.now():%Y%m%d_%H%M%S}"
    kat_r.mkdir(parents=True, exist_ok=True)
    parametry = f"{liczba_parametrow(UNet()):,}".replace(",", " ")
    print(f"Pary: {len(zbior.pary)}, znamiona: {len(set(zbior.znamie.tolist()))}, "
          f"foldy: {sorted(set(zbior.fold.tolist()))}; urzadzenie: {urz}; parametry sieci: {parametry}")
    print(f"Wagi: {kat_w}\nWyniki: {kat_r}")
    konfig = {"epoki": a.epoki, "batch": a.batch, "lr": a.lr, "wejscie": list(WEJSCIE), "ziarno": a.ziarno}
    oof, foldy_info = [], {}
    for k in a.foldy:
        idx_tr, idx_te = np.where(zbior.fold != k)[0], np.where(zbior.fold == k)[0]
        print(f"\n=== Fold {k}: trening {len(idx_tr)} par, test {len(idx_te)} par "
              f"(znamiona {sorted(set(zbior.znamie[idx_te].tolist()))}) ===")
        t0 = time.time()
        model = trenuj(zbior, idx_tr, a.epoki, a, urz, a.ziarno + k, f"fold {k}", idx_te, kat_r / f"log_fold{k}.csv")
        p = przewiduj(model, zbior, idx_te, urz)
        dices = []
        for pi, i in zip(p, idx_te):
            d, j = dice_iou(maska_z_prawdopodobienstwa(pi, pi.shape), zbior.maski[i])
            dices.append(d)
            oof.append({"para": int(zbior.pary[i]), "znamie": int(zbior.znamie[i]), "fold": k,
                        "dice": round(float(d), 4), "iou": round(float(j), 4)})
        roznica = eksportuj(model, kat_w, f"fold{k}", {**konfig, "fold": k,
                                                       "pary_treningowe": zbior.pary[idx_tr].tolist()})
        foldy_info[k] = {"pary_testowe": zbior.pary[idx_te].tolist(), "dice_srednia": float(np.mean(dices)),
                         "dice_mediana": float(np.median(dices)), "czas_s": time.time() - t0, "onnx_roznica": roznica}
        print(f"Fold {k}: Dice test srednio {np.mean(dices):.3f}, mediana {np.median(dices):.3f}")
    if oof:
        with open(kat_r / "ocena_oof.csv", "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, ["para", "znamie", "fold", "dice", "iou"], delimiter=";")
            wr.writeheader()
            wr.writerows(sorted(oof, key=lambda r: r["para"]))
        d = np.array([r["dice"] for r in oof])
        print(f"\nWalidacja krzyzowa ({len(d)} par): Dice srednio {d.mean():.3f} ± {d.std():.3f}, "
              f"mediana {np.median(d):.3f}, min {d.min():.3f}")
    if not a.bez_koncowego:
        print(f"\n=== Model koncowy: wszystkie {len(zbior.pary)} pary ===")
        model = trenuj(zbior, np.arange(len(zbior.pary)), a.epoki, a, urz, a.ziarno, "wszystkie",
                       log_csv=kat_r / "log_wszystkie.csv")
        eksportuj(model, kat_w, "wszystkie", {**konfig, "fold": None, "pary_treningowe": zbior.pary.tolist()})
    (kat_r / "trening.json").write_text(json.dumps({
        "data": f"{datetime.now():%Y-%m-%d %H:%M}", "urzadzenie": str(urz), "torch": torch.__version__,
        "parametry": liczba_parametrow(UNet()), "konfiguracja": konfig, "foldy": foldy_info,
        "oof_dice_srednia": float(np.mean([r["dice"] for r in oof])) if oof else None,
        "wagi": str(kat_w)}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nGotowe: {kat_w}\nLogi i ocena: {kat_r}")


if __name__ == "__main__":
    main()
