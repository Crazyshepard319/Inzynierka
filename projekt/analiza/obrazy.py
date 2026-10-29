"""
Obrazy do raportu pary (BGR, uint8):
    rgb                 zdjecie wokol znacznika: znacznik i narozniki, znamie
    termal              termowizja 3x: znacznik oznaczony na termowizji i przeniesiony ze zdjecia, znamie
    nakladka            termowizja nalozona na zdjecie (50 %) z obrysami znacznika i znamienia
    nakladka_zblizenie  to samo w powiekszeniu wokol znamienia; termowizja bez wygladzania, wiec widac
                        jej piksele, i podzialka w mm
    znacznik_modalnosci badanie E2: maska znacznika ze zdjecia przeniesiona przez T i maska z U-Netu na
                        termowizji (siatka 4x), z otworami (ROI) obu masek
    piksele_termal      piksele termowizji objete znamieniem: surowa intensywnosc z nagrania .SEQ, siatka
                        pikseli kamery, piksele w masce i wspolrzedne x, y (gdy jest nagranie)
Znamie z segmentacji (PanDerm) - czerwone; gdy para ma adnotacje z CVAT, znamie z CVAT - niebieskie (cienkie).
"""
import cv2
import numpy as np

from . import geometria as geo

ZIELONY, CZERWONY, FIOLET = (0, 200, 0), (0, 0, 255), (255, 0, 255)
NIEBIESKI, BIALY, CZARNY = (255, 160, 0), (255, 255, 255), (0, 0, 0)
TURKUS = (255, 229, 0)      # maska znacznika z U-Netu (termowizja) - kontrastuje z paleta inferno
ZOLTY = (0, 220, 255)       # piksele termowizji w masce znamienia


def napis(img, tekst, xy, skala=0.6):
    for kol, g in ((CZARNY, 4), (BIALY, 1)):
        cv2.putText(img, tekst, (int(xy[0]), int(xy[1])), cv2.FONT_HERSHEY_SIMPLEX, skala, kol, g, cv2.LINE_AA)


