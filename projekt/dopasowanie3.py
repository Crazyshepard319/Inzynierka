"""
Rejestracja multimodalna: RGB <-> termal (wersja 3)
Eksportuje: run_registration(rgb_path, ter_path, out_path, model=MODEL)

Idea: transformacje wyznacza sam znacznik Π (folia 35 x 26 mm, pasek 9 mm), a nie cala scena.
  1. Termal: kandydaci = obszary ciemniejsze od skory albo teksturowane (odbicia w folii); wybierany
     jest najbardziej podobny ksztaltem do wzorca Π; krawedz z lokalnego progu (polowa drogi
     miedzy folia a skora).
  2. RGB: kandydaci = obszary chlodniejsze w barwie od skory (a* + b* w Lab) i/lub teksturowane
     (zalamania folii), po zamknieciu i otwarciu roznej wielkosci; wybierany jest najbardziej podobny
     ksztaltem do wzorca Π; krawedz poprawia GrabCut. Na 94 parach z 23.10 maska zgadza sie z
     adnotacja z CVAT na ~90 parach (IoU >= 0,85); zgodnosc z wzorcem < 0,65 = ostrzezenie.
  3. Wstepne podobienstwo (srodek masy, skala z pol, kat z przeszukania 360 st.).
  4. Doprecyzowanie ECC (cv2.findTransformECC) na maskach znacznikow:
     afiniczna, opcjonalnie homografia (tylko gdy jest stabilna).
"""

import cv2
import numpy as np
from pathlib import Path


RGB_DET_PX = 1000     # dluzszy bok obrazu RGB, na ktorym odbywa sie detekcja i dopasowanie
MODEL = 'auto'        # 'afiniczna' | 'homografia' | 'auto' (homografia tylko gdy stabilna)
# Odbicie lustrzane termowizji: znacznik Π jest symetryczny wzgledem osi, wiec odbicie pasuje rownie dobrze
# i zamienia ramiona miejscami (blad ~25 mm na parach 10, 55, 72). Kamera nie odwraca obrazu - wylaczone.
SPRAWDZ_LUSTRO = False


# ── Funkcje pomocnicze ───────────────────────────────────────────────────────

def _kolo(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r + 1, 2*r + 1))


def _h3(M):
    return np.vstack([M, [0, 0, 1]]) if M.shape[0] == 2 else M


def _przesun(tx, ty):
    return np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], dtype=float)


def imread(sciezka, flagi=cv2.IMREAD_COLOR):
    """cv2.imread, ktory dziala tez ze sciezkami z polskimi znakami (Windows)."""
    try:
        dane = np.fromfile(str(sciezka), dtype=np.uint8)
    except OSError:
        return None
    return cv2.imdecode(dane, flagi) if dane.size else None


def imwrite(sciezka, img):
    """cv2.imwrite, ktory dziala tez ze sciezkami z polskimi znakami (Windows)."""
    ok, buf = cv2.imencode(Path(sciezka).suffix or '.png', img)
    if ok:
        buf.tofile(str(sciezka))
    return ok


def nalozenie(rgb, ter_bgra, przezroczystosc):
    """Termal (BGRA, kanal alfa = pole widzenia kamery) nalozony na RGB.
    przezroczystosc: 0 = widac tylko termal, 1 = widac tylko RGB."""
    if ter_bgra.shape[2] == 4:
        pokrycie = ter_bgra[:, :, 3:4].astype(np.float32) / 255
    else:
        pokrycie = (ter_bgra.max(axis=2, keepdims=True) > 0).astype(np.float32)
    a = (1.0 - przezroczystosc) * pokrycie
    wynik = rgb.astype(np.float32) * (1 - a) + ter_bgra[:, :, :3].astype(np.float32) * a
    return np.clip(wynik + 0.5, 0, 255).astype(np.uint8)


def wypelnij_dziury(maska, max_udzial):
    """Wypelnia dziury mniejsze niz max_udzial * pole obiektu."""
    m = maska.copy()
    H, W = m.shape
    pole = cv2.countNonZero(m)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.bitwise_not(m), connectivity=4)
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if x == 0 or y == 0 or x + w == W or y + h == H:
            continue
        if a < max_udzial * pole:
            m[lab == j] = 255
    return m


def udzial_dziur(maska):
    pelna = wypelnij_dziury(maska, 1e9)
    return 1.0 - cv2.countNonZero(maska) / max(1, cv2.countNonZero(pelna))


