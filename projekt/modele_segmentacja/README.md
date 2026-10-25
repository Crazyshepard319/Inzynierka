# Modele segmentacji znamion

Folder z modelami do segmentacji znamienia na zdjęciu RGB i aplikacja do ich testowania.
Każdy model ma ten sam interfejs, więc wybrany model łatwo podłączyć do aplikacji
dopasowania RGB ↔ termowizja (`aplikacja.py`, `dopasowanie3.py`).

## Gdzie co leży

| Co | Gdzie |
|---|---|
| Kod, adaptery, aplikacja testowa | `Inzynierka/projekt/modele_segmentacja/` (OneDrive, git) |
| Sklonowane repozytoria autorów | `modele_segmentacja/repozytoria/` (poza gitem) |
| Środowisko Pythona 3.12 + PyTorch (CUDA) | `C:\Users\groch\modele_dane\srodowisko\` |
| Wagi modeli | `C:\Users\groch\modele_dane\wagi\<model>\` |
| Zbiory danych (ISIC 2018) | `C:\Users\groch\modele_dane\dane\` |
| Wyniki z aplikacji testowej i treningu | `Inzynierka/wyniki/wyniki_segmentacji/` (`wyniki.csv` + foldery z maskami) |

Ciężkie pliki są poza OneDrive (środowisko ~5 GB, wagi 1,3 GB+, dane ~14 GB).
Katalog można zmienić zmienną środowiskową `MODELE_DANE`.

## Aplikacja testowa

`uruchom_tester.bat` (dwuklik). Kolejno:

1. **Wczytaj zdjęcie**. Tester od razu szuka znacznika Π (opcja *szukaj po wczytaniu*);
   gdy go znajdzie, obszar analizy = wnętrze znacznika (biały kontur, szary = folia),
   patrz [Obszar ze znacznika Π](#obszar-ze-znacznika-π).
2. **Zaznacz obszar** (gdy nie ma znacznika) — luźny prostokąt wokół wybranego znamienia.
   Bez tego model (uczony na zdjęciach z jedną zmianą) wybierze największą plamkę/cień na zdjęciu.
   Ręczny prostokąt albo *Cały obraz* wyłączają obszar ze znacznika; *Ze znacznika Π* go przywraca.
3. Zaznacz modele → **Segmentuj**. Kolorowe maski i kontury na podglądzie.
   **Automatyczne przybliżenie** (domyślnie włączone): po znalezieniu znamienia kadr
   ustawia się jak w danych uczących ISIC 2018 — znamię ok. 53% dłuższego boku kadru,
   proporcje 3:2 (zmierzone na 2594 maskach) — i segmentacja jest powtarzana (2–3 przebiegi).
   Bez tego znamię na zdjęciu z telefonu ma na wejściu modelu kilka pikseli i maska
   wychodzi 1,5–2,5× za duża. Przerywana ramka w kolorze modelu = ostateczny kadr.
   W trakcie treningu tester sam wczytuje nowszy „najlepszy” model, gdy się pojawi
   (wersja wag w statusie), a PanDerm liczy wtedy na CPU (~1,6 s/przebieg), bo karta jest zajęta.
4. **Maska wzorcowa** (do metryk): *Rysuj* (klikaj punkty obrysu, PPM/Enter zamyka,
   Backspace cofa, Esc anuluje) albo *Wczytaj* PNG (biały = znamię). Zapisany wzorzec
   `<zdjęcie>_wzorzec.png` wczytuje się automatycznie przy kolejnym otwarciu zdjęcia.
5. Tabela: czas, pole, **Dice, IoU, precyzja, czułość**. **Zapisz wyniki** → maski PNG,
   podgląd z konturami i wiersz w `wyniki/wyniki_segmentacji/wyniki.csv` (separator `;`, do Excela).

Podgląd: kółko myszy = zoom, przeciąganie = przesuwanie, *Przybliż do obszaru*.

## Obszar ze znacznika Π

`znacznik.py`. Znamię leży między ramionami znacznika, więc model nie przeszukuje całego zdjęcia:

1. **Folia** — ta sama detekcja co w rejestracji (`dopasowanie3.wykryj_folie_rgb`): barwa chłodniejsza
   od skóry i tekstura folii, wybór kandydata najbardziej podobnego do wzorca Π (belka 35 mm, ramiona
   26 mm, pasek 9 mm) — obraz termalny nie jest potrzebny. W aplikacji używana jest maska folii
   z rejestracji (`znacznik_z_maski`).
2. **Wnętrze** = otoczka wypukła folii − folia (otwór 17 × 17 mm między ramionami).
3. **Obszar** = wnętrze + margines 8% (znamię może wystawać za linię końców ramion), bez pasa
   przy krawędzi folii (ciemny brzeg taśmy, cień). **ROI** = prostokąt obejmujący obszar.

Przy segmentacji z obszarem (`segmentuj(..., obszar=...)`) piksele poza obszarem (folia) są na
wejściu modelu zastępowane medianą koloru skóry — inaczej skóra w otworze wygląda jak ciemna
plama otoczona jasną ramką, czyli jak znamię w ISIC — a maska znamienia jest ograniczana do
obszaru w każdym przebiegu, także po automatycznym przybliżeniu.

Kryterium akceptacji: zgodność kształtu z wzorcem Π ≥ 0,65 (`dopasowanie3.MIN_ZGODNOSC`) i udział
otworu 0,15–0,60 otoczki.

**Sprawdzenie zdjęć przed adnotacją w CVAT:** przeciągnij folder ze zdjęciami na
`sprawdz_znaczniki.bat` (podfoldery = znamiona: `znamie_01/`, `znamie_02/`, …). Wynik w
`wyniki/wyniki_segmentacji/znaczniki/<folder>_<data>/`: podgląd każdego zdjęcia (zielony = folia, żółty = wnętrze,
pomarańczowy = ROI) i `znaczniki.csv` (zgodność, udział wnętrza, ROI, powód, gdy nie znaleziono).
Zdjęcia HEIC trzeba najpierw wyeksportować do JPG.

## Kandydaci na znamię (`propozycje.py`)

PanDerm uczono na ISIC, gdzie znamię zajmuje ok. połowy kadru. Wnętrze znacznika ma 17 × 17 mm,
a znamię zwykle 1–4 mm, więc gdy model dostaje całe wnętrze, często zaznacza duży fragment skóry
(cień przy folii, włosy), a automatyczne przybliżenie przybliża się do tego błędnego obszaru.
Dlatego `segmentuj_w_znaczniku` (aplikacja, `segmentuj_znamie.py`, tester przy obszarze ze znacznika):

1. `propozycje.py` szuka do 3 kandydatów: ciemne plamy względem lokalnego tła skóry (jasność L po
   usunięciu włosów domknięciem ~0,2 mm, tło = mediana w oknie 8 mm, poza obszarem wartość
   najbliższej skóry, więc cień przy folii nie odstaje), odrzucane pasy cienia wzdłuż folii,
   kształty niezwarte i wydłużone (włos, zmarszczka);
2. model segmentuje każdego kandydata w kadrze jak w ISIC (znamię ~0,53 boku) z automatycznym
   przybliżeniem;
3. zostaje wynik o największym **kontraście brzegu** (średnia ciemność w masce minus w pasie 0,4 mm
   tuż za jej brzegiem); gdy przybliżanie „odpłynie” na skórę (kontrast spadnie poniżej 0,7
   najlepszego przebiegu), zostaje przebieg o największym kontraście.

Gdy nie ma kandydatów — jak dawniej (kadr = całe wnętrze). Ręcznie zaznaczony prostokąt w testerze
działa bez zmian.

Wynik na 94 parach z adnotacjami CVAT (Dice maski PanDerm z maską z CVAT, 25.10):

| metoda | średni Dice | mediana | Dice < 0,5 | Dice ≥ 0,8 |
|---|---|---|---|---|
| kadr = całe wnętrze (dawniej) | 0,38 | 0,06 | 56/94 | 32/94 |
| kandydaci (teraz) | 0,85 | 0,90 | 3/94 | 81/94 |

Trzy słabe pary: 75 i 76 (nie znaleziono znacznika) oraz 81 (znamię w cieniu tuż przy folii).
Nowa metoda nie jest gorsza od dawnej na żadnej parze. Przeliczenie (GPU): `ocen_segmentacje.bat`
→ `wyniki/wyniki_segmentacji/ocena_<model>_<data>/ocena.csv`.

## Modele

| Klucz | Model | Stan |
|---|---|---|
| `progowanie` | Progowanie Otsu jasności — metoda klasyczna, punkt odniesienia | działa od razu |
| `panderm_upernet` | PanDerm (ViT-L) + UperNet | wymaga treningu (niżej) |

### PanDerm + UperNet

Źródło: https://github.com/SiyuanYan1/PanDerm (`Segmentation.md`).
Procedura autorów: pobrać ISIC 2018 Task 1 → pobrać wagi PanDerm → trening (`run.sh`) → ewaluacja.
Gotowe wagi segmentacji z notebooka autorów są niedostępne (link wygasł —
[issue #7](https://github.com/SiyuanYan1/PanDerm/issues/7)), więc model trzeba douczyć.

Odtworzenie procedury autorów (`modele/panderm_upernet/`):

- `architektura.py` — backbone autorów (CAE, ViT-L/16) + głowica UperNet przeniesiona
  z mmsegmentation do czystego PyTorch. Środowisko autorów (mmcv 2.1) się nie instaluje
  ([issue #11](https://github.com/SiyuanYan1/PanDerm/issues/11)). Nazwy wag są identyczne,
  więc checkpoint autorów też by się wczytał.
- `dane.py` — pobranie ISIC 2018 Task 1 i przygotowanie 224×224 tak jak w `dataset_seg.py` autorów.
- `trening.py` — trening jak w `run.sh` autorów: oficjalny podział 2594/100/1000,
  te same augmentacje, CrossEntropy, AdamW lr 1e-4 wd 0,05, cosinus, 100 epok, batch 2,
  wybór modelu wg Jaccarda na walidacji, Dice/Jaccard z największą składową.

**Różnice względem autorów** (wymusza je karta 8 GB):

| | Autorzy | Tutaj | Powód |
|---|---|---|---|
| Optymalizator | AdamW 32-bit | AdamW 8-bit (bitsandbytes) | 32-bit: 8,4 GB i 6,4 s/krok (nie mieści się w 8 GB); 8-bit: 6,0 GB i 0,26 s/krok |
| Precyzja obliczeń | float32 | bfloat16 (autocast), wagi float32 | szybkość |
| GPU | 2 × 1 obraz | 1 × 2 obrazy | ten sam efektywny batch |
| SyncBatchNorm | tak | BatchNorm2d | na jednym GPU działają identycznie |

**Uruchomienie treningu:**

1. `przygotuj_dane_isic.bat` — pobiera ~14 GB (ok. 40 min) i przygotowuje 224×224.
2. `trenuj_panderm.bat` — ok. 6 min/epokę, 100 epok ≈ 10 h. Laptop podłączony do zasilania.
   Skrypt blokuje usypianie. Na końcu sam liczy wynik na zbiorze testowym.
   - przerwany? `trenuj_panderm.bat --wznow`
   - krócej: `trenuj_panderm.bat --epoki 30`
   - szybki test, czy wszystko działa: `trenuj_panderm.bat --proba`
3. Najlepszy model zapisuje się w `modele_dane\wagi\panderm_upernet\model_najlepszy.pth`,
   a log epok (strata, Dice, Jaccard) w `...\przebiegi\<data>\log.csv`.
   Od tej chwili PanDerm jest dostępny w aplikacji testowej.

## Podłączenie do aplikacji dopasowania

```python
from modele_segmentacja import wczytaj_model, maska_w_termalu
from modele_segmentacja.znacznik import segmentuj_w_znaczniku, znacznik_z_maski

