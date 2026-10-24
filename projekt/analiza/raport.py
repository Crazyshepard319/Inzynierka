"""Raport HTML pary: jeden plik z osadzonymi obrazami (mozna go wyslac lub otworzyc gdziekolwiek)."""
import base64
import html

import cv2


def _img(obraz_bgr, opis):
    ok, buf = cv2.imencode(".png", obraz_bgr)
    b64 = base64.b64encode(buf.tobytes()).decode()
    return (f'<figure><img src="data:image/png;base64,{b64}" alt="{html.escape(opis)}">'
            f'<figcaption>{html.escape(opis)}</figcaption></figure>')


def _f(v, cyfry=2):
    if v is None:
        return "–"
    if isinstance(v, float):
        if v != v:
            return "–"
        s = f"{v:.{cyfry}f}"
        return (s[1:] if s.startswith("-") and float(s) == 0 else s).replace(".", ",")
    return html.escape(str(v))


def _tabela(wiersze, naglowek=("Wielkość", "Wartość", "Co znaczy")):
    h = "".join(f"<th>{html.escape(x)}</th>" for x in naglowek)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in w) + "</tr>" for w in wiersze)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"


CSS = """
body{font-family:'Segoe UI',system-ui,sans-serif;margin:0;background:#fafaf8;color:#1a1a1a;line-height:1.45}
main{max-width:980px;margin:0 auto;padding:24px 20px 60px}
h1{font-size:24px;margin:0 0 4px} h2{font-size:18px;margin:32px 0 8px;border-bottom:1px solid #ddd;padding-bottom:4px}
.meta{color:#555;font-size:14px} .ok{color:#1d7a3a;font-weight:600} .zle{color:#b3261e;font-weight:600}
table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0} th,td{border-bottom:1px solid #e3e3e0;padding:6px 8px;text-align:left;vertical-align:top}
th{background:#f0efec;font-weight:600} td:nth-child(2){white-space:nowrap;font-variant-numeric:tabular-nums}
figure{margin:12px 0} img{max-width:100%;border:1px solid #ddd;border-radius:6px} figcaption{font-size:13px;color:#555;margin-top:4px}
.siatka{display:grid;grid-template-columns:1fr 1fr;gap:12px} ol li{margin:4px 0}
@media(max-width:700px){.siatka{grid-template-columns:1fr}}
"""


