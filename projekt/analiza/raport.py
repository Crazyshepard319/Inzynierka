"""Raport HTML pary: jeden plik z osadzonymi obrazami (mozna go wyslac lub otworzyc gdziekolwiek)."""
import base64
import html
import re

import cv2


def _img(obraz_bgr, opis):
    ok, buf = cv2.imencode(".png", obraz_bgr)
    b64 = base64.b64encode(buf.tobytes()).decode()
    return (f'<figure><img src="data:image/png;base64,{b64}" alt="{html.escape(opis)}">'
            f'<figcaption>{html.escape(opis)}</figcaption></figure>')


def _f(v, cyfry=2):
    """Liczba z przecinkiem dziesietnym (tekst, bez znacznikow HTML)."""
    if v is None:
        return "–"
    if isinstance(v, float):
        if v != v:
            return "–"
        s = f"{v:.{cyfry}f}"
        return (s[1:] if s.startswith("-") and float(s) == 0 else s).replace(".", ",")
    return str(v)


def _tabela(wiersze, naglowek=("Wielkość", "Wartość", "W skrócie")):
    """wiersze: (klucz objasnienia, nazwa, wartosc, skrot) - tekst; nazwa prowadzi do objasnienia."""
    h = "".join(f"<th>{html.escape(x)}</th>" for x in naglowek)
    b = "".join(f'<tr><td><a href="#g-{k}">{html.escape(n)}</a></td><td>{html.escape(v)}</td><td>{html.escape(o)}</td></tr>'
                for k, n, v, o in wiersze)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"


CSS = """
body{font-family:'Segoe UI',system-ui,sans-serif;margin:0;background:#fafaf8;color:#1a1a1a;line-height:1.5}
main{max-width:980px;margin:0 auto;padding:24px 20px 60px}
h1{font-size:24px;margin:0 0 4px} h2{font-size:18px;margin:34px 0 8px;border-bottom:1px solid #ddd;padding-bottom:4px}
h3{font-size:16px;margin:26px 0 4px;color:#1f5fa8}
.meta{color:#555;font-size:14px} .ok{color:#1d7a3a;font-weight:600} .zle{color:#b3261e;font-weight:600}
table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0} th,td{border-bottom:1px solid #e3e3e0;padding:6px 8px;text-align:left;vertical-align:top}
th{background:#f0efec;font-weight:600} td:nth-child(2){white-space:nowrap;font-variant-numeric:tabular-nums}
a{color:#1f5fa8;text-decoration:none} a:hover{text-decoration:underline}
figure{margin:12px 0} img{max-width:100%;border:1px solid #ddd;border-radius:6px} figcaption{font-size:13px;color:#555;margin-top:4px}
.siatka{display:grid;grid-template-columns:1fr 1fr;gap:12px} ol li{margin:4px 0}
.uwagi{background:#fff6e5;border:1px solid #f0d9a8;border-radius:6px;padding:8px 14px;font-size:14px}
dl{margin:0} dt{font-weight:600;font-size:14.5px;margin-top:12px} dd{margin:2px 0 0 0;font-size:14px}
dd .wzor{font-family:'Cambria Math',Cambria,Georgia,serif;font-size:15px;background:#f0efec;padding:1px 5px;border-radius:4px}
@media(max-width:700px){.siatka{grid-template-columns:1fr}}
"""