def brzegi(maska):
    """Wszystkie brzegi maski (zewnetrzne i wewnetrzne)."""
    ks, _ = cv2.findContours(np.asarray(maska).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return [k[:, 0, :].astype(np.float64) for k in ks if len(k) >= 3]


def ramka(pkt, ksztalt, margines=0.25, min_bok=0):
    """Prostokat (x0, y0, x1, y1) wokol punktow z marginesem, przyciety do obrazu."""
    pkt = np.asarray(pkt, np.float64).reshape(-1, 2)
    (x0, y0), (x1, y1) = pkt.min(0), pkt.max(0)
    m = max(margines * max(x1 - x0, y1 - y0), (min_bok - max(x1 - x0, y1 - y0)) / 2, 0)
    return (int(max(0, x0 - m)), int(max(0, y0 - m)),
            int(min(ksztalt[1], x1 + m)), int(min(ksztalt[0], y1 + m)))


def _linie(img, wielokaty, przelicz, kolor, grubosc, zamkniete=True):
    for w in wielokaty:
        cv2.polylines(img, [np.round(przelicz(w)).astype(np.int32)], zamkniete, kolor, grubosc, cv2.LINE_AA)


def nalozenie_kadru(a, rk, szer, alfa=0.5, interpolacja=cv2.INTER_LINEAR):
    """Kadr zdjecia rk = (x0, y0, x1, y1) przeskalowany do szerokosci szer z nalozona termowizja.
    Termowizja jest probkowana wprost dla pikseli kadru (wyjscie -> zdjecie -> T -> termowizja),
    bez przeksztalcania calego zdjecia. Zwraca (obraz, funkcja px zdjecia -> px kadru)."""
    x0, y0, x1, y1 = rk
    z = szer / max(1, x1 - x0)
    wh = (szer, max(1, int(round((y1 - y0) * z))))
    kadr = cv2.resize(a.rgb[y0:y1, x0:x1], wh, interpolation=cv2.INTER_AREA if z < 1 else cv2.INTER_LINEAR)
    wyj_do_rgb = np.array([[1 / z, 0, x0 + 0.5 / z - 0.5], [0, 1 / z, y0 + 0.5 / z - 0.5], [0, 0, 1]])
    wyj_do_t = np.asarray(a.M, np.float64) @ wyj_do_rgb
    ter = cv2.warpPerspective(a.termal, wyj_do_t, wh, flags=interpolacja | cv2.WARP_INVERSE_MAP)
    pole = cv2.warpPerspective(np.full(a.termal.shape[:2], 255, np.uint8), wyj_do_t, wh,
                               flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP) > 127
    wynik = kadr.copy()
    wynik[pole] = (alfa * kadr[pole] + (1 - alfa) * ter[pole]).astype(np.uint8)
    return wynik, (lambda p: (np.asarray(p, np.float64) - [x0, y0] + 0.5) * z - 0.5)


def _znacznik_termowizji_na_zdjeciu(a):
    """Narozniki znacznika oznaczone na termowizji (CVAT albo automatycznie) przeniesione przez T^-1."""
    nar = a.wzorzec["narozniki_termal"] if a.wzorzec is not None else a.narozniki_termal
    return None if nar is None else geo.przenies_punkty(nar, np.linalg.inv(a.M))


def _podzialka(img, mm_na_px_wyj, dlugosc_mm=None):
    """Podzialka w lewym dolnym rogu; mm_na_px_wyj: mm na piksel obrazu wyjsciowego."""
    if dlugosc_mm is None:
        cel = 0.25 * img.shape[1] * mm_na_px_wyj
        dlugosc_mm = max((d for d in (0.5, 1, 2, 5, 10) if d <= cel), default=0.5)
    dl = int(round(dlugosc_mm / mm_na_px_wyj))
    x, y = 16, img.shape[0] - 18
    cv2.line(img, (x, y), (x + dl, y), CZARNY, 7)
    cv2.line(img, (x, y), (x + dl, y), BIALY, 3)
    napis(img, f"{dlugosc_mm:g} mm", (x, y - 10), 0.6)


def rysuj(a):
    """a: system.Analiza po etapie pomiarow. Zwraca slownik nazwa -> obraz BGR."""
    ob = {}
    pr = a.przeniesione
    kontury_rgb = geo.kontury(a.maska_znamie)
    kontury_cvat = geo.kontury(a.wzorzec["maska_znamie_rgb"]) if a.wzorzec is not None else []

    # 1. zdjecie: kadr wokol znacznika
    x0, y0, x1, y1 = ramka(a.narozniki_rgb, a.rgb.shape)
    sk = 700 / max(1, x1 - x0)
    k = cv2.resize(a.rgb[y0:y1, x0:x1], None, fx=sk, fy=sk, interpolation=cv2.INTER_AREA)
    tr = lambda p: (np.asarray(p, np.float64) - [x0, y0]) * sk
    _linie(k, [a.narozniki_rgb], tr, ZIELONY, 2)
    _linie(k, kontury_cvat, tr, NIEBIESKI, 1)
    _linie(k, kontury_rgb, tr, CZERWONY, 2)
    for i, q in enumerate(tr(a.narozniki_rgb)):
        cv2.circle(k, (int(q[0]), int(q[1])), 5, ZIELONY, -1, cv2.LINE_AA)
        napis(k, str(i), (q[0] + 7, q[1] - 7))
    ob["rgb"] = k

    # 2. termowizja 3x
    z = 3
    t = cv2.resize(a.termal, None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC)
    d = lambda p: (np.asarray(p, np.float64) + 0.5) * z - 0.5
    nar_ref = a.wzorzec["narozniki_termal"] if a.wzorzec is not None else a.narozniki_termal
    if nar_ref is not None:
        _linie(t, [nar_ref], d, FIOLET, 2)
    if a.maska_znacznika_termal_unet is not None:
        _linie(t, brzegi(a.maska_znacznika_termal_unet > 0), d, TURKUS, 3)
    _linie(t, [pr["narozniki"]], d, ZIELONY, 2)
    _linie(t, [(kk + 0.5) / 4 - 0.5 for kk in geo.kontury(pr["znamie_gesta"].astype(np.uint8))], d, CZERWONY, 2)
    if a.wzorzec is not None:              # blad rejestracji: narozniki z CVAT (zdjecie -> T) vs z CVAT na termowizji
        nar_cvat_T = geo.przenies_punkty(a.wzorzec["narozniki_rgb"], a.M)
        for p, q in zip(d(nar_cvat_T), d(a.wzorzec["narozniki_termal"])):
            cv2.line(t, (int(round(p[0])), int(round(p[1]))), (int(round(q[0])), int(round(q[1]))), BIALY, 2, cv2.LINE_AA)
    ob["termal"] = t

    # 3. nalozenie: kadr wokol znacznika, termowizja 50 %
    nal, tr = nalozenie_kadru(a, ramka(a.narozniki_rgb, a.rgb.shape), 900)
    _linie(nal, [a.narozniki_rgb], tr, ZIELONY, 2)
    zt = _znacznik_termowizji_na_zdjeciu(a)
    if zt is not None:
        _linie(nal, [zt], tr, FIOLET, 2)
    _linie(nal, kontury_rgb, tr, CZERWONY, 3)
    ob["nakladka"] = nal

    # 4. zblizenie wokol znamienia: termowizja bez wygladzania (widac jej piksele), podzialka
    s = a.wyniki["pomiary_rgb"]["mm_na_px"]
    bok_mm = max(8.0, 2.2 * a.wyniki["pomiary_rgb"]["feret_max_mm"])
    srodek = np.argwhere(a.maska_znamie > 0).mean(0)[::-1]
    rk = ramka(srodek, a.rgb.shape, 0, bok_mm / s)
    nal, tr = nalozenie_kadru(a, rk, 600, interpolacja=cv2.INTER_NEAREST)
    _linie(nal, kontury_cvat, tr, NIEBIESKI, 1)
    _linie(nal, kontury_rgb, tr, CZERWONY, 2)
    _podzialka(nal, s * (rk[2] - rk[0]) / 600)
    ob["nakladka_zblizenie"] = nal
    if getattr(a, "_maski_e2", None) is not None:
        ob["znacznik_modalnosci"] = obraz_e2(a)
    if getattr(a, "piksele", None) is not None and len(a.piksele["x"]):
        ob["piksele_termal"] = obraz_pikseli(a)
    return ob


def obraz_pikseli(a, szer=600, margines=3):
    """Kadr termowizji wokol znamienia: surowa intensywnosc (szarosci rozciagniete na zakres kadru), kazdy piksel
    kamery jako kwadrat z siatka; zolte ramki - piksele w masce (pokrycie >= 50 %), czerwona linia - znamie
    przeniesione ze zdjecia; na brzegach wspolrzedne x (kolumna) i y (wiersz) pikseli."""
    pk, I = a.piksele, a.intensywnosc
    h, w = I.shape
    x0, x1 = max(0, int(pk["x"].min()) - margines), min(w, int(pk["x"].max()) + margines + 1)
    y0, y1 = max(0, int(pk["y"].min()) - margines), min(h, int(pk["y"].max()) + margines + 1)
    kadr = I[y0:y1, x0:x1].astype(np.float64)
    lo, hi = float(kadr.min()), float(kadr.max())
    g = np.round((kadr - lo) / max(hi - lo, 1.0) * 255).astype(np.uint8)
    z = max(8, szer // (x1 - x0))                                     # piksele obrazu na piksel kamery
    img = cv2.cvtColor(cv2.resize(g, None, fx=z, fy=z, interpolation=cv2.INTER_NEAREST), cv2.COLOR_GRAY2BGR)
    for i in range(x1 - x0 + 1):
        cv2.line(img, (min(i * z, img.shape[1] - 1), 0), (min(i * z, img.shape[1] - 1), img.shape[0] - 1), (110, 110, 110), 1)
    for j in range(y1 - y0 + 1):
        cv2.line(img, (0, min(j * z, img.shape[0] - 1)), (img.shape[1] - 1, min(j * z, img.shape[0] - 1)), (110, 110, 110), 1)
    gr = max(1, z // 12)
    for x, y, m in zip(pk["x"].tolist(), pk["y"].tolist(), pk["w_masce"].tolist()):
        if m:
            cv2.rectangle(img, ((x - x0) * z + 2 * gr, (y - y0) * z + 2 * gr),
                          ((x - x0 + 1) * z - 2 * gr - 1, (y - y0 + 1) * z - 2 * gr - 1), ZOLTY, gr)
    d = lambda p: ((np.asarray(p, np.float64) + 0.5) / 4 - 0.5 - [x0, y0] + 0.5) * z     # siatka 4x -> kadr
    _linie(img, geo.kontury(a.przeniesione["znamie_gesta"].astype(np.uint8)), d, CZERWONY, max(2, z // 10))
    # brzegi z opisami: x u gory, y z lewej, zakres intensywnosci na dole
    gora, lewa, dol = 26, 46, 30
    img = cv2.copyMakeBorder(img, gora, dol, lewa, 8, cv2.BORDER_CONSTANT, value=BIALY)
    co = int(np.ceil(34 / z))                                         # co ile pikseli podpis
    for i in range(0, x1 - x0, co):
        t = str(x0 + i)
        (tw, _), _ = cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.putText(img, t, (lewa + i * z + (z - tw) // 2, gora - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.42, CZARNY, 1, cv2.LINE_AA)
    for j in range(0, y1 - y0, co):
        t = str(y0 + j)
        (tw, th), _ = cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.putText(img, t, (lewa - tw - 6, gora + j * z + (z + th) // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.42, CZARNY, 1, cv2.LINE_AA)
    cv2.putText(img, "x", (lewa - 16, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, CZARNY, 1, cv2.LINE_AA)
    cv2.putText(img, "y", (6, gora + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, CZARNY, 1, cv2.LINE_AA)
    st = (a.wyniki or {}).get("piksele_termal") or {}
    opis = (f"intensywnosc surowa: czarny {lo:.0f}, bialy {hi:.0f}; w masce {st.get('piksele_w_masce', '-')} px, "
            f"mediana {st.get('intensywnosc_mediana', float('nan')):.0f}")
    cv2.putText(img, opis, (lewa, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, CZARNY, 1, cv2.LINE_AA)
    return img


def obraz_e2(a, szer=800):
    """Termowizja w siatce 4x wokol znacznika: maska ze zdjecia (przez T) i z U-Netu, kolorami wg pokrycia."""
    A, B, wa, wb = a._maski_e2
    g = A.shape[0] // a.termal.shape[0]
    t = cv2.resize(a.termal, (A.shape[1], A.shape[0]), interpolation=cv2.INTER_CUBIC)
    t = (0.55 * t).astype(np.uint8)
    for maska, kolor in ((A & B, BIALY), (A & ~B, ZIELONY), (B & ~A, TURKUS)):
        t[maska] = (0.45 * t[maska] + 0.55 * np.array(kolor)).astype(np.uint8)
    _linie(t, brzegi(wa), lambda p: p, ZIELONY, max(1, g // 2))          # otwor maski ze zdjecia
    _linie(t, brzegi(B), lambda p: p, TURKUS, g)                         # obrys folii z U-Netu
    _linie(t, brzegi(wb), lambda p: p, TURKUS, g)                        # otwor maski z U-Netu
    y, x = np.nonzero(A | B)
    x0, y0, x1, y1 = ramka(np.c_[x, y], t.shape, 0.15)
    k = t[y0:y1, x0:x1]
    k = cv2.resize(k, (szer, max(1, int(round(k.shape[0] * szer / max(1, k.shape[1]))))), interpolation=cv2.INTER_NEAREST)
    e2 = (a.wyniki or {}).get("zgodnosc_modalnosci") or {}
    if e2:
        tekst = f"E2: Dice folii {e2['obrys']['dice']:.3f}, Dice otworu {e2['otwor']['dice']:.3f}"
        (tw, th), _ = cv2.getTextSize(tekst, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(k, (6, 6), (18 + tw, 20 + th), CZARNY, -1)
        cv2.putText(k, tekst, (12, 12 + th), cv2.FONT_HERSHEY_SIMPLEX, 0.7, BIALY, 2, cv2.LINE_AA)
    return k