def srodek_pole(maska):
    M = cv2.moments(maska, binaryImage=True)
    return np.array([M['m10'] / M['m00'], M['m01'] / M['m00']]), M['m00']


def _rho(maska):
    """Promien obejmujacy liczony od srodka masy, w jednostkach sqrt(pola)."""
    ys, xs = np.nonzero(maska)
    cx, cy = xs.mean(), ys.mean()
    return np.sqrt(((xs - cx)**2 + (ys - cy)**2).max() / len(xs)), (cx, cy), len(xs)


def _normalizuj(maska, sz, rho):
    """Maska wysrodkowana (srodek masy) i przeskalowana do jednakowego pola;
    rho dobrane tak, by wydluzone ksztalty miescily sie w kanwie."""
    _, (cx, cy), a = _rho(maska)
    s = 0.45 * sz / rho / np.sqrt(a)
    M = np.array([[s, 0, sz/2 - s*cx], [0, s, sz/2 - s*cy]])
    return cv2.warpAffine(maska, M, (sz, sz),
                          flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)


def krzywa_iou(ref, mov, katy, sz=128):
    """IoU(ref, obrot(mov, kat)) dla kazdego kata [stopnie, konwencja OpenCV CCW]."""
    rho = max(_rho(ref)[0], _rho(mov)[0])
    a = _normalizuj(ref, sz, rho) > 127
    b = _normalizuj(mov, sz, rho)
    out = np.empty(len(katy))
    for i, k in enumerate(katy):
        R = cv2.getRotationMatrix2D((sz/2, sz/2), float(k), 1.0)
        bb = cv2.warpAffine(b, R, (sz, sz)) > 127
        out[i] = np.count_nonzero(a & bb) / max(1, np.count_nonzero(a | bb))
    return out


# ── Wzorzec znacznika ────────────────────────────────────────────────────────
# Znacznik Π z folii: belka 35 mm, ramiona 26 mm, pasek 9 mm; narozniki w tej samej kolejnosci
# co w import_cvat.py. Kandydat na znacznik jest wybierany wedlug podobienstwa ksztaltu do tego wzorca
# (osobno w kazdej modalnosci - blad detekcji w jednej nie psuje drugiej).
BELKA, RAMIE, PASEK = 35.0, 26.0, 9.0
WZORZEC_MM = np.array([[0, 0], [BELKA, 0], [BELKA, RAMIE], [BELKA - PASEK, RAMIE], [BELKA - PASEK, PASEK],
                       [PASEK, PASEK], [PASEK, RAMIE], [0, RAMIE]], np.float64)
MIN_ZGODNOSC = 0.65   # IoU ksztaltu z wzorcem; ponizej detekcja jest niepewna (na 94 parach poprawne >= 0,68)
_KATY = np.arange(0, 360, 4)


def maska_wzorca(px_na_mm=4.0):
    """Maska wzorca Π (uint8 0/255) w skali px_na_mm, z marginesem 5 mm."""
    m = int(round(5 * px_na_mm))
    t = np.zeros((int(RAMIE * px_na_mm) + 2 * m, int(BELKA * px_na_mm) + 2 * m), np.uint8)
    cv2.fillPoly(t, [np.round((WZORZEC_MM * px_na_mm + m) * 16).astype(np.int32)], 255, cv2.LINE_8, 4)
    return t


_WZORZEC = maska_wzorca()


def zgodnosc_z_wzorcem(maska):
    """IoU ksztaltu maski z wzorcem Π po najlepszym obrocie (srodki mas i pola wyrownane)."""
    return float(krzywa_iou(_WZORZEC, maska, _KATY, sz=96).max())


def _najlepszy(kandydaci, najl=None):
    """kandydaci: (maska, opis); zwraca (zgodnosc z wzorcem, opis, maska) najlepszego."""
    for m, opis in kandydaci:
        z = zgodnosc_z_wzorcem(m)
        if najl is None or z > najl[0]:
            najl = (z, opis, m)
    return najl


# ── Detekcja: termal ─────────────────────────────────────────────────────────