# ── objasnienia wielkosci (sekcja na koncu raportu) ─────────────────────────
OBJASNIENIA = [
    ("Rejestracja", [
        ("model", "Model rejestracji",
         "Rodzaj przekształcenia T, które nakłada termowizję na zdjęcie. <b>Podobieństwo</b> (4 parametry): "
         "przesunięcie, obrót i jednakowa skala. <b>Afiniczne</b> (6 parametrów): dodatkowo różna skala w dwóch "
         "kierunkach i pochylenie. <b>Homografia</b> (8 parametrów): także perspektywa, gdy telefon i kamera patrzą na "
         "skórę pod różnymi kątami. Tryb „auto” wybiera homografię tylko wtedy, gdy zmniejsza błąd krawędzi o ponad 5% "
         "i nie „rozjeżdża się” poza znacznikiem; inaczej zostaje przy afinicznym."),
        ("T", "Macierz T",
         "Macierz 3×3 z pliku <code>dopasowanie_macierz.txt</code>. Piksel zdjęcia (x, y) przechodzi na piksel "
         "termowizji: <span class='wzor'>[x′, y′, w]ᵀ = T·[x, y, 1]ᵀ</span>, wynik (x′/w, y′/w). Odwrotność T⁻¹ "
         "przenosi w drugą stronę. T jest liczona tylko z masek znacznika wykrytych automatycznie (metoda klasyczna), "
         "bez adnotacji z CVAT, więc adnotacje mogą służyć do jej niezależnej oceny."),
        ("wewn", "Wewnętrzna kontrola rejestracji (Dice, błąd krawędzi)",
         "Dice i średnia odległość krawędzi między maskami znacznika, na których T była dopasowywana. Rejestracja "
         "z definicji maksymalizuje tę zgodność, więc wartość jest zawsze wysoka (ok. 0,95–0,99) i pokazuje tylko, "
         "czy optymalizacja zbiegła. Nie jest niezależną oceną – tą jest porównanie z CVAT."),
    ]),
    ("Zgodność między modalnościami", [
        ("tre", "TRE – błąd położenia narożników",
         "Target Registration Error. Dla każdego z 8 narożników znacznika: punkt oznaczony na zdjęciu przeniesiony "
         "przez T i ten sam narożnik oznaczony ręcznie na termowizji. Odległość liczona w milimetrach na płaszczyźnie "
         "znacznika (homografia termowizji px → mm). Raport podaje średnią i maksimum z 8 narożników. "
         "Punkty odniesienia: rozmiar piksela termowizji (tabela kontroli skali; w tych danych ok. 0,2 mm) oraz "
         "niepewność samych adnotacji – oznaczone narożniki odbiegają od idealnego kształtu 35 × 26 mm średnio "
         "o 0,7–0,9 mm (RMS narożników). TRE rzędu 0,5–1 mm jest więc na poziomie dokładności wzorca."),
        ("dice", "Dice",
         "Pokrycie dwóch obszarów: A – przeniesionego ze zdjęcia, B – oznaczonego na termowizji. "
         "<span class='wzor'>Dice = 2·|A ∩ B| / (|A| + |B|)</span>, gdzie |·| to pole. 1 = obszary identyczne, "
         "0 = rozłączne. Liczony w siatce 4× gęstszej niż piksele termowizji, żeby schodki pikseli nie zaniżały "
         "wyniku. Dla dużego obiektu (znacznik) wartości powyżej 0,9 oznaczają dobrą zgodność; ten sam błąd w mm "
         "daje dla małego obiektu niższy Dice, dlatego obok są też miary w mm."),
        ("iou", "IoU (indeks Jaccarda)",
         "<span class='wzor'>IoU = |A ∩ B| / |A ∪ B|</span>. Mierzy to samo co Dice, ale surowiej: "
         "IoU = Dice / (2 − Dice), np. Dice 0,95 odpowiada IoU 0,905."),
        ("hd95", "HD95 – odległość konturów w najgorszych miejscach",
         "Dla każdego punktu konturu A liczona jest odległość do najbliższego punktu konturu B i odwrotnie. "
         "Z każdego kierunku bierzemy 95. percentyl, a wynikiem jest większy z nich. To „prawie maksymalna” "
         "odległość konturów: pokazuje, o ile rozjeżdżają się w najgorszym miejscu, ale pomija 5% skrajnych "
         "punktów (pojedyncze błędne piksele). W mm."),
        ("assd", "ASSD – średnia odległość konturów",
         "Średnia wszystkich odległości opisanych przy HD95 (oba kierunki razem). Typowe przesunięcie konturu, "
         "zawsze ≤ HD95. W mm."),
        ("srodki", "Przesunięcie środków",
         "Odległość między środkami ciężkości obszarów A i B. Pokazuje, o ile przesunięty jest cały obszar, "
         "niezależnie od kształtu. Dla otworu znacznika to najprostsza miara tego, o ile przeniesione ROI "
         "trafia obok właściwego miejsca na termowizji. W mm."),
        ("pola", "Stosunek pól",
         "<span class='wzor'>|A| / |B|</span>: pole obszaru przeniesionego ze zdjęcia przez pole oznaczonego na "
         "termowizji. 1 = równe; > 1 – przeniesiony jest większy. Wskazuje błąd skali T albo różnicę w tym, jak "
         "szeroko oznaczono krawędź folii w obu obrazach."),
    ]),
    ("Kontrola skali i rozdzielczości", [
        ("rms", "Dopasowanie narożników do wzorca",
         "Skalę w mm daje homografia z 8 narożników znacznika do jego wymiarów (belka 35 mm, ramiona 26 mm, pasek "
         "10 mm). <b>RMS</b> (dla narożników z CVAT) to średni kwadratowy błąd, z jakim oznaczone narożniki pasują "
         "do tego kształtu po homografii; powyżej 1 mm warto sprawdzić adnotację albo krzywiznę skóry. "
         "<b>IoU wzorca</b> (dla narożników automatycznych) to pokrycie maski znacznika przez dopasowany kształt Π; "
         "poniżej ok. 0,8 dopasowanie jest niepewne."),
        ("otwor240", "Pole otworu na termowizji",
         "Nominalnie otwór znacznika ma 15 × 16 mm = 240 mm². Porównujemy dwa pola zmierzone w mm na termowizji "
         "(homografią termowizji): otworu przeniesionego ze zdjęcia przez T i otworu wyznaczonego na samej "
         "termowizji (narożniki z CVAT albo automatyczne). Ich stosunek (1 = równe) to łączny błąd rejestracji "
         "i skali, dostępny także bez adnotacji. Przy narożnikach z CVAT pole otworu odbiega od 240 mm² już na "
         "pojedynczym obrazie, bo oznaczony kształt nie jest idealnym Π (RMS narożników); przy narożnikach "
         "automatycznych wynosi 240 mm² z definicji."),
        ("pole_tr", "Pole znamienia: termowizja / RGB",
         "Pole maski znamienia przeniesionej na termowizję (suma ułamków pokrycia pikseli × rozmiar piksela²) "
         "podzielone przez pole zmierzone na zdjęciu. Obie wartości liczone są niezależnymi skalami "
         "(narożniki na zdjęciu i na termowizji), więc wynik bliski 1 potwierdza spójność skali i rejestracji."),
        ("px_t", "Znamię na termowizji (piksele) i rozmiar piksela",
         "Ile pikseli termowizji obejmuje przeniesione znamię (piksele częściowo pokryte liczą się ułamkiem) oraz "
         "ile milimetrów skóry przypada na jeden piksel kamery (320 × 240). Przy kilku–kilkunastu pikselach "
         "każdy pomiar na termowizji w obrębie znamienia jest mało pewny – to ograniczenie rozdzielczości kamery."),
    ]),
    ("Znamię na zdjęciu RGB", [
        ("skala", "Skala (mm/px)",
         "Lokalny rozmiar piksela zdjęcia w miejscu znamienia: pierwiastek z wyznacznika jakobianu homografii "
         "px → mm w środku znamienia. Uwzględnia perspektywę (zdjęcie pod kątem), ale zakłada, że skóra wokół "
         "znamienia jest płaska i leży w płaszczyźnie znacznika."),
        ("pole", "Pole",
         "<span class='wzor'>pole = liczba pikseli maski × (mm/px)²</span>. W mm²."),
        ("d", "Średnica równoważna",
         "<span class='wzor'>d = 2·√(pole / π)</span> – średnica koła o tym samym polu. Odpowiada kryterium "
         "„D” reguły ABCD (w dermatologii zwraca się uwagę na znamiona powyżej ok. 6 mm)."),
        ("feret", "Średnice Fereta (maks. / min.)",
         "Szerokość znamienia mierzona jak suwmiarką. Maksymalna = największa odległość dwóch punktów konturu "
         "(najdłuższy wymiar). Minimalna = najmniejsza szerokość, z najmniejszego prostokąta opisanego na "
         "znamieniu. Liczone na konturze przeliczonym na mm, więc perspektywa jest skorygowana."),
        ("obwod", "Obwód",
         "Długość konturu znamienia po przeliczeniu na mm. Zależy od dokładności obrysu: ząbkowany kontur "
         "(schodki pikseli, drobne wypustki) wydłuża go."),
        ("kolistosc", "Kolistość",
         "<span class='wzor'>4π·pole / obwód²</span>. 1 dla koła, mniej dla kształtów wydłużonych lub o "
         "nieregularnym brzegu (kryterium „B” – border). Obwód z konturu pikselowego jest lekko zawyżony, więc "
         "kolistość wychodzi o kilka procent zaniżona."),
        ("asym", "Asymetria (oś główna / prostopadła)",
         "Kształt znamienia odbijany jest względem prostej przez jego środek ciężkości: osi głównej (kierunek "
         "największego wydłużenia, z momentów bezwładności) i osi do niej prostopadłej. "
         "<span class='wzor'>asymetria = pole(A XOR odbite A) / pole(A)</span> – część pola, która po odbiciu "
         "nie pokrywa się z oryginałem. 0 = idealnie symetryczne (kryterium „A”)."),
        ("lab", "Kolor L*a*b*",
         "Średni kolor w przestrzeni CIE L*a*b*: L* – jasność (0 czarny … 100 biały), a* – oś zieleń (−) / "
         "czerwień (+), b* – oś błękit (−) / żółć (+). Liczony osobno dla znamienia i dla pierścienia skóry wokół. "
         "Kolor zależy od oświetlenia i automatyki aparatu, więc wartości bezwzględne między zdjęciami porównuje się "
         "ostrożnie; różnica znamię–skóra na tym samym zdjęciu jest stabilniejsza."),
        ("pierscien", "Pierścień skóry",
         "Pas skóry od 2 do 4 mm od brzegu znamienia (odległość w mm na zdjęciu), z wyłączeniem folii znacznika. "
         "Służy jako tło do porównania koloru – jest dość blisko, by mieć to samo oświetlenie, i dość daleko, "
         "by nie łapać rozmytej krawędzi znamienia."),
        ("de", "ΔE (znamię – skóra)",
         "Różnica koloru CIE76: <span class='wzor'>ΔE = √(ΔL*² + Δa*² + Δb*²)</span> między średnim kolorem "
         "znamienia i pierścienia skóry. Ok. 2,3 to próg ledwo zauważalnej różnicy; powyżej 10 kontrast jest "
         "wyraźny."),
    ]),
    ("Segmentacja znamienia i obszary z termowizji", [
        ("seg", "Segmentacja vs adnotacja z CVAT",
         "Gdy znamię wyznaczono inną metodą niż adnotacja (PanDerm, obrys ręczny, plik), jego maska jest "
         "porównywana z maską z CVAT tymi samymi miarami co obszary między modalnościami (Dice, IoU, HD95, ASSD, "
         "przesunięcie środków, stosunek pól), w mm na zdjęciu. To ocena segmentacji (model M1), a nie rejestracji."),
        ("obszar_t", "Obszar zaznaczony na termowizji",
         "Wielokąt zaznaczony na obrazie termowizyjnym i przeniesiony na zdjęcie przez T⁻¹ (przenoszenie ROI "
         "w drugą stronę, np. ciepłe miejsce pokazane na zdjęciu). Pole podawane jest w mm² z obu skal."),
    ]),
]


