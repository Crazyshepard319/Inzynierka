"""
Rejestracja multimodalna: RGB <-> termal (wersja 3)
Eksportuje: run_registration(rgb_path, ter_path, out_path, model=MODEL)

Idea: transformacje wyznacza sam znacznik (folia), a nie cala scena.
  1. Termal: znacznik = najciemniejszy obiekt otoczony cieplejsza skora,
     krawedz z lokalnego progu (polowa drogi miedzy folia a skora).
  2. RGB: kandydaci = obszary o niskim nasyceniu barwy (chroma w Lab) oraz
     obszary odbiegajace od lokalnego koloru skory (lustrzana folia odbija
     biel lub skore). Wybierany jest kandydat najbardziej podobny KSZTALTEM
     do znacznika z termalu (max IoU po obrocie) - nie zalezy od tego,
     czy znacznik jest kolem, pierscieniem, litera C czy ksztaltem "Pi".
  3. Wstepne podobienstwo (srodek masy, skala z pol, kat z przeszukania 360 st.).
  4. Doprecyzowanie ECC (cv2.findTransformECC) na maskach znacznikow:
     afiniczna, opcjonalnie homografia (tylko gdy jest stabilna).
"""

import cv2
import numpy as np
from pathlib import Path


RGB_DET_PX = 1000     # dluzszy bok obrazu RGB, na ktorym odbywa sie detekcja i dopasowanie
MODEL = 'auto'        # 'afiniczna' | 'homografia' | 'auto' (homografia tylko gdy stabilna)


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


