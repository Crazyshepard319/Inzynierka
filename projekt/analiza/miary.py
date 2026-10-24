"""
Miary zgodnosci dwoch obszarow (masek bool w tej samej siatce) i dwoch zestawow punktow.

    Dice  = 2|A∩B| / (|A| + |B|)          pokrycie, 0..1
    IoU   = |A∩B| / |A∪B|                 pokrycie (surowsze), 0..1
    HD95  = max(P95 d(A->B), P95 d(B->A)) odleglosc konturow w najgorszych miejscach, bez 5% skrajnych
    ASSD  = srednia wszystkich odleglosci konturow A->B i B->A
    przesuniecie srodkow, stosunek pol |A|/|B|
    TRE   = odleglosc odpowiadajacych sobie punktow (naroznikow) po rejestracji
Odleglosci w pikselach siatki; `mm_na_px` (rozmiar piksela tej siatki w mm) przelicza je na mm.
"""
import cv2
import numpy as np


def _brzeg(m):
    m8 = m.astype(np.uint8)
    return m & ~(cv2.erode(m8, np.ones((3, 3), np.uint8)) > 0)


def _odleglosci(a, b):
    """Odleglosci pikseli brzegu A do brzegu B i odwrotnie (transformata odleglosci)."""
    ba, bb = _brzeg(a), _brzeg(b)
    dt_b = cv2.distanceTransform((~bb).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    dt_a = cv2.distanceTransform((~ba).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    return dt_b[ba], dt_a[bb]


def zgodnosc_masek(a, b, mm_na_px=1.0):
    """Slownik miar dla masek bool A (np. przeniesiona z RGB) i B (wyznaczona w termowizji)."""
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    pa, pb, wsp = int(a.sum()), int(b.sum()), int((a & b).sum())
    suma = int((a | b).sum())
    wynik = {"dice": 2 * wsp / (pa + pb) if pa + pb else float("nan"),
             "iou": wsp / suma if suma else float("nan"),
             "stosunek_pol": pa / pb if pb else float("nan")}
    if pa and pb:
        dab, dba = _odleglosci(a, b)
        wynik["hd95_mm"] = float(max(np.percentile(dab, 95), np.percentile(dba, 95))) * mm_na_px
        wynik["assd_mm"] = float((dab.sum() + dba.sum()) / (len(dab) + len(dba))) * mm_na_px
        ca = np.argwhere(a).mean(0)
        cb = np.argwhere(b).mean(0)
        wynik["przesuniecie_srodkow_mm"] = float(np.hypot(*(ca - cb))) * mm_na_px
    return wynik


def tre(pkt_a, pkt_b, H_mm=None):
    """Bledy polozenia odpowiadajacych sobie punktow. H_mm: homografia px -> mm siatki punktow
    (odleglosc liczona w mm na plaszczyznie znacznika); None = w pikselach."""
    a, b = np.asarray(pkt_a, np.float64), np.asarray(pkt_b, np.float64)
    if H_mm is not None:
        a = cv2.perspectiveTransform(a[None], np.asarray(H_mm, np.float64))[0]
        b = cv2.perspectiveTransform(b[None], np.asarray(H_mm, np.float64))[0]
    d = np.hypot(*(a - b).T)
    return {"tre_srednie": float(d.mean()), "tre_max": float(d.max()), "tre_punkty": d.round(3).tolist()}