def _objasnienia():
    czesci = ["<h2 id='objasnienia'>Objaśnienie wielkości</h2>"
              "<p class='meta'>Nazwy wielkości w tabelach wyżej prowadzą do tych opisów.</p>"]
    for grupa, pozycje in OBJASNIENIA:
        czesci.append(f"<h3>{html.escape(grupa)}</h3><dl>")
        for klucz, nazwa, opis in pozycje:
            czesci.append(f"<dt id='g-{klucz}'>{html.escape(nazwa)}</dt><dd>{opis}</dd>")
        czesci.append("</dl>")
    return "".join(czesci)


def objasnienie(klucz):
    """(grupa, nazwa, opis bez znacznikow HTML) - do aplikacji."""
    for grupa, pozycje in OBJASNIENIA:
        for k, nazwa, opis in pozycje:
            if k == klucz:
                return grupa, nazwa, html.unescape(re.sub(r"<[^>]+>", "", opis))
    return "", klucz, ""


def uwagi(w):
    """Ostrzezenia dla pary (tekst)."""
    u = []
    zg, ks, nar = w.get("zgodnosc"), w["kontrola_skali"], w.get("narozniki", {})
    if zg:
        if zg["obrys"]["dice"] < 0.9:
            u.append(f"Dice obrysu znacznika {_f(zg['obrys']['dice'], 3)} < 0,9 – sprawdź rejestrację.")
        if zg["tre"]["tre_srednie"] > 1.0:
            u.append(f"Średni błąd narożników {_f(zg['tre']['tre_srednie'])} mm > 1 mm.")
    if ks["piksele_znamienia_termal"] < 10:
        u.append(f"Znamię obejmuje na termowizji tylko ok. {_f(ks['piksele_znamienia_termal'], 0)} pikseli – "
                 f"pomiary w jego obrębie na termowizji są mało pewne.")
    odch = ks["stosunek_pol_otworu"] - 1
    if abs(odch) > 0.10:
        u.append(f"Pole otworu przeniesionego ze zdjęcia różni się od wyznaczonego na termowizji o {_f(100 * odch, 0)}%.")
    for k, nazwa in (("rgb_rms_mm", "na zdjęciu"), ("termal_rms_mm", "na termowizji")):
        if nar.get(k) is not None and nar[k] > 1.0:
            u.append(f"Narożniki {nazwa} pasują do wzorca 35 × 26 mm z RMS {_f(nar[k])} mm > 1 mm.")
    for k, nazwa in (("rgb_iou_wzorca", "na zdjęciu"), ("termal_iou_wzorca", "na termowizji")):
        if nar.get(k) is not None and nar[k] < 0.8:
            u.append(f"Automatyczne narożniki {nazwa} są niepewne (IoU wzorca {_f(nar[k])}).")
    if not (0.85 <= ks["pole_znamienia_termal_do_rgb"] <= 1.15):
        u.append("Pole znamienia na termowizji różni się od pola na zdjęciu o ponad 15%.")
    return u