def wczytaj_termal(sciezka):
    """Obraz termalny jako skalar float 0..255 (paleta 8-bit lub surowe 16-bit)."""
    img = imread(sciezka, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Nie mozna otworzyc: {sciezka}")
    if img.ndim == 3:
        kolor = img[:, :, :3]
        g = cv2.cvtColor(kolor, cv2.COLOR_BGR2GRAY).astype(np.float32)
    else:
        g = img.astype(np.float32)
        g = (g - g.min()) / max(1e-6, g.max() - g.min()) * 255
        kolor = cv2.applyColorMap(g.astype(np.uint8), cv2.COLORMAP_INFERNO)
    return g, kolor


def _kandydaci_termal(binarna, min_pole, opis):
    m = cv2.morphologyEx(binarna.astype(np.uint8) * 255, cv2.MORPH_OPEN, _kolo(2))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, _kolo(2), iterations=2)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    return [(wypelnij_dziury((lab == j).astype(np.uint8) * 255, 0.03), opis)
            for j in range(1, n) if st[j, cv2.CC_STAT_AREA] >= min_pole]


def wykryj_znacznik_termal(sciezka):
    """
    Znacznik na termowizji. Folia odbija otoczenie: jest ciemniejsza od skory (zimne odbicia) albo
    ma silna teksture (cieple i zimne odbicia obok siebie), a skora jest gladka. Kandydaci:
    "ciemne" oraz "ciemne lub teksturowane" przy kilku progach; wybierany jest kandydat najbardziej
    podobny ksztaltem do wzorca Π. Krawedz rozmyta przez optyke: w pasie +-4 px prog w pol drogi
    miedzy folia przy krawedzi a skora wokol.
    Zwraca dict: maska (uint8), miekka (float 0..1, krawedz subpikselowa z intensywnosci),
    kolor (obraz BGR), zgodnosc (IoU ksztaltu z wzorcem).
    """
    g, kolor = wczytaj_termal(sciezka)
    H, W = g.shape
    gb = cv2.GaussianBlur(g, (0, 0), 1.0)
    mu = cv2.blur(gb, (5, 5))
    sd = np.sqrt(np.maximum(cv2.blur(gb * gb, (5, 5)) - mu * mu, 0))
    skora = float(np.percentile(gb, 70))
    min_pole = 0.003 * H * W
    najl = None
    for fd in (0.5, 0.65, 0.8):
        ciemne = gb < fd * skora
        najl = _najlepszy(_kandydaci_termal(ciemne, min_pole, f"ciemne < {fd} skory"), najl)
        for ts in (6, 10, 15):
            najl = _najlepszy(_kandydaci_termal(ciemne | (sd > ts), min_pole,
                                                f"ciemne < {fd} skory lub tekstura > {ts}"), najl)
    if najl is None:
        raise RuntimeError("[termal] Nie znaleziono znacznika")
    zgodnosc, opis, sk = najl

    # krawedz: wnetrze kandydata (bez pasa 4 px) + piksele pasa ciemniejsze niz polowa drogi folia-skora
    r = 4
    wn = cv2.erode(sk, _kolo(r))
    zew = cv2.subtract(cv2.dilate(sk, _kolo(r + 3)), cv2.dilate(sk, _kolo(r)))
    pas = cv2.subtract(cv2.dilate(sk, _kolo(r)), wn) > 0
    brzeg_wn = cv2.subtract(wn, cv2.erode(wn, _kolo(2))) > 0
    v_out = float(np.median(gb[zew > 0]))
    v_in = float(np.percentile(gb[brzeg_wn], 30)) if brzeg_wn.any() else float(np.median(gb[sk > 0]))
    prog = 0.5 * (v_in + v_out)
    m = ((wn > 0) | (pas & (gb < prog))).astype(np.uint8) * 255
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n > 1:
        m = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8) * 255
    maska = wypelnij_dziury(m, 0.05)

    # miekka maska: w pasie +-2 px wokol krawedzi wartosc z intensywnosci
    miekka = np.clip((v_out - g) / max(1e-3, v_out - v_in), 0, 1)
    pas2 = cv2.subtract(cv2.dilate(maska, _kolo(2)), cv2.erode(maska, _kolo(2))) > 0
    miekka = np.where(pas2, miekka, (maska > 0)).astype(np.float32)

    c, pole = srodek_pole(maska)
    print(f"  [termal] srodek=({c[0]:.1f},{c[1]:.1f})  promien rown.={np.sqrt(pole/np.pi):.1f}px  "
          f"zgodnosc z wzorcem Pi={zgodnosc:.3f}  kryterium: {opis}  prog krawedzi={prog:.0f} "
          f"(folia {v_in:.0f} / skora {v_out:.0f})  obraz={W}x{H}")
    if zgodnosc < MIN_ZGODNOSC:
        print("  OSTRZEZENIE [termal] znacznik wykryty niepewnie - sprawdz _debug_termal.png")
    return dict(maska=maska, miekka=miekka, kolor=kolor, zgodnosc=zgodnosc)