def wykryj_znacznik_termal(sciezka):
    """
    Znacznik = ciemny obiekt (folia odbija zimne otoczenie) otoczony skora.
    Zwraca dict: maska (uint8), miekka (float 0..1, 1 = znacznik, krawedz
    subpikselowa z intensywnosci), kolor (obraz BGR), info.
    """
    g, kolor = wczytaj_termal(sciezka)
    H, W = g.shape
    gb = cv2.GaussianBlur(g, (0, 0), 1.0)
    u8 = np.clip(gb, 0, 255).astype(np.uint8)
    otsu, _ = cv2.threshold(u8, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Kilka progow: Otsu oraz nizsze - gdy znacznik dotyka zimnego tla (krawedz
    # reki), przy progu Otsu zlewa sie z nim w jedna plame; folia jest zwykle
    # "zimniejsza" niz tlo, wiec przy nizszym progu sie rozdzielaja.
    # Ocena skladowej: kontrast do otoczenia, otoczenie jasnym, nie przy brzegu.
    k9 = _kolo(4)
    v_min = float(np.percentile(gb, 0.5))
    progi = [otsu] + [v_min + f * (otsu - v_min) for f in (0.8, 0.6, 0.45, 0.3)]
    najl, najl_ocena = None, -1.0
    for t in progi:
        ciemne = (u8 < t).astype(np.uint8) * 255
        n, lab, st, _ = cv2.connectedComponentsWithStats(ciemne, connectivity=8)
        for j in range(1, n):
            x, y, w, h, a = st[j]
            if a < 0.0005 * H * W:
                continue
            sk = (lab == j).astype(np.uint8) * 255
            obwod = cv2.subtract(cv2.dilate(sk, k9), sk)
            jasne = cv2.bitwise_and(obwod, cv2.bitwise_not(ciemne))
            if cv2.countNonZero(jasne) == 0:
                continue
            otoczenie = cv2.countNonZero(jasne) / max(1, cv2.countNonZero(obwod))
            kontrast = gb[jasne > 0].mean() - gb[sk > 0].mean()
            przy_brzegu = x == 0 or y == 0 or x + w == W or y + h == H
            ocena = kontrast * otoczenie**2 * np.sqrt(a) * (0.1 if przy_brzegu else 1.0)
            if ocena > najl_ocena:
                najl_ocena, najl = ocena, sk
    if najl is None:
        raise RuntimeError("[termal] Nie znaleziono znacznika")
    sk = najl

    # lokalny prog: polowa drogi miedzy wnetrzem znacznika a skora wokol;
    # krawedz moze przesunac sie najwyzej o 3 px (nie "wycieka" w zimne tlo)
    pierscien = cv2.subtract(cv2.dilate(sk, k9, iterations=3), cv2.dilate(sk, k9))
    wnetrze = cv2.erode(sk, _kolo(2))
    if cv2.countNonZero(wnetrze) < 20:
        wnetrze = sk
    v_in = float(np.median(gb[wnetrze > 0]))
    v_out = float(np.median(gb[pierscien > 0]))
    prog = 0.5 * (v_in + v_out)
    lok = cv2.bitwise_and((gb < prog).astype(np.uint8) * 255, cv2.dilate(sk, _kolo(3)))
    _, lab2 = cv2.connectedComponents(lok, connectivity=8)
    ids, cnt = np.unique(lab2[(sk > 0) & (lok > 0)], return_counts=True)
    cnt, ids = cnt[ids > 0], ids[ids > 0]
    maska = (lab2 == ids[np.argmax(cnt)]).astype(np.uint8) * 255 if len(ids) else sk
    maska = wypelnij_dziury(maska, 0.03)       # odblaski wewnatrz folii

    # miekka maska: w pasie +-2 px wokol krawedzi wartosc z intensywnosci
    miekka = np.clip((v_out - g) / max(1e-3, v_out - v_in), 0, 1)
    pas = cv2.subtract(cv2.dilate(maska, _kolo(2)), cv2.erode(maska, _kolo(2))) > 0
    miekka = np.where(pas, miekka, (maska > 0)).astype(np.float32)

    c, pole = srodek_pole(maska)
    print(f"  [termal] srodek=({c[0]:.1f},{c[1]:.1f})  promien rown.={np.sqrt(pole/np.pi):.1f}px  "
          f"prog={prog:.0f} (folia {v_in:.0f} / skora {v_out:.0f})  obraz={W}x{H}")
    return dict(maska=maska, miekka=miekka, kolor=kolor)


# ── Detekcja: RGB ────────────────────────────────────────────────────────────

def _skladowe(binarna, k, min_pole, roi=None):
    m = cv2.morphologyEx(binarna, cv2.MORPH_OPEN, k)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k, iterations=2)
    if roi is not None:
        m = cv2.bitwise_and(m, roi)
    H, W = m.shape
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
    out = []
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if a < min_pole or x == 0 or y == 0 or x + w == W or y + h == H:
            continue
        out.append(((lab == j).astype(np.uint8) * 255, st[j], cen[j]))
    return out


def _najlepszy_kandydat(kand, maska_ter, ma_dziure, najl, opis):
    """Ocena kandydatow (pojedyncze skladowe i pary bliskich skladowych - znacznik
    bywa przeciety odblaskiem) przez podobienstwo ksztaltu do znacznika z termalu."""
    katy = np.arange(0, 360, 4)
    opcje = [[i] for i in range(len(kand))]
    for i in range(len(kand)):
        for j in range(i + 1, len(kand)):
            si, sj = kand[i][1], kand[j][1]
            d = np.hypot(*(kand[i][2] - kand[j][2]))
            if d < 0.6 * (max(si[2], si[3]) + max(sj[2], sj[3])):
                opcje.append([i, j])
    for o in opcje:
        m = kand[o[0]][0]
        for i in o[1:]:
            m = cv2.bitwise_or(m, kand[i][0])
        m = wypelnij_dziury(m, 0.03 if ma_dziure else 1e9)
        ocena = krzywa_iou(maska_ter, m, katy, sz=96).max() - 0.02 * (len(o) - 1)
        if najl is None or ocena > najl[0]:
            najl = (ocena, opis, m)
    return najl


def odleglosc_od_skory(im, maska):
    """Odleglosc Mahalanobisa (Lab) od koloru skory zmierzonego wokol znacznika.
    Zwraca mape odleglosci i ROI (otoczenie znacznika)."""
    _, pole = srodek_pole(maska)
    r = np.sqrt(pole / np.pi)
    lab = cv2.cvtColor(cv2.GaussianBlur(im, (0, 0), 1.0), cv2.COLOR_BGR2LAB).astype(np.float32)
    pelna = wypelnij_dziury(maska, 1e9)
    probka = cv2.subtract(cv2.dilate(pelna, _kolo(0.45*r)), cv2.dilate(pelna, _kolo(0.12*r))) > 0
    dziura = cv2.subtract(pelna, cv2.dilate(maska, _kolo(0.08*r))) > 0   # np. srodek pierscienia
    smp = lab[probka | dziura].reshape(-1, 3)
    mu = np.median(smp, 0)
    d0 = np.linalg.norm((smp - mu) / (smp.std(0) + 1e-3), axis=1)
    smp = smp[d0 < np.percentile(d0, 80)]          # odrzuc tlo, paznokcie, cienie
    cov = np.cov(smp.T) + np.diag([4.0, 1.0, 1.0])
    d = lab.reshape(-1, 3) - smp.mean(0)
    D = np.sqrt(np.einsum('ij,jk,ik->i', d, np.linalg.inv(cov), d))
    return D.reshape(lab.shape[:2]), cv2.dilate(pelna, _kolo(0.6*r))


def wykryj_znacznik_rgb(sciezka, maska_ter):
    """
    Zwraca dict: maska (w skali roboczej), sc (skala robocza), obraz (oryginal), opis.
    """
    img = imread(sciezka, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Nie mozna otworzyc: {sciezka}")
    H0, W0 = img.shape[:2]
    sc = min(1.0, RGB_DET_PX / max(H0, W0))
    im = cv2.resize(img, (int(round(W0*sc)), int(round(H0*sc))), interpolation=cv2.INTER_AREA)
    H, W = im.shape[:2]
    k = _kolo(max(2, min(H, W) // 200))
    ma_dziure = udzial_dziur(maska_ter) > 0.05
    min_pole = 0.0007 * H * W

    # przebieg 1: folia = niskie nasycenie barwy
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
    C = cv2.GaussianBlur(np.hypot(lab[..., 1] - 128, lab[..., 2] - 128), (0, 0), 1.5)
    c_skora = float(np.percentile(C, 90))
    najl = None
    for f in (0.15, 0.22, 0.30, 0.38, 0.46, 0.55, 0.65):
        niskie = (C < f * c_skora).astype(np.uint8) * 255
        najl = _najlepszy_kandydat(_skladowe(niskie, k, min_pole), maska_ter, ma_dziure,
                                   najl, f"chroma < {f:.2f}*skora")
    if najl is None:
        raise RuntimeError(f"[rgb] Brak kandydatow na znacznik w {sciezka}")

    # przebieg 2: folia = wszystko, co odbiega od lokalnego koloru skory
    #   (lapie tez lustrzana folie odbijajaca biel albo rozowa skore)
    D, roi = odleglosc_od_skory(im, najl[2])
    for t in (2.5, 3.5, 5.0, 7.0):
        inne = (D > t).astype(np.uint8) * 255
        najl = _najlepszy_kandydat(_skladowe(inne, k, min_pole, roi), maska_ter, ma_dziure,
                                   najl, f"odl. od skory > {t}")

    ocena, opis, maska = najl
    c, pole = srodek_pole(maska)
    print(f"  [rgb]    srodek=({c[0]/sc:.1f},{c[1]/sc:.1f})  promien rown.={np.sqrt(pole/np.pi)/sc:.1f}px  "
          f"kryterium: {opis}  zgodnosc ksztaltu IoU={ocena:.3f}  obraz={W0}x{H0}")
    if ocena < 0.6:
        print("  OSTRZEZENIE [rgb] slabe podobienstwo ksztaltu do termalu - sprawdz _debug_rgb.png")
    return dict(maska=maska, sc=sc, obraz=img, im=im)


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