def sekcje(w):
    """Tabele wynikow: lista (tytul, wstep albo None, wiersze (klucz objasnienia, nazwa, wartosc, skrot)).
    Wspolne dla raportu HTML i aplikacji."""
    rej, zg, rgb = w["rejestracja"], w.get("zgodnosc"), w["pomiary_rgb"]
    ks, zr, nar = w["kontrola_skali"], w["zrodla"], w.get("narozniki", {})
    r0, r1 = (f"{x:g}" for x in w["pierscien_mm"])
    wynik = []
    if zg:
        wynik.append(("Zgodność między modalnościami (badanie E1)",
                      "Wzorzec: znacznik oznaczony ręcznie w CVAT na termowizji. Obszar A = przeniesiony ze zdjęcia "
                      "przez T, B = oznaczony na termowizji.", [
            ("tre", "Średni błąd narożników (TRE)", f"{_f(zg['tre']['tre_srednie'])} mm", "średnia odległość 8 narożników przeniesionych ze zdjęcia od oznaczonych na termowizji"),
            ("tre", "Maks. błąd narożnika", f"{_f(zg['tre']['tre_max'])} mm", "najgorszy z 8 narożników"),
            ("dice", "Dice obrysu znacznika", _f(zg['obrys']['dice'], 3), "pokrycie obrysów (1 = idealne)"),
            ("iou", "IoU obrysu znacznika", _f(zg['obrys']['iou'], 3), "część wspólna / suma; surowsze od Dice"),
            ("hd95", "HD95 obrysu", f"{_f(zg['obrys'].get('hd95_mm'))} mm", "odległość konturów w najgorszych miejscach"),
            ("assd", "ASSD obrysu", f"{_f(zg['obrys'].get('assd_mm'))} mm", "średnia odległość konturów"),
            ("dice", "Dice otworu (ROI)", _f(zg['otwor']['dice'], 3), "pokrycie wnętrza znacznika, w którym leży znamię"),
            ("hd95", "HD95 otworu", f"{_f(zg['otwor'].get('hd95_mm'))} mm", "jak wyżej, dla otworu"),
            ("srodki", "Przesunięcie środków otworu", f"{_f(zg['otwor'].get('przesuniecie_srodkow_mm'))} mm", "o ile przesunięty jest cały obszar"),
            ("pola", "Stosunek pól otworu", _f(zg['otwor']['stosunek_pol'], 3), "przeniesiony / oznaczony (1 = równe)"),
        ]))
    else:
        wynik.append(("Zgodność między modalnościami (badanie E1)",
                      "Te obrazy nie mają adnotacji z CVAT, więc nie ma wzorca do niezależnej oceny. Po wytrenowaniu "
                      "modeli znacznika M2 (zdjęcie) i M3 (termowizja) w tym miejscu będzie zgodność ich masek (E2, E3). "
                      "Kontrolą bez wzorca jest stosunek pól otworu niżej.", []))
    wynik.append(("Rejestracja", None, [
        ("model", "Model rejestracji", _f(rej.get('model')), "rodzaj przekształcenia T"),
        ("wewn", "Wewnętrzna kontrola: Dice", _f(rej.get('dice_wewnetrzny'), 4), "maski, na których liczono T – nie jest niezależną oceną"),
        ("wewn", "Wewnętrzna kontrola: błąd krawędzi", f"{_f(rej.get('blad_krawedzi_px'))} px", "w pikselach termowizji"),
    ]))
    wiersze = [
        ("otwor240", "Pole otworu: przeniesiony / na termowizji",
         f"{_f(ks['pole_otworu_przeniesionego_mm2'], 1)} / {_f(ks['pole_otworu_termal_mm2'], 1)} mm²",
         f"stosunek {_f(ks['stosunek_pol_otworu'], 3)}; nominalnie {_f(ks['pole_otworu_wzorzec_mm2'], 0)} mm²"),
        ("pole_tr", "Pole znamienia: termowizja / RGB", _f(ks['pole_znamienia_termal_do_rgb'], 3), "zgodność skali obu modalności (1 = równe)"),
        ("px_t", "Znamię na termowizji", f"{_f(ks['piksele_znamienia_termal'], 1)} px", f"= {_f(ks['pole_znamienia_termal_mm2'])} mm²"),
        ("px_t", "Rozmiar piksela termowizji", f"{_f(ks['mm_na_px_termal'], 3)} mm", "bok jednego piksela kamery na skórze"),
    ]
    if zr.get("narozniki_klucz") == "cvat":
        wiersze.append(("rms", "RMS narożników (zdjęcie / termowizja)", f"{_f(nar.get('rgb_rms_mm'))} / {_f(nar.get('termal_rms_mm'))} mm",
                        "dopasowanie adnotacji do wzorca 35 × 26 mm"))
    else:
        wiersze.append(("rms", "IoU wzorca (zdjęcie / termowizja)", f"{_f(nar.get('rgb_iou_wzorca'), 3)} / {_f(nar.get('termal_iou_wzorca'), 3)}",
                        "pokrycie maski znacznika przez dopasowany kształt Π"))
    wynik.append(("Kontrola skali i rozdzielczości", None, wiersze))
    seg = w.get("segmentacja_vs_cvat")
    if seg:
        wynik.append((f"Segmentacja znamienia ({zr['znamie']}) a adnotacja z CVAT", None, [
            ("seg", "Dice", _f(seg['dice'], 3), "pokrycie masek znamienia"),
            ("iou", "IoU", _f(seg['iou'], 3), ""),
            ("hd95", "HD95", f"{_f(seg.get('hd95_mm'))} mm", "kontury w najgorszych miejscach"),
            ("assd", "ASSD", f"{_f(seg.get('assd_mm'))} mm", "średnia odległość konturów"),
            ("srodki", "Przesunięcie środków", f"{_f(seg.get('przesuniecie_srodkow_mm'))} mm", ""),
            ("pola", "Stosunek pól", _f(seg['stosunek_pol'], 3), "segmentacja / adnotacja"),
        ]))
    wynik.append(("Znamię na zdjęciu RGB", f"Znamię: {zr['znamie']}; skala z narożników: {zr['narozniki']}.", [
        ("pole", "Pole", f"{_f(rgb['pole_mm2'])} mm²", "liczba pikseli maski × lokalna skala²"),
        ("d", "Średnica równoważna", f"{_f(rgb['srednica_rownowazna_mm'])} mm", "średnica koła o tym samym polu"),
        ("feret", "Maks. / min. średnica Fereta", f"{_f(rgb['feret_max_mm'])} / {_f(rgb['feret_min_mm'])} mm", "największa i najmniejsza szerokość"),
        ("obwod", "Obwód", f"{_f(rgb['obwod_mm'])} mm", "długość konturu"),
        ("kolistosc", "Kolistość", _f(rgb['kolistosc'], 3), "1 = koło; mniej = wydłużone lub nieregularny brzeg"),
        ("asym", "Asymetria (oś główna / prostopadła)", f"{_f(rgb['asymetria_os_glowna'], 3)} / {_f(rgb['asymetria_os_prostopadla'], 3)}", "część pola niepokryta po odbiciu (0 = symetryczne)"),
        ("lab", "Kolor L*a*b* znamienia", ", ".join(_f(x, 1) for x in rgb['lab_znamie']), "jasność, czerwień–zieleń, żółć–błękit"),
        ("pierscien", "Kolor L*a*b* skóry wokół", ", ".join(_f(x, 1) for x in rgb['lab_skora']), f"pierścień {r0}–{r1} mm, bez folii"),
        ("de", "ΔE (znamię – skóra)", _f(rgb['delta_e'], 1), "różnica koloru; > 10 = wyraźna"),
        ("skala", "Skala", f"{_f(rgb['mm_na_px'], 4)} mm/px", "rozmiar piksela zdjęcia w miejscu znamienia"),
    ]))
    obszary = w.get("obszary_z_termowizji") or []
    if obszary:
        wynik.append(("Obszary zaznaczone na termowizji (przeniesione na zdjęcie)", None,
                      [("obszar_t", f"Obszar {o['nr']}", f"{_f(o.get('pole_rgb_mm2'))} / {_f(o.get('pole_termal_mm2'))} mm²",
                        "pole na zdjęciu / na termowizji") for o in obszary]))
    return wynik