model = wczytaj_model("panderm_upernet")             # albo inny klucz
wynik = segmentuj_w_znaczniku(model, obraz_rgb_bgr)  # obszar = wnętrze znacznika Π
# albo z maską folii z rejestracji (rgb = dopasowanie3.wykryj_znacznik_rgb(...)):
#   z = znacznik_z_maski(rgb["maska"], obraz_rgb_bgr.shape, sc=rgb["sc"])
#   wynik = segmentuj_w_znaczniku(model, obraz_rgb_bgr, znacznik=z)
# albo ręczny prostokąt: wynik = model.segmentuj(obraz_rgb_bgr, roi=(x, y, w, h))
maska = wynik.maska                                  # uint8 0/255, rozmiar zdjęcia RGB

# maska w obrazie termalnym (macierz z dopasowania: <wynik>_macierz.txt)
M = numpy.loadtxt("wynik_macierz.txt")
maska_t = maska_w_termalu(maska, M, obraz_termalny.shape)
```

Aplikacja główna musi wtedy działać w środowisku `modele_dane\srodowisko`
(są w nim też wszystkie biblioteki z `aplikacja.py`).

## Dodanie kolejnego modelu

1. Sklonuj repozytorium do `repozytoria/`.
2. Utwórz `modele/<klucz>/__init__.py` z klasą:

```python
from ...interfejs import ModelSegmentacji

class Model(ModelSegmentacji):
    klucz = "moj_model"
    nazwa = "Mój model"
    opis = "..."

    def dostepnosc(self):            # (True, "") albo (False, "powód")
        ...
    def _wczytaj(self):              # wczytanie wag (raz)
        ...
    def _prawdopodobienstwo(self, wycinek_bgr):
        ...                          # -> float32 0..1, rozmiar wycinka
```

Model pojawi się automatycznie w aplikacji testowej. Wycinanie obszaru, progowanie,
największa składowa i wklejanie maski robi klasa bazowa.