def zapisz(sciezka, w, obrazy):
    """w: slownik wynikow z potok_pary.analizuj(); obrazy: slownik nazwa -> obraz BGR."""
    i, rej, zg, rgb, ter = w["info"], w["rejestracja"], w["zgodnosc"], w["pomiary_rgb"], w["pomiary_termiczne"]
    ocena = ('<span class="ok">dobra</span>' if zg["obrys"]["dice"] >= 0.9 and zg["tre"]["tre_srednie"] <= 1.0
             else '<span class="zle">do sprawdzenia</span>')
    czesci = [f"""<!doctype html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Para {i['para']} – raport</title>
<style>{CSS}</style></head><body><main>
<h1>Para {i['para']}: RGB i termowizja</h1>
<p class="meta">Zdjęcie {_f(i.get('rgb_oryginal'))} ({_f(i.get('rgb_data'))}) · nagranie {_f(i.get('termal_nagranie'))}
 · znamię {_f(i.get('znamie'))}, fold {_f(i.get('fold'))}</p>
<p>Rejestracja: model <b>{_f(rej['model'])}</b>, zgodność z wzorcem z CVAT: {ocena}
 (Dice obrysu znacznika {_f(zg['obrys']['dice'], 3)}, średni błąd narożników {_f(zg['tre']['tre_srednie'])} mm).
 Znamię: {_f(rgb['pole_mm2'])} mm², średnica {_f(rgb['srednica_rownowazna_mm'])} mm,
 ΔT = {_f(ter.get('delta_T'))} °C względem skóry wokół.</p>
<h2>Co zrobiono</h2><ol>
<li><b>Wczytanie pary</b> z <code>dane/pary/{i['para']}/</code>: zdjęcie, obraz termowizyjny, mapa temperatur °C z pliku SEQ,
 maski i narożniki znacznika z CVAT.</li>
<li><b>Rejestracja</b> (<code>dopasowanie3.py</code>): znacznik wykryty automatycznie w obu obrazach (metoda klasyczna, bez
 masek z CVAT), dopasowanie kształtów → macierz T (piksel RGB → piksel termowizji).</li>
<li><b>Przeniesienie ROI przez T</b>: obrys znamienia, obrys i otwór znacznika oraz 8 narożników ze zdjęcia na obraz
 termowizyjny.</li>
<li><b>Pomiary</b>: na zdjęciu wymiary w mm (homografia z narożników znacznika 35 × 26 mm) i kolor; na termowizji
 temperatura w przeniesionej masce znamienia i w pierścieniu skóry {w['pierscien_mm'][0]:g}–{w['pierscien_mm'][1]:g} mm wokół.</li>
<li><b>Zgodność</b> (badanie E1 z planu): przeniesione obrysy i narożniki porównane z obrysami i narożnikami
 oznaczonymi ręcznie na termowizji.</li>
<li><b>Raport</b>: ten plik i <code>metryki.json</code> w <code>wyniki/wyniki_obu/para_{i['para']}/</code>.</li></ol>
<h2>Obrazy</h2><div class="siatka">{_img(obrazy['rgb'], 'Zdjęcie: znacznik i narożniki (zielone), znamię (czerwone), pierścień skóry do porównania koloru (żółty)')}
{_img(obrazy['termal'], 'Termowizja: znacznik z CVAT (fiolet), przeniesione z RGB: znacznik (zielony) i znamię (czerwone); kreski = błąd narożników')}</div>
<div class="siatka">{_img(obrazy['nakladka'], 'Nałożenie: termowizja przeniesiona na zdjęcie (50%)')}
{_img(obrazy['znamie'], 'Powiększenie termowizji wokół znamienia: przeniesiony obrys (czerwony), pierścień skóry (biały); skala barw od min do max temperatury w kadrze')}</div>
<h2>Zgodność między modalnościami (wzorzec z CVAT)</h2>"""]

    czesci.append(_tabela([
        ("Średni błąd narożników (TRE)", f"{_f(zg['tre']['tre_srednie'])} mm", "średnia odległość 8 narożników przeniesionych z RGB od oznaczonych na termowizji"),
        ("Maks. błąd narożnika", f"{_f(zg['tre']['tre_max'])} mm", "najgorszy z 8 narożników"),
        ("Dice obrysu znacznika", _f(zg['obrys']['dice'], 3), "pokrycie obrysu przeniesionego i oznaczonego (1 = idealne)"),
        ("IoU obrysu znacznika", _f(zg['obrys']['iou'], 3), "część wspólna / suma; surowsze od Dice"),
        ("HD95 obrysu", f"{_f(zg['obrys'].get('hd95_mm'))} mm", "odległość konturów w najgorszych miejscach (bez 5% skrajnych)"),
        ("ASSD obrysu", f"{_f(zg['obrys'].get('assd_mm'))} mm", "średnia odległość konturów"),
        ("Dice otworu (ROI)", _f(zg['otwor']['dice'], 3), "pokrycie wnętrza znacznika, w którym leży znamię"),
        ("HD95 otworu", f"{_f(zg['otwor'].get('hd95_mm'))} mm", "jak wyżej, dla otworu"),
        ("Przesunięcie środków otworu", f"{_f(zg['otwor'].get('przesuniecie_srodkow_mm'))} mm", "o ile przesunięty jest cały obszar"),
        ("Stosunek pól otworu", _f(zg['otwor']['stosunek_pol'], 3), "przeniesiony / oznaczony (1 = równe)"),
        ("Pole znamienia: termowizja / RGB", _f(w['pole_znamienia_termal_do_rgb'], 3), "pole przeniesionej maski w mm² względem pola na zdjęciu (spójność skali)"),
    ]))
    czesci.append(f"""<p class="meta">Wewnętrzna kontrola rejestracji (maski klasyczne, na których liczono T): Dice {_f(rej.get('dice_wewnetrzny'), 4)},
 błąd krawędzi {_f(rej.get('blad_krawedzi_px'))} px termowizji. To nie jest niezależna ocena — niezależna jest tabela wyżej.</p>
<h2>Znamię na zdjęciu RGB</h2>""")
    czesci.append(_tabela([
        ("Pole", f"{_f(rgb['pole_mm2'])} mm²", "liczba pikseli maski × lokalna skala²"),
        ("Średnica równoważna", f"{_f(rgb['srednica_rownowazna_mm'])} mm", "średnica koła o tym samym polu"),
        ("Maks. / min. średnica Fereta", f"{_f(rgb['feret_max_mm'])} / {_f(rgb['feret_min_mm'])} mm", "największa i najmniejsza szerokość"),
        ("Obwód", f"{_f(rgb['obwod_mm'])} mm", ""),
        ("Kolistość", _f(rgb['kolistosc'], 3), "4π·pole/obwód² (1 = koło); mniej = nieregularny brzeg"),
        ("Asymetria (oś główna / prostopadła)", f"{_f(rgb['asymetria_os_glowna'], 3)} / {_f(rgb['asymetria_os_prostopadla'], 3)}", "część pola niepokryta po odbiciu względem osi (0 = symetryczne)"),
        ("Kolor Lab znamienia", ", ".join(_f(x, 1) for x in rgb['lab_znamie']), "L (jasność), a (czerwień–zieleń), b (żółć–błękit)"),
        ("Kolor Lab skóry wokół", ", ".join(_f(x, 1) for x in rgb['lab_skora']), f"pierścień {w['pierscien_mm'][0]:g}–{w['pierscien_mm'][1]:g} mm, bez folii"),
        ("ΔE (znamię – skóra)", _f(rgb['delta_e'], 1), "różnica koloru CIE76; > 10 = wyraźnie widoczna"),
        ("Skala", f"{_f(rgb['mm_na_px'], 4)} mm/px", "lokalny rozmiar piksela w miejscu znamienia"),
    ]))
    czesci.append("<h2>Znamię na termowizji (maska przeniesiona z RGB)</h2>")
    czesci.append(_tabela([
        ("Temperatura znamienia (średnia)", f"{_f(ter.get('T_znamie_srednia'))} °C", "średnia ważona częścią piksela pokrytą przez znamię"),
        ("Mediana / min / max", f"{_f(ter.get('T_znamie_mediana'))} / {_f(ter.get('T_znamie_min'))} / {_f(ter.get('T_znamie_max'))} °C", "piksele pokryte co najmniej w połowie"),
        ("Temperatura skóry wokół", f"{_f(ter.get('T_skora_srednia'))} °C (± {_f(ter.get('T_skora_odchylenie'))})", "pierścień skóry, bez folii znacznika"),
        ("ΔT = znamię – skóra", f"{_f(ter.get('delta_T'))} °C", "kontrast termiczny znamienia"),
        ("Wielkość maski na termowizji", f"{_f(ter['piksele_znamienia'], 1)} px", "przy kilku pikselach wynik jest mało pewny"),
        ("Średnia temperatura otworu znacznika", f"{_f(w.get('T_otwor_srednia'))} °C", "cały obszar zainteresowania (bez folii)"),
        ("Skala", f"{_f(ter['mm_na_px'], 3)} mm/px", "rozmiar piksela termowizji"),
    ]))
    czesci.append(f"""<p class="meta">Mapa temperatur: emisyjność {_f(w.get('emisyjnosc'))}, przeliczenie z pliku SEQ (flirpy).
 Pliki: <code>metryki.json</code>, obrazy PNG w tym folderze, rejestracja w <code>wyniki/wyniki_dopasowania/para_{i['para']}/</code>.</p>
</main></body></html>""")
    sciezka.write_text("".join(czesci), encoding="utf-8")