# ── Detekcja: RGB ────────────────────────────────────────────────────────────

def _kandydaci_rgb(binarna, k_r, min_pole, opis):
    """Skladowe po zamknieciu (sklejenie przerw i zalaman folii) i otwarciu roznej wielkosci
    (odciecie wlosow i waskich polaczen z tlem); bez skladowych dotykajacych brzegu zdjecia."""
    out = []
    H, W = binarna.shape
    b = binarna.astype(np.uint8) * 255
    for rc, ro in ((1, 1), (2, 2), (2, 4), (3, 7)):
        m = cv2.morphologyEx(b, cv2.MORPH_CLOSE, _kolo(rc * k_r))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, _kolo(ro * k_r))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        for j in range(1, n):
            x, y, w, h, a = st[j]
            if a < min_pole or x == 0 or y == 0 or x + w == W or y + h == H:
                continue
            out.append((wypelnij_dziury((lab == j).astype(np.uint8) * 255, 0.03), f"{opis}, morfologia {rc}/{ro}"))
    return out


def _grabcut(im, m, powieksz=0.5, iteracje=4):
    """Krawedz folii metoda GrabCut: kolory folii z kandydata, skory z jego otoczenia
    (liczone tylko w prostokacie wokol kandydata)."""
    r = max(5, int(powieksz * np.sqrt(cv2.countNonZero(m))))
    obszar = cv2.dilate(m, _kolo(r))
    x, y, w, h = cv2.boundingRect(obszar)
    x0, y0 = max(0, x - 2), max(0, y - 2)
    x1, y1 = min(m.shape[1], x + w + 2), min(m.shape[0], y + h + 2)
    gc = np.full((y1 - y0, x1 - x0), cv2.GC_BGD, np.uint8)
    gc[obszar[y0:y1, x0:x1] > 0] = cv2.GC_PR_BGD
    gc[m[y0:y1, x0:x1] > 0] = cv2.GC_PR_FGD
    bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(np.ascontiguousarray(im[y0:y1, x0:x1]), gc, None, bg, fg, iteracje, cv2.GC_INIT_WITH_MASK)
    except cv2.error:
        return None
    w_ = ((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8) * 255
    n, lab, st, _ = cv2.connectedComponentsWithStats(w_, connectivity=8)
    if n < 2:
        return None
    wynik = np.zeros_like(m)
    wynik[y0:y1, x0:x1] = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8) * 255
    return wypelnij_dziury(wynik, 0.03)