def zapisz(sciezka, w, obrazy):
    """w: wyniki z system.Analiza.zmierz(); obrazy: slownik nazwa -> obraz BGR (obrazy.rysuj)."""
    e = html.escape
    i, rej, zg, rgb = w["info"], w["rejestracja"], w.get("zgodnosc"), w["pomiary_rgb"]
    ks, zr = w["kontrola_skali"], w["zrodla"]
    r0, r1 = (f"{x:g}" for x in w["pierscien_mm"])
    para = i.get("para")
    tytul = f"Para {para}" if para is not None else f"{i.get('zdjecie')} + {i.get('termowizja')}"

    if zg:
        dobra = zg["obrys"]["dice"] >= 0.9 and zg["tre"]["tre_srednie"] <= 1.0
        ocena = (f"zgodność z wzorcem z CVAT: {'<span class=ok>dobra</span>' if dobra else '<span class=zle>do sprawdzenia</span>'} "
                 f"(Dice obrysu znacznika {_f(zg['obrys']['dice'], 3)}, średni błąd narożników {_f(zg['tre']['tre_srednie'])} mm)")
    else:
        ocena = "brak wzorca z CVAT – niezależnej oceny zgodności nie ma"
    meta = []
    if para is not None:
        meta.append(f"zdjęcie {_f(i.get('rgb_oryginal'))} ({_f(i.get('rgb_data'))}) · nagranie {_f(i.get('termal_nagranie'))}"
                    f" · znamię {_f(i.get('znamie'))}, fold {_f(i.get('fold'))}")
    meta.append(f"pliki: {_f(i.get('zdjecie'))}, {_f(i.get('termowizja'))}")

    czesci = [f"""<!doctype html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(tytul)} – raport</title>
<style>{CSS}</style></head><body><main>
<h1>{e(tytul)}: zdjęcie RGB i termowizja</h1>
<p class="meta">{e(' · '.join(meta))}</p>
<p>Rejestracja: model <b>{e(_f(rej.get('model')))}</b>, {ocena}.
 Znamię: {_f(rgb['pole_mm2'])} mm², średnica {_f(rgb['srednica_rownowazna_mm'])} mm; na termowizji obejmuje
 ok. {_f(ks['piksele_znamienia_termal'], 0)} pikseli.</p>"""]
    u = uwagi(w)
    if u:
        czesci.append("<div class='uwagi'><b>Uwagi</b><ul>" + "".join(f"<li>{e(x)}</li>" for x in u) + "</ul></div>")

    folder_wynikow = f"wyniki/wyniki_obu/para_{para}/" if para is not None else "folderze wyników"
    czesci.append(f"""<h2>Co zrobiono</h2><ol>
<li><b>Wejście</b>: zdjęcie z telefonu i obraz termowizyjny{' z <code>dane/pary/' + str(para) + '/</code>' if para is not None else ''};
 {'adnotacje z CVAT dostępne (wzorzec do oceny)' if zg else 'bez adnotacji z CVAT'}.</li>
<li><b>Rejestracja</b> (<code>dopasowanie3.py</code>): znacznik wykryty automatycznie w obu obrazach (metoda klasyczna,
 bez adnotacji), dopasowanie kształtów → macierz T (piksel zdjęcia → piksel termowizji).</li>
<li><b>Segmentacja</b>: narożniki znacznika – {e(zr['narozniki'])}, z nich skala w mm (homografia do wymiarów
 35 × 26 mm); znamię – {e(zr['znamie'])}.</li>
<li><b>Przeniesienie ROI</b>: obrys znamienia, obrys i otwór znacznika oraz 8 narożników ze zdjęcia na termowizję
 (przez T){'; obszary zaznaczone na termowizji na zdjęcie (przez T⁻¹)' if w.get('obszary_z_termowizji') else ''}.</li>
<li><b>Pomiary i zgodność</b>: wymiary i kolor znamienia w mm; kontrola skali (pole otworu
 znacznika){'; porównanie z wzorcem z CVAT (badanie E1)' if zg else ''}.</li>
<li><b>Raport</b>: ten plik, <code>metryki.json</code> i obrazy PNG w {folder_wynikow}.</li></ol>""")

    fiolet = "oznaczony w CVAT" if zg else "wykryty automatycznie"
    niebieskie = ", obszary zaznaczone na termowizji (niebieskie)" if w.get("obszary_z_termowizji") else ""
    czesci.append("<h2>Obrazy</h2><div class='siatka'>"
                  + _img(obrazy["rgb"], f"Zdjęcie: znacznik i narożniki 0–7 (zielone), znamię (czerwone), pierścień skóry "
                                        f"{r0}–{r1} mm do porównania koloru (żółty){niebieskie}")
                  + _img(obrazy["termal"], f"Termowizja (3×): znacznik {fiolet} na termowizji (fioletowy); przeniesione ze "
                                           f"zdjęcia: znacznik (zielony) i znamię (czerwone)"
                                           + ("; białe kreski = błąd narożników" if zg else "") + niebieskie)
                  + "</div><div class='siatka'>"
                  + _img(obrazy["nakladka"], f"Nałożenie: termowizja przeniesiona na zdjęcie (50%). Znacznik ze zdjęcia (zielony), "
                                             f"znacznik {fiolet} na termowizji przeniesiony przez T⁻¹ (fioletowy), znamię (czerwone)")
                  + _img(obrazy["nakladka_zblizenie"], f"Nałożenie w powiększeniu wokół znamienia (czerwone). Termowizja bez "
                                                       f"wygładzania: każdy kwadrat to jeden piksel kamery "
                                                       f"(ok. {_f(ks['mm_na_px_termal'])} mm)")
                  + "</div>")

    for tytul_s, wstep, wiersze in sekcje(w):
        czesci.append(f"<h2>{e(tytul_s)}</h2>")
        if wstep:
            czesci.append(f"<p class='meta'>{e(wstep)}</p>")
        if wiersze:
            czesci.append(_tabela(wiersze))

    czesci.append(_objasnienia())
    czesci.append(f"""<p class="meta" style="margin-top:28px">Pliki: <code>metryki.json</code> i obrazy PNG obok tego raportu,
 rejestracja w <code>{e(str(rej.get('folder', '')))}</code>.</p>
</main></body></html>""")
    sciezka.write_text("".join(czesci), encoding="utf-8")