def wykryj_folie_rgb(img):
    """
    Folia znacznika na zdjeciu (BGR). Folia jest chlodniejsza w barwie od skory (mniej czerwieni
    i zolci: a* + b* w Lab, wzgledem mediany skory na tym zdjeciu) i ma teksture (zalamania).
    Kandydaci z trzech map: chlod barwy, tekstura, chlod i tekstura w poblizu, przy kilku progach;
    wybierany jest kandydat najbardziej podobny ksztaltem do wzorca Π. Krawedz poprawia GrabCut,
    jesli nie psuje ksztaltu.
    Zwraca dict: maska (skala robocza), sc (skala robocza), im (obraz roboczy), zgodnosc, opis.
    """
    H0, W0 = img.shape[:2]
    sc = min(1.0, RGB_DET_PX / max(H0, W0))
    im = cv2.resize(img, (int(round(W0 * sc)), int(round(H0 * sc))), interpolation=cv2.INTER_AREA)
    H, W = im.shape[:2]
    k_r = max(2, min(H, W) // 250)
    min_pole = 0.01 * H * W
    lab = cv2.cvtColor(cv2.GaussianBlur(im, (0, 0), 1.5), cv2.COLOR_BGR2LAB).astype(np.float32)
    L, cieplo = lab[..., 0], (lab[..., 1] - 128) + (lab[..., 2] - 128)
    jasne = L > np.percentile(L, 20)                       # bez wlosow i cieni
    c_sk = float(np.median(cieplo[jasne]))
    chlod = (c_sk - cieplo) / (float(np.percentile(np.abs(cieplo[jasne] - c_sk), 50)) + 1.0)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    mu = cv2.blur(g, (7, 7))
    sd = np.sqrt(np.maximum(cv2.blur(g * g, (7, 7)) - mu * mu, 0))
    sd_sk = float(np.median(sd))
    sd_blisko = cv2.dilate(sd, _kolo(4 * k_r))             # gladkie plamy folii tez lezą blisko zalaman
    najl = None
    for t in (1.5, 2.0, 3.0, 4.0, 5.5, 7.5):
        najl = _najlepszy(_kandydaci_rgb(chlod > t, k_r, min_pole, f"chlodniejsze od skory > {t}"), najl)
    for f in (2.0, 3.0, 4.5):
        najl = _najlepszy(_kandydaci_rgb(sd > f * sd_sk, k_r, min_pole, f"tekstura > {f} x mediana"), najl)
    for t in (1.0, 1.5, 2.0, 3.0):
        for f in (1.5, 2.5):
            najl = _najlepszy(_kandydaci_rgb((chlod > t) & (sd_blisko > f * sd_sk), k_r, min_pole,
                                             f"chlodniejsze > {t} i tekstura > {f}"), najl)
    if najl is None:
        raise RuntimeError("[rgb] Nie znaleziono znacznika (musi byc caly w kadrze)")
    zgodnosc, opis, maska = najl
    gc = _grabcut(im, maska)
    if gc is not None:
        z_gc = zgodnosc_z_wzorcem(gc)
        wsp = np.count_nonzero((gc > 0) & (maska > 0)) / max(1, np.count_nonzero((gc > 0) | (maska > 0)))
        if z_gc >= zgodnosc - 0.06 and wsp >= 0.7:
            maska, zgodnosc, opis = gc, z_gc, opis + " + GrabCut"
    return dict(maska=maska, sc=sc, im=im, zgodnosc=zgodnosc, opis=opis)


def wykryj_znacznik_rgb(sciezka, maska_ter=None):
    """
    Znacznik na zdjeciu RGB (wykryj_folie_rgb). maska_ter nie jest potrzebna (zostaje dla zgodnosci
    wywolan) - ksztalt jest porownywany z wzorcem Π, nie z termowizja.
    Zwraca dict: maska (w skali roboczej), sc (skala robocza), obraz (oryginal), im, zgodnosc.
    """
    img = imread(sciezka, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Nie mozna otworzyc: {sciezka}")
    w = wykryj_folie_rgb(img)
    sc = w["sc"]
    c, pole = srodek_pole(w["maska"])
    print(f"  [rgb]    srodek=({c[0]/sc:.1f},{c[1]/sc:.1f})  promien rown.={np.sqrt(pole/np.pi)/sc:.1f}px  "
          f"zgodnosc z wzorcem Pi={w['zgodnosc']:.3f}  kryterium: {w['opis']}  obraz={img.shape[1]}x{img.shape[0]}")
    if w["zgodnosc"] < MIN_ZGODNOSC:
        print("  OSTRZEZENIE [rgb] znacznik wykryty niepewnie - sprawdz _debug_rgb.png")
    return dict(maska=w["maska"], sc=sc, obraz=img, im=w["im"], zgodnosc=w["zgodnosc"])


# ── Dopasowanie ──────────────────────────────────────────────────────────────

def _podobienstwo(m_rgb, m_ter):
    """W (3x3): RGB(robocze) -> termal, z srodkow masy, pol i najlepszego kata."""
    c_r, a_r = srodek_pole(m_rgb)
    c_t, a_t = srodek_pole(m_ter)
    s = np.sqrt(a_t / a_r)
    katy = np.arange(0, 360, 2.0)
    krzywa = krzywa_iou(m_rgb, m_ter, katy)
    k0 = katy[np.argmax(krzywa)]
    dokl = np.arange(k0 - 2, k0 + 2.01, 0.25)
    kd = krzywa_iou(m_rgb, m_ter, dokl, sz=256)
    kat = dokl[np.argmax(kd)]
    R = _h3(cv2.getRotationMatrix2D((0, 0), float(kat), 1.0 / s))
    T2R = _przesun(*c_r) @ R @ _przesun(-c_t[0], -c_t[1])     # termal -> RGB
    return np.linalg.inv(T2R), kat, kd.max()


def wstepne_dopasowanie(m_rgb, m_ter):
    W, kat, iou = _podobienstwo(m_rgb, m_ter)
    if not SPRAWDZ_LUSTRO:
        return W, kat, iou, False
    # kontrola odbicia lustrzanego (przy asymetrycznym znaczniku jest jednoznaczna)
    lustro = cv2.flip(m_ter, 1)
    Wl, kat_l, iou_l = _podobienstwo(m_rgb, lustro)
    if iou_l > iou + 0.03:
        print(f"  OSTRZEZENIE: znacznik pasuje lepiej po odbiciu lustrzanym termalu "
              f"(IoU {iou_l:.3f} vs {iou:.3f}) - obraz termalny jest prawdopodobnie odwrocony,"
              f" uwzgledniam to w transformacji")
        F = np.array([[-1, 0, m_ter.shape[1] - 1], [0, 1, 0], [0, 0, 1]], dtype=float)
        return F @ Wl, kat_l, iou_l, True
    return W, kat, iou, False


def _ecc(tmpl, inp, W0, s, ruch, sigmy):
    """ECC na rozmytych maskach. W: wsp. tmpl -> wsp. inp. s = px inp / px tmpl."""
    W = W0.astype(np.float32)
    if ruch != cv2.MOTION_HOMOGRAPHY:
        W = W[:2]
    kryt = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6)
    for sg in sigmy:
        t = cv2.GaussianBlur(tmpl, (0, 0), sg)
        i = cv2.GaussianBlur(inp, (0, 0), max(0.5, sg * s))
        try:
            _, W = cv2.findTransformECC(t, i, W, ruch, kryt, None, 1)
        except cv2.error as e:
            print("  ECC nie zbiegl:", str(e).strip().splitlines()[-1])
            break
    return _h3(W.astype(np.float64))


def ocen(m_rgb, m_ter, W, s):
    """Dice oraz sredni blad krawedzi [px termalne] miedzy maska RGB a
    maska termalna przeniesiona transformacja W."""
    H, W_ = m_rgb.shape
    mt = cv2.warpPerspective(m_ter, W, (W_, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    mt = (mt > 127).astype(np.uint8) * 255
    wsp = np.count_nonzero((m_rgb > 0) & (mt > 0))
    dice = 2 * wsp / max(1, np.count_nonzero(m_rgb) + np.count_nonzero(mt))

    def brzeg(m):
        return cv2.subtract(m, cv2.erode(m, np.ones((3, 3), np.uint8))) > 0
    br, bt = brzeg(m_rgb), brzeg(mt)
    if not br.any() or not bt.any():
        return dice, float('inf'), mt
    dt_t = cv2.distanceTransform((~bt).astype(np.uint8), cv2.DIST_L2, 5)
    dt_r = cv2.distanceTransform((~br).astype(np.uint8), cv2.DIST_L2, 5)
    return dice, 0.5 * (dt_t[br].mean() + dt_r[bt].mean()) * s, mt


def _homografia_stabilna(Wh, c, ksztalt, max_zmiana_pola=2.0):
    """Homografia jest dopasowana tylko do znacznika - poza nim moze sie
    'rozjechac'. Akceptujemy ja, gdy lokalna skala pola w rogach kadru RGB
    rozni sie od skali w srodku znacznika najwyzej max_zmiana_pola razy."""
    H, W = ksztalt
    w = lambda x, y: Wh[2, 0]*x + Wh[2, 1]*y + Wh[2, 2]
    wc = w(*c)
    for x, y in [(0, 0), (W, 0), (0, H), (W, H)]:
        wr = w(x, y)
        if wr * wc <= 0:
            return False
        r = (wc / wr)**3                      # det J(x) / det J(c)
        if not (1 / max_zmiana_pola <= r <= max_zmiana_pola):
            return False
    return True


def dopasuj(m_rgb, ter, model=MODEL):
    """Zwraca W (3x3) RGB(robocze) -> termal oraz opis."""
    W0, kat, iou, lustro = wstepne_dopasowanie(m_rgb, ter['maska'])
    s = np.sqrt(abs(np.linalg.det(W0[:2, :2])))
    print(f"  wstepnie: kat={kat:.2f} st  skala={1/s:.3f} px RGB(rob.)/px termal  IoU ksztaltu={iou:.3f}")

    # wycinek wokol znacznika - szybciej i bez wplywu reszty sceny
    x, y, w, h = cv2.boundingRect(m_rgb)
    p = max(20, int(0.3 * max(w, h)))
    x0, y0 = max(0, x - p), max(0, y - p)
    x1, y1 = min(m_rgb.shape[1], x + w + p), min(m_rgb.shape[0], y + h + p)
    tmpl = (m_rgb[y0:y1, x0:x1] > 0).astype(np.float32)
    T = _przesun(x0, y0)
    Ti = np.linalg.inv(T)

    wyniki = {'podobienstwo': W0}
    Wa = _ecc(tmpl, ter['miekka'], W0 @ T, s, cv2.MOTION_AFFINE, (6.0, 3.0, 1.5)) @ Ti
    wyniki['afiniczna'] = Wa
    if model in ('homografia', 'auto'):
        Wh = _ecc(tmpl, ter['miekka'], Wa @ T, s, cv2.MOTION_HOMOGRAPHY, (3.0, 1.5)) @ Ti
        Wh = Wh / Wh[2, 2]
        wyniki['homografia'] = Wh

    oceny = {k: ocen(m_rgb, ter['maska'], Wk, s)[:2] for k, Wk in wyniki.items()}
    for k, (d, e) in oceny.items():
        print(f"    {k:13s} Dice={d:.4f}  sredni blad krawedzi={e:.2f} px termal")

    wybor = 'afiniczna'
    if oceny['afiniczna'][0] < oceny['podobienstwo'][0] - 0.01:
        wybor = 'podobienstwo'                     # ECC sie rozjechal
    if 'homografia' in wyniki:
        c, _ = srodek_pole(m_rgb)
        stabilna = _homografia_stabilna(wyniki['homografia'], c, m_rgb.shape)
        lepsza = oceny['homografia'][1] < 0.95 * oceny[wybor][1]
        if model == 'homografia' or (stabilna and lepsza):
            wybor = 'homografia'
        elif not stabilna:
            print("    homografia odrzucona: niestabilna poza znacznikiem")
    print(f"  => wybrany model: {wybor}")
    return wyniki[wybor], dict(model=wybor, kat=kat, s=s, lustro=lustro,
                               dice=oceny[wybor][0], blad=oceny[wybor][1])


# ── Zapis wynikow ────────────────────────────────────────────────────────────

def _do_u8(x, maska=None):
    v = x[maska] if maska is not None and maska.any() else x
    lo, hi = np.percentile(v, 0.5), np.percentile(v, 99.5)
    return np.clip((x - lo) / max(1e-6, hi - lo) * 255, 0, 255).astype(np.uint8)


def _kontur(maska, sc, kolor, img, grubosc):
    ks, _ = cv2.findContours(maska, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    ks = [(k.astype(np.float64) / sc).astype(np.int32) for k in ks]
    cv2.drawContours(img, ks, -1, kolor, grubosc, cv2.LINE_AA)


def zapisz_debug_detekcji(rgb_path, ter_path, rgb, ter, katalog=None, prefiks=""):
    """Maski i podglady detekcji znacznikow. katalog=None: obok plikow wejsciowych
    (jak dawniej); inaczej w podanym folderze z prefiksem nazwy wyniku."""
    k_rgb = Path(katalog) if katalog is not None else Path(rgb_path).parent
    k_ter = Path(katalog) if katalog is not None else Path(ter_path).parent
    imwrite(k_rgb / f"{prefiks}_maska_rgb.png", rgb['maska'])
    imwrite(k_ter / f"{prefiks}_maska_termal.png", ter['maska'])
    d = rgb['im'].copy()
    _kontur(rgb['maska'], 1.0, (0, 255, 0), d, 2)
    imwrite(k_rgb / f"{prefiks}_debug_rgb.png", d)
    t = ter['kolor'].copy()
    _kontur(ter['maska'], 1.0, (0, 255, 0), t, 1)
    imwrite(k_ter / f"{prefiks}_debug_termal.png", t)


def run_registration(rgb_path, ter_path, out_path, model=MODEL):
    """
    Rejestruje obraz termalny do RGB. Zapisuje:
      out_path                      - nalozenie (R = RGB, G = termal)
      <out>_kontury.png             - kontur znacznika RGB (zielony) i termalnego (rozowy)
      <out>_termal_wyrownany.png    - obraz termalny w geometrii zdjecia RGB (BGRA,
                                      alfa = pole widzenia kamery; do funkcji nalozenie())
      <out>_macierz.txt             - macierz 3x3: piksel RGB -> piksel termalny
      <out>_maska_*.png, <out>_debug_*.png - detekcja znacznikow (diagnostyka)
    Wszystko w folderze out_path - dane wejsciowe nie sa modyfikowane.
    Zwraca sciezke do pliku wyjsciowego (str).
    """
    rgb_path, ter_path, out_path = Path(rgb_path), Path(ter_path), Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("== Detekcja znacznikow ========================================")
    ter = wykryj_znacznik_termal(ter_path)
    rgb = wykryj_znacznik_rgb(rgb_path, ter['maska'])
    zapisz_debug_detekcji(rgb_path, ter_path, rgb, ter, out_path.parent, out_path.stem)

    print("\n== Dopasowanie ksztaltow znacznikow ===========================")
    W_rob, info = dopasuj(rgb['maska'], ter, model)
    sc = rgb['sc']
    W = W_rob @ np.diag([sc, sc, 1.0])            # piksel RGB (oryginal) -> piksel termalny

    # podglad zgodnosci ksztaltow (zielony = RGB, czerwony = termal, zolty = oba)
    _, _, mt = ocen(rgb['maska'], ter['maska'], W_rob, info['s'])
    x, y, w, h = cv2.boundingRect(cv2.bitwise_or(rgb['maska'], mt))
    p = max(w, h) // 6
    y0, x0 = max(0, y - p), max(0, x - p)
    porownanie = np.zeros(rgb['maska'].shape + (3,), np.uint8)
    porownanie[:, :, 1] = rgb['maska']
    porownanie[:, :, 2] = mt
    imwrite(out_path.parent / f"{out_path.stem}_debug_ksztalt.png", porownanie[y0:y + h + p, x0:x + w + p])

    # ── Nalozenie w pelnej rozdzielczosci RGB ────────────────────────────────
    img = rgb['obraz']
    H0, W0 = img.shape[:2]
    g_ter, kolor_ter = wczytaj_termal(ter_path)
    flagi = cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP
    ter_w = cv2.warpPerspective(g_ter, W, (W0, H0), flags=flagi)
    alfa = cv2.warpPerspective(np.ones_like(g_ter), W, (W0, H0), flags=flagi)
    pokrycie = alfa > 0.5
    kolor_w = cv2.warpPerspective(kolor_ter, W, (W0, H0), flags=flagi)

    f = _do_u8(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32))
    m = np.where(pokrycie, _do_u8(ter_w, pokrycie), 0).astype(np.uint8)
    kompozyt = cv2.merge([np.zeros_like(f), m, f])    # BGR: R = RGB, G = termal (jak w v2)
    imwrite(out_path, kompozyt)

    # kanal alfa = pole widzenia kamery termalnej (poza nim obraz jest przezroczysty)
    stem = out_path.with_suffix('')
    alfa_u8 = np.clip(alfa * 255 + 0.5, 0, 255).astype(np.uint8)
    imwrite(f"{stem}_termal_wyrownany.png", np.dstack([kolor_w, alfa_u8]))
    np.savetxt(f"{stem}_macierz.txt", W, fmt="%.10g",
               header=f"Piksel RGB (x,y,1) -> piksel termalny; model={info['model']}")

    kont = img.copy()
    gr = max(2, int(round(1.5 / sc)))
    _kontur(rgb['maska'], sc, (0, 255, 0), kont, gr)
    _kontur(mt, sc, (255, 0, 255), kont, gr)
    x, y, w, h = [int(v / sc) for v in cv2.boundingRect(rgb['maska'])]
    p = max(w, h) // 3
    wyc = kont[max(0, y - p):y + h + p, max(0, x - p):x + w + p]
    s_w = min(1.0, 1600 / max(wyc.shape[:2]))
    imwrite(f"{stem}_kontury.png", cv2.resize(wyc, None, fx=s_w, fy=s_w, interpolation=cv2.INTER_AREA))

    print(f"\n  Dice={info['dice']:.4f}  sredni blad krawedzi={info['blad']:.2f} px termal "
          f"(~{info['blad'] / info['s'] / sc:.1f} px RGB)")
    print(f"Wynik: {out_path}")
    return str(out_path)


# ── Uruchomienie bezposrednie ─────────────────────────────────────────────────

if __name__ == '__main__':
    INZ = Path(__file__).resolve().parent.parent      # folder Inzynierka
    BASE = INZ / "archiwum" / "dane" / "pary_rgb_termal" / "nowe1"
    run_registration(
        BASE / "rgb.jpg",
        BASE / "thermal.png",
        INZ / "wyniki" / "wyniki_dopasowania" / "nowe1" / "dopasowanie_v3.png",
    )
