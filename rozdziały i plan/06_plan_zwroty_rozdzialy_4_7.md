# Plan i zwroty do rozdziałów 4–7 (pkt 3)

Stan: 28.10.2026. Plik mówi, **co** napisać w każdym podrozdziale, **jakie liczby** podać (wszystkie sprawdzone w wynikach z 28.10), **gdzie** dać rysunek, tabelę, wykres i pseudokod oraz **jakich zwrotów** użyć. Gotowy wzór tekstu: `praca/wzor/rozdzial4_…`–`rozdzial7_…`. Zasady ogólne (styl bezosobowy, liczby z przecinkiem, odsyłacze) – jak w `01_materialy_rozdzialy_1_3_4.md`, sekcja 0.

**Budżet stron** (limit całej pracy 30–40 s. z dodatkami): rozdz. 4 ≈ 4,5 s. · rozdz. 5 ≈ 6 s. · rozdz. 6 ≈ 6,5 s. · rozdz. 7 ≈ 1,5 s.

**Źródła liczb:**
- `wyniki/wyniki_obu/para_N/metryki.json` (potok z 28.10, n = 92) – zestawienie: `Claude outputs/dane_rozdz6/pary_28_10.csv`;
- `wyniki/raport_zbiorczy/statystyki.csv`, `tabele.tex` (26.10 – te same wartości);
- `wyniki/wyniki_dopasowania/porownanie_rejestracji.csv` (badanie E4);
- `wyniki/wyniki_segmentacji/unet_termal/ocena_20261026_152810/` (U-Net, n = 94);
- `wyniki/wyniki_segmentacji/panderm_trening_20261017_121535.png` (trening PanDerm);
- testy: `projekt/testy/test_systemu.py` (wynik w `testy/wynik_testow.txt` po `uruchom_testy.bat`).

**Nazewnictwo (stałe w całej pracy):** znacznik Π · macierz T · homografia H (piksele → mm) · model M1 (PanDerm + UperNet) · model M3 (U-Net) · badania E1, E2, E4 · wymagania WF1–WF15, WN1–WN10 · przypadki użycia PU1–PU13 · testy T01–T18.

**Nowe wymaganie (uwaga promotora z 28.10)** – dopisz w tabeli 3.1:
> WF15 – zapis, dla każdego piksela obrazu termowizyjnego objętego obszarem znamienia przeniesionym ze zdjęcia, jego współrzędnych (x, y) i surowej intensywności z nagrania .SEQ (plik CSV i baza danych). Priorytet: W.

---

## Rozdział 4 „Projekt systemu” (≈ 4,5 s.)

**Rola:** decyzje projektowe i ich uzasadnienie – *jak* spełniono wymagania z rozdz. 3. Bez kodu i bez szczegółów algorytmów (to rozdz. 5). Każda decyzja: „ponieważ …” + odsyłacz do WFx/WNx.

Rozdział jest już we wzorze (wersja z 26.10). Zmiany z 28.10:
- kamera: **FLIR A320, obiektyw 18 mm (FOL18), 320 × 240 px** (odczytane z nagrań .SEQ);
- tabela technologii: flirpy – odczyt surowych wartości z nagrań .SEQ;
- baza: **6 tabel** (nowa `piksel`), schemat w wersji 2 z automatyczną migracją; nowy diagram ERD;
- diagram klas: `Analiza.wczytaj_intensywnosc()`, atrybuty `intensywnosc`, `piksele`; `pomiary.piksele_znamienia()`.

| Podrozdział | Co zawrzeć | Element graficzny |
|---|---|---|
| 4.1 Dobór technologii (≈ 1 s.) | Kryteria wyboru: gotowe implementacje metod z rozdz. 2, praca bez GPU, prosta instalacja. Dwa środowiska (aplikacja bez PyTorch; modele z PyTorch). Odrzucona alternatywa: rejestracja z informacją wzajemną (SimpleITK) – zostaje jako metoda porównawcza E4; pliki CSV zamiast bazy. | **Tab. 4.1** technologie z wersjami (bez cytatów – decyzja 28.10) |
| 4.2 Znacznik Π (≈ 1 s.) | Wymagania wobec znacznika → materiał (folia aluminiowa) → kształt i wymiary (35 × 26 mm, pasek 9 mm, otwór 17 × 17 mm = 289 mm², P1–P8) → uzasadnienie (brak symetrii obrotowej, otwór = ROI, narożniki = skala i TRE) → ograniczenie (symetria lustrzana) → ewolucja. | **Rys. 4.1** wymiary znacznika |
| 4.3 Baza danych (≈ 1 s.) | Cel, obrazy poza bazą (ścieżki względne), 6 tabel i relacje 1 : N, tabela `miara` w układzie długim, tabela `piksel` (klucz złożony analiza–x–y), widoki, wersja schematu i migracja, zapis automatyczny (WF12, WF15, WN9). | **Rys. 4.2** ERD (`baza_erd.pdf`, szer. 0,75) + **Tab. 4.2** tabele |
| 4.4 Diagram klas (≈ 0,75 s.) | `Analiza` (stan + metody = etapy), `Aplikacja` + `Podglad`, `Baza`, `BladEtapu`, `ModelSegmentacji` (interfejs, dziedziczenie), `SegmentacjaZnacznikaTermal` + `UNet` ◆ `Blok`, moduły «utility». | **Rys. 4.3** diagram klas |
| 4.5 Interfejs (≈ 0,75 s.) | Zakładki = etapy potoku, lewa kolumna sterowanie / prawa podglądy, przyciski nieaktywne, wątek roboczy, objaśnienia miar, dwa tryby wejścia, nowe: podgląd „Piksele”. Szczegóły obsługi → Dodatek A. | **Rys. 4.4** zrzut ekranu (✍ Ty) |

**Zwroty (4):**
- „Przy wyborze technologii kierowano się następującymi kryteriami: …”
- „Zdecydowano się na …, ponieważ …” · „Alternatywą było …, jednak …”
- „Wybór ten wynika bezpośrednio z wymagania WN7.”
- „Model danych przedstawiono na diagramie związków encji (rys. 4.2).”
- „Tabela `piksel` ma klucz główny złożony z identyfikatora analizy i współrzędnych piksela, dzięki czemu …”
- „Schemat bazy ma numer wersji; przy otwarciu starszej bazy brakujące tabele są tworzone automatycznie.”
- „Centralną klasą systemu jest …, której metody odpowiadają kolejnym etapom potoku.”
- „Interfejs zaprojektowano tak, aby odzwierciedlał kolejność etapów przetwarzania.”

**Unikaj:** opisu kodu; listy wszystkich metod; zrzutu ekranu bez opisu obszarów.

---

## Rozdział 5 „Implementacja” (≈ 6 s.)

**Rola:** *jak działa* każdy moduł – algorytmy, parametry, dane uczące. Poziom szczegółu: tyle, żeby inny inżynier mógł odtworzyć wynik. Kod tylko jako pseudokod (2 algorytmy), nie listingi Pythona. Wyników oceny tu nie ma – tylko dane techniczne (np. wynik modelu M1 na zbiorze testowym ISIC, bo to część opisu modelu).

### 5.1 Akwizycja i przygotowanie danych (≈ 0,75 s.)
- Seria 23.10.2026: **94 pary, 34 znamiona** (2–3 zdjęcia na znamię, różny obrót znacznika, odległość i kąt).
- Zdjęcia: telefon, format HEIC → JPG (`heic_do_jpg.py`); dłuższy bok 1104–3274 px.
- Termowizja: **FLIR A320 z obiektywem 18 mm**, nagrania .SEQ, 320 × 240 px; pierwsza klatka → obraz z paletą inferno (normalizacja 2.–98. percentyla nagrania, `read_flirpy.py`) + surowe wartości detektora (`termal_surowe.npy`) + mapa °C (`termal_C.npy`, emisyjność 0,98; tylko pomocniczo).
- Poprawki odczytu: obcięcie wierszy telemetrii, kontrola zgodności z obrazem (korelacja rang ≥ 0,95 – spełniona dla 94/94 par).
- Adnotacje w CVAT: maska znamienia (zdjęcie), maski znacznika (obie modalności), 8 narożników (obie modalności); import `import_cvat.py` → `dane/pary/N/` + homografie px → mm z dopasowania narożników do wzorca.
- Podział do walidacji krzyżowej: 5 foldów **po znamionach** (wszystkie zdjęcia znamienia w jednym foldzie).
- Element: **Tab. 5.1** zbiór danych (liczby, rozdzielczości, adnotacje) – opcjonalnie, można opisać tekstem.

### 5.2 Moduł rejestracji (≈ 1,5 s.)
- 5.2.1 Wstępne przetwarzanie: zdjęcie zmniejszane do dłuższego boku 1000 px; termowizja w skali szarości.
- 5.2.2 Detekcja znacznika:
  - termowizja – kandydaci = obszary ciemniejsze od skóry (progi 0,5 / 0,65 / 0,8 × 70. percentyl jasności) lub teksturowane (lokalne odchylenie > 6 / 10 / 15), oczyszczone morfologicznie; wybór kandydata o największym IoU z wzorcem Π (przeszukanie kąta co 4°); krawędź subpikselowa – próg w połowie drogi folia–skóra w pasie ±4 px;
  - zdjęcie – kandydaci z mapy „chłodu” barwy (a* + b* w Lab względem mediany skóry) i tekstury (odchylenie w oknie 7 × 7), kilka progów; ten sam wybór po wzorcu; krawędź doprecyzowana segmentacją interaktywną z OpenCV (tylko gdy nie psuje kształtu). **Nie podawaj nazwy GrabCut** (decyzja 26.10).
  - próg pewności: zgodność z Π ≥ 0,65; poniżej – ostrzeżenie.
- 5.2.3 Dopasowanie wstępne (podobieństwo): środki mas, skala z pierwiastka stosunku pól, kąt z przeszukania 0–360° co 2° i doprecyzowania ±2° co 0,25°.
- 5.2.4 Doprecyzowanie ECC (`evangelidis2008`): na **maskach** (nie na intensywnościach) – problem wielomodalny sprowadzony do jednomodalnego; wycinek wokół znacznika (margines 30%); przekształcenie afiniczne przy rozmyciu masek σ = 6 → 3 → 1,5 px, następnie homografia σ = 3 → 1,5 px; maks. 200 iteracji, ε = 10⁻⁶.
- 5.2.5 Wybór modelu: domyślnie afiniczne; homografia, gdy zmniejsza błąd krawędzi o > 5% **i** jest stabilna (lokalna skala pola w narożnikach kadru różni się od skali w środku znacznika najwyżej 2×). Wynik na 92 parach: homografia 65, afiniczne 27.
- 5.2.6 Wynik: macierz T (piksel zdjęcia → piksel termowizji), termowizja w geometrii zdjęcia (kanał alfa = pole widzenia kamery), nałożenie.
- Elementy: **Algorytm 5.1** (pseudokod rejestracji) + **Rys. 5.1** para 14: a) folia na zdjęciu, b) folia na termowizji, c) kontury po rejestracji (`rejestracja_para14.pdf`).

### 5.3 Modele segmentacji (≈ 1,75 s.)
- 5.3.1 M1 – znamię na zdjęciu (PanDerm + UperNet):
  - koder ViT-L PanDerm z wagami autorów (`yan2025panderm`; uczenie samonadzorowane na 2 149 706 obrazach z 11 źródeł), dekoder UperNet (`xiao2018upernet`);
  - douczanie na ISIC 2018 Task 1 (`codella2019`): 2594 / 100 / 1000 obrazów, 224 × 224, entropia krzyżowa, AdamW (8-bit), lr 10⁻⁴, wd 0,05, harmonogram kosinusowy, 100 epok, paczka 2, obliczenia bfloat16 (karta 8 GB); wybór epoki po indeksie Jaccarda na walidacji (epoka 11);
  - wynik na zbiorze testowym ISIC (1000 obrazów): **Dice 0,899, Jaccard 0,833** (rys. 5.2 – krzywe uczenia, plik `panderm_trening.png`);
  - zastosowanie w systemie: obszar szukania = otwór znacznika poszerzony o 8% (√pola), folia zastąpiona medianą barwy skóry; do 3 kandydatów (ciemne plamy względem lokalnego tła skóry; domknięcie ≈ 0,2 mm usuwa włosy; tło = mediana w oknie 8 mm; odrzucane pasy wzdłuż folii i kształty wydłużone) → PanDerm na kadrze wokół każdego kandydata z automatycznym przybliżeniem → wybór maski o największym kontraście brzegu (ciemność w masce minus w pasie 0,4 mm na zewnątrz);
  - uzasadnienie kandydatów: przesunięcie dziedziny – w ISIC znamię zajmuje ok. 53% kadru, tu 1–4 mm w otworze 17 mm. Bez kandydatów: mediana Dice 0,06; z kandydatami: 0,90 (liczby z notatek 25.10 – w pracy możesz podać jako uzasadnienie decyzji, nie jako wynik).
  - uruchamiany jako osobny proces w środowisku modeli (WN7).
- 5.3.2 M3 – znacznik na termowizji (U-Net, `ronneberger2015`):
  - architektura: 4 poziomy, kanały 16–32–64–128, dno 256, 9 bloków (2 × splot 3 × 3 + normalizacja wsadowa + ReLU), 1,94 mln parametrów; wejście 240 × 320 w skali szarości standaryzowane per obraz; wyjście – logit, próg 0,5;
  - uczenie: BCE + (1 − miękki Dice), AdamW lr 2·10⁻³, wd 10⁻⁴, kosinus, paczka 8, **60 epok bez wyboru epoki na zbiorze testowym**; augmentacja: obrót 0–360°, skala 0,75–1,3, przesunięcie, odbicia, gamma, kontrast, rozmycie, szum;
  - 5-krotna walidacja krzyżowa po znamionach (pary testowe foldu nie były w treningu); model końcowy na wszystkich parach dla obrazów spoza zbioru;
  - eksport do ONNX → `cv2.dnn` w aplikacji (bez PyTorch), ok. 67 ms / obraz na CPU.
- Elementy: **Tab. 5.2** parametry uczenia M1 i M3 (dwie kolumny) – oszczędza tekst; **Rys. 5.2** krzywe uczenia M1 (opcjonalnie – przy braku miejsca pominąć).

### 5.4 Przeniesienie ROI i skala metryczna (≈ 0,75 s.)
- Narożniki: wzorzec Π dopasowany do maski znacznika (podobieństwo → ECC afiniczne → homografia), 8 wierzchołków → homografia H (px → mm) w każdej modalności.
- Skala lokalna: √|det J| homografii w środku znamienia; piksel termowizji na skórze: mediana 0,283 mm (0,21–0,44 mm).
- Przeniesienie obszarów **wektorowo**: kontur maski (z poprawką o pół piksela) → wierzchołki przez T → wypełnienie w siatce 4× gęstszej (piksel należy, gdy jego środek jest w wielokącie) → ułamek pokrycia każdego piksela (wielokrotność 1/16); błąd pola ok. 1%.
- **Piksele znamienia (WF15):** piksele z ułamkiem > 0; „w masce” – ułamek ≥ 0,5; dla każdego: x (kolumna), y (wiersz), ułamek, surowa intensywność z .SEQ. Zapis: CSV + tabela `piksel`.
- Element: **Algorytm 5.2** (pseudokod przeniesienia i pikseli) – krótki.

### 5.5 Pomiary i miary zgodności (≈ 0,5 s.)
- Parametry znamienia (zdjęcie, mm): pole, obwód, średnica równoważna, Feret maks./min., kolistość 4π·pole/obwód², asymetria (XOR z odbiciem względem osi głównej i prostopadłej), barwa L*a*b*.
- Miary zgodności masek: Dice, IoU, HD95, ASSD (transformata odległości), przesunięcie środków, stosunek pól – w siatce 4×, w mm; TRE (`fitzpatrick1998`) – na płaszczyźnie znacznika (H termowizji).
- E2: folia ze zdjęcia przez T (A) vs folia z M3 (B); otwór = otoczka wypukła − folia, ta sama funkcja dla A i B.
- Element: wzory (Dice, IoU, HD95, TRE) – **równania**, nie tabela. Definicje są w 2.4 – tu tylko sposób obliczenia (siatka 4×, mm). Unikaj powtarzania definicji.

### 5.6 Baza danych, raport i aplikacja (≈ 0,75 s.)
- Baza: moduł `sqlite3`, schemat w kodzie, wersja (PRAGMA user_version = 2), migracja; zapis automatyczny; polecenia `baza_danych.bat` (utworz, importuj_wyniki, pokaz, eksport, eksport_piksele, sql).
- Raport: HTML z osadzonymi obrazami i objaśnieniami, `metryki.json`, PNG, CSV pikseli; uwagi automatyczne (np. TRE > 1 mm, Dice E2 < 0,85, zgodność z Π < 0,65, brak .SEQ).
- Aplikacja: customtkinter, 6 zakładek, obliczenia w wątku roboczym + kolejka komunikatów; PanDerm jako podproces; potok wsadowy (`potok_pary.py`, `--z_zapisanych`) i raport zbiorczy z tabelami LaTeX.
- Element: zrzut ekranu zakładki „5. Pomiary” albo „6. Raport” – **tylko jeśli** nie ma go w 4.5; inaczej odsyłacz.

**Zwroty (5):**
- „Moduł … zaimplementowano w języku Python z wykorzystaniem biblioteki …”
- „Przebieg algorytmu przedstawiono w postaci pseudokodu (algorytm 5.1).”
- „Kryterium ECC maksymalizowano na maskach znacznika, a nie na intensywnościach obrazów, dzięki czemu problem wielomodalny sprowadzono do jednomodalnego.”
- „Parametry dobrano eksperymentalnie na …” (uczciwie – jeśli tak było) / „przyjęto zgodnie z procedurą autorów [x]”.
- „Model douczono na zbiorze …, stosując …”
- „Ze względu na przesunięcie dziedziny między … a … zastosowano …”
- „W celu uniknięcia przecieku danych podział wykonano według znamion, a nie zdjęć.”
- „Obszary przenoszono wektorowo: …”
- „Wynik etapu zapisywany jest w …”

**Unikaj:** listingów kodu (najwyżej 5–10 linii, jeśli naprawdę trzeba); parametrów bez uzasadnienia; wyników badań E1–E4 (to rozdz. 6); słowa „GrabCut”, „Bland–Altman”.

---

## Rozdział 6 „Testy i wyniki” (≈ 6,5 s.)

**Rola:** weryfikacja wymagań i ocena jakości. Kolejność w każdym podrozdziale: **pytanie → protokół → wynik (tabela/wykres) → interpretacja**. Wszystkie liczby z odchyleniem lub medianą i zakresem; zawsze podaj n.

### 6.1 Zbiór danych i protokół oceny (≈ 0,5 s.)
- 94 pary, 34 znamiona; **92 pary przeanalizowane** – w parach 75 i 76 maska znacznika na zdjęciu bez poprawnego otworu (2% i 8% otoczki, oczekiwane 15–60%), a ponowna detekcja niezgodna z Π (0,54 i 0,58 < 0,65) → brak obszaru segmentacji znamienia, komunikat (WN6). Uwaga: pary 8, 59, 78, 79 też mają zgodność na zdjęciu < 0,65, ale ich maska ma poprawny otwór, więc są analizowane z ostrzeżeniem – i wszystkie mają TRE > 1,3 mm (ostrzeżenie trafne).
- Wzorzec: adnotacje CVAT – wyłącznie do oceny.
- Badania: E1 (rejestracja vs CVAT), E2 (zgodność masek między modalnościami bez adnotacji), E4 (porównanie metod rejestracji), ocena segmentacji M1 i M3, piksele znamienia, testy funkcjonalne.
- Statystyka: średnia ± odchylenie, mediana, min.–maks.; porównania parami – test Wilcoxona (rozkłady skośne); zależność – współczynnik Spearmana.
- Kryteria akceptacji ustalone **przed** wynikami (WN1, WN4, WN5) – przypomnij je.

### 6.2 Dokładność rejestracji (E1) i porównanie metod (E4) (≈ 1,5 s.)
- E1 (n = 92): TRE **mediana 0,61 mm**, średnia 0,96 ± 2,52 mm, zakres 0,29–24,69 mm; ≤ 1 mm w **78/92 (85%)**; maks. błąd narożnika – mediana 1,13 mm; Dice obrysu – mediana 0,960; Dice otworu – mediana 0,960; HD95 obrysu – mediana 0,81 mm. **WN4 spełnione** (mediana ≤ 1 mm).
- Odstające: para 78 – TRE 24,7 mm (nieudana rejestracja); 8 – 2,31 mm; 79 – 1,93 mm; 72 – 1,69 mm. Średnia zawyżona przez jedną parę – dlatego mediana.
- E4 (n = 92, ten sam start – znacznik wykryty jak w systemie):

| Metoda | Mediana TRE [mm] | Q1–Q3 | ≤ 1 mm | Czas – mediana [s] |
|---|---|---|---|---|
| dopasowanie wstępne (bez optymalizacji) | 3,13 | 1,56–6,26 | 10/92 | – |
| informacja wzajemna – cały obraz | 4,51 | 2,62–9,60 | 5/92 | 16,0 |
| informacja wzajemna – otoczenie znacznika | 3,36 | 1,42–6,20 | 13/92 | 10,5 |
| **ECC na maskach (system)** | **0,61** | 0,52–0,78 | **79/92** | **8,4** |

  - Wilcoxon ECC vs MI-otoczenie: p < 0,001; ECC lepsze w 87/92 parach.
  - Czas rejestracji systemu: mediana 8,4 s, maks. 13,2 s → **WN1 spełnione** (< 15 s). (Potwierdź, na jakim komputerze liczono E4; test T04 w maszynie wirtualnej: 6,4 s.)
  - Interpretacja: MI na intensywnościach nie poprawia nawet dopasowania wstępnego – zgodne z `correlation-ratio` (wiele maksimów MI) i z `visible-and-infared` (brak powiązania intensywności); znacznik daje korespondencję niezależną od modalności.
- Elementy: **Tab. 6.1** E1 (lub połączona z E2) · **Rys. 6.1** wykres E4 (`wyk_e4_tre.pdf`) · tabela E4 w tekście albo na wykresie (mediany są na wykresie – tabela niepotrzebna).

### 6.3 Jakość segmentacji w obu modalnościach (≈ 1 s.)
- M3 U-Net (n = 94, walidacja krzyżowa): Dice **0,969 ± 0,008** (mediana 0,970, min. 0,937), IoU 0,939, HD95 0,68 ± 0,27 mm (mediana 0,62), ASSD 0,23 mm, stosunek pól 1,004; foldy 0,968–0,970; Dice ≥ 0,9 na 94/94 → **WN5 spełnione**.
- Detektor klasyczny (z rejestracji): Dice 0,954 ± 0,017, HD95 1,06 ± 0,59 mm, stosunek pól 0,950 (zaniża brzeg folii). U-Net lepszy: Wilcoxon p < 0,001.
- M1 PanDerm na zdjęciach z telefonu (n = 92): Dice **0,870 ± 0,103** (mediana 0,896), IoU 0,812 (mediana), HD95 mediana 0,24 mm, ASSD mediana 0,10 mm, stosunek pól mediana 1,10 (średnia 1,22) – model zawyża obszar; Dice ≥ 0,8 na 81/92; < 0,5 na 2 parach (57 – 0,32, znamię przy folii; 81 – 0,37, znamię w cieniu folii); 59 – 0,55 (bardzo blade znamię).
- Porównanie z ISIC (test 0,899): wynik na własnych zdjęciach niewiele niższy mimo przesunięcia dziedziny – dzięki kandydatom i kadrowaniu.
- Elementy: **Rys. 6.2** wykres pudełkowy Dice M1/M3/detektor (`wyk_segmentacja.pdf`) · **Tab. 6.2** miary segmentacji (Dice, IoU, HD95, ASSD, stosunek pól dla M1, M3, detektora).

### 6.4 Zgodność ROI między modalnościami (E2) (≈ 1 s.)
- n = 92, bez adnotacji: Dice folii **0,957 ± 0,032** (mediana 0,966), ≥ 0,9 na 89/92; Dice otworu (ROI) mediana 0,960; HD95 otworu mediana 0,88 mm; przesunięcie środków otworu mediana 0,23 mm; stosunek pól otworu mediana 0,96.
- Najważniejszy wynik: E2 **wykrywa złą rejestrację bez wzorca** – korelacja rang Dice folii (E2) z TRE (E1): ρ = −0,72; najniższe E2 = pary z największym TRE (78: Dice 0,72 / TRE 24,7 mm; 8: 0,86 / 2,3 mm; 79: 0,89 / 1,9 mm). Dice otworu < 0,93 w 10 parach, z czego 9 ma TRE > 1 mm.
- E2 ujawnia też błędy segmentacji jednej modalności (para 1: Dice otworu 0,81 – maska folii ze zdjęcia wchodzi w otwór).
- Elementy: **Rys. 6.3** wykres E2 vs TRE (`wyk_e2_tre.pdf`) · **Rys. 6.4** para 14: a) maski E2 na termowizji, b) nałożenie w powiększeniu (`wyniki_para14.pdf`) · tabela E2 – można połączyć z E1 w **Tab. 6.1** (kolumny: miara, E1, E2).

### 6.5 Parametry znamion i piksele na termowizji (≈ 1 s.)
- Znamiona (zdjęcie, PanDerm, n = 92): pole mediana 3,42 mm² (1,16–28,58), średnica równoważna mediana 2,09 mm (1,22–6,03); pole z CVAT mediana 3,24 mm².
- Spójność skali: pole znamienia na termowizji / na zdjęciu = 1,015 ± 0,034 (dwie niezależne homografie) → skala i rejestracja spójne.
- **Piksele (WF15):** łącznie **7337 pikseli w maskach** 92 znamion; na znamię mediana 44 (10–290) + mediana 12 częściowych; surowa intensywność: odchylenie w obrębie znamienia mediana 14,1 (Q1–Q3 10,9–19,8), rozstęp mediana 65 jednostek. Orientacyjnie 1 °C ≈ 213 jednostek surowych w zakresie 30–37 °C (z map °C kamery) → odchylenie ≈ 0,07 °C – znamię bez schłodzenia nie wyróżnia się termicznie (`visualization-detection-cancer`). Przy TRE ≈ 0,6 mm (≈ 2 px) piksele brzegowe mogą należeć do skóry obok.
- Elementy: **Rys. 6.5** piksele pary 14 (`piksele_para14.png`, szer. 0,6) · **Tab. 6.3** parametry znamion + piksele (mediana, zakres).

### 6.6 Testy funkcjonalne (≈ 0,75 s.)
- 18 testów automatycznych (`projekt/testy/test_systemu.py`, `unittest`) – każdy przypisany do WF/WN; wynik w maszynie wirtualnej (Linux, bez wag U-Net): **17 zaliczonych, 1 pominięty (T09 – brak wag)**, czas 19,7 s. **Uruchom `uruchom_testy.bat` u siebie** (wtedy T09 też się wykona) i wpisz wynik.
- Testy ręczne GUI (TG1–TG6) – tabela w Dodatku A albo tu; wykonaj sam i wpisz wynik.
- Elementy: **Tab. 6.4** testy (ID, wymaganie, scenariusz, wynik) – skrócona: 18 wierszy po jednej linii.

### 6.7 Dyskusja i ograniczenia (≈ 0,75 s.)
- Porównanie z literaturą (bez porównywania liczb wprost – inne dane i miary): Maurya (`non-contact-breathing-monitoring`) – błąd 1,8 px; González-Pérez (`gonzalezperez2021`) – Dice/Jaccard stóp (duże obiekty); Oniga (`oniga2026`) – SSIM/MI bez TRE w mm. Tu: TRE w mm + niezależna weryfikacja E2.
- Ograniczenia: jedna seria, jeden zestaw kamer, jeden autor zdjęć; adnotacje CVAT jednej osoby (zmienność obserwatora – `codella2019`: zgodność ekspertów 0,786 Jaccard); płaska skóra (homografia); znacznik musi być cały w kadrze; obraz bez znacznika daje tylko ostrzeżenie (test T05: zgodność 0,54), a nie przerwanie; M1 zawyża obszar (stosunek pól 1,10); intensywność to wartość surowa (bez kalibracji temperatury).
- Wnioski cząstkowe → rozdz. 7.

**Zwroty (6):**
- „Celem badania … było sprawdzenie, czy …”
- „Za wzorzec przyjęto adnotacje …, które nie były wykorzystywane przez system.”
- „Wyniki zestawiono w tabeli 6.1; rozkład … przedstawiono na rysunku 6.1.”
- „Mediana błędu wyniosła …, a w … z … par błąd nie przekroczył 1 mm.”
- „Ze względu na skośny rozkład błędów podano medianę i zakres.”
- „Różnica jest istotna statystycznie (test Wilcoxona, p < 0,001).”
- „Wynik ten potwierdza, że …” / „Oznacza to, że …” / „Należy jednak zauważyć, że …”
- „Największy błąd wystąpił dla pary …, w której …”
- „Wymaganie WN4 zostało spełnione.”
- „Uzyskane wartości są zbliżone do … opisanych w pracy [x], przy czym …”
- „Ograniczeniem przeprowadzonych badań jest …”

**Unikaj:** samych średnich przy rozkładach skośnych; „bardzo dobre wyniki” bez kryterium; porównywania liczb z innych prac jak 1 : 1; ukrywania porażek (pary 75, 76, 78 – pokaż i wyjaśnij).

---

## Rozdział 7 „Podsumowanie” (≈ 1,5 s.)

**Rola:** zamknięcie – czy cel osiągnięto, co z tego wynika, co dalej. Bez nowych wyników, bez nowych cytatów (najwyżej 1–2).

| Podrozdział | Co zawrzeć |
|---|---|
| 7.1 Realizacja celu (≈ 0,5 s.) | Powtórz cel jednym zdaniem; przejdź przez zadania z 1.2 (najlepiej w tej samej kolejności) i wymagania promotorki: baza (6 tabel), projekt, implementacja, modele dla obu modalności (M1, M3), miary zgodności, weryfikacja, dokumentacja; wszystkie wymagania W spełnione (tab. 6.4). |
| 7.2 Wnioski (≈ 0,5 s.) | 4–5 wniosków z liczbami: (1) znacznik + ECC na maskach: mediana TRE 0,61 mm, 85% par ≤ 1 mm, 5× lepiej niż MI; (2) U-Net na 94 obrazach: Dice 0,969 – mały model wystarcza; (3) E2 bez adnotacji wykrywa złą rejestrację (ρ = −0,72); (4) PanDerm po douczeniu na ISIC i kadrowaniu kandydatów: Dice 0,87 na zdjęciach z telefonu, ale zawyża pole; (5) piksele: dane do analizy termicznej gotowe, ale znamię bez schłodzenia nie odróżnia się (σ ≈ 0,07 °C). |
| 7.3 Kierunki dalszych prac (≈ 0,5 s.) | termografia dynamiczna (schłodzenie) i analiza pikseli w czasie; douczenie M1 na własnych zdjęciach (walidacja krzyżowa po znamionach); przerwanie analizy, gdy znacznik na termowizji jest niepewny; więcej serii i kamer; ocena wielu obserwatorów; automatyczna kalibracja temperatury; badanie z udziałem lekarzy (użyteczność). |

**Zwroty (7):**
- „Cel pracy został osiągnięty.” / „Zrealizowano wszystkie zadania wymienione w podrozdziale 1.2.”
- „Najważniejsze wnioski z pracy są następujące: …”
- „Przeprowadzone badania wykazały, że …”
- „Otrzymane wyniki wskazują, że …”
- „Rozwiązanie może zostać rozszerzone o …”
- „Interesującym kierunkiem dalszych prac jest …”
- „Ograniczenia opisane w podrozdziale 6.7 wyznaczają kierunki dalszych prac.”

**Unikaj:** powtarzania rozdz. 6 słowo w słowo; „system jest idealny”; obietnic bez podstaw („system może być stosowany w klinice”).

---

## Pseudokod w LaTeX-u

Pakiety: `\usepackage[chapter]{algorithm}` (numeracja 5.1, 5.2) i `\usepackage[noend]{algpseudocode}` (bez linii „koniec …”). Polskie nazwy:
```latex
\floatname{algorithm}{Algorytm}
\renewcommand{\listalgorithmname}{Spis algorytmów}
\algrenewcommand\algorithmicrequire{\textbf{Wejście:}}
\algrenewcommand\algorithmicensure{\textbf{Wyjście:}}
\algrenewcommand\algorithmicfor{\textbf{dla}}
\algrenewcommand\algorithmicdo{\textbf{wykonaj}}
\algrenewcommand\algorithmicif{\textbf{jeżeli}}
\algrenewcommand\algorithmicthen{\textbf{to}}
\algrenewcommand\algorithmicelse{\textbf{w przeciwnym razie}}
\algrenewcommand\algorithmicend{\textbf{koniec}}
\algrenewcommand\algorithmicreturn{\textbf{zwróć}}
```
Wstaw je raz w preambule (są w `wzor/wzor_podglad.tex`).

## Zestawienie elementów graficznych rozdz. 4–7

| Nr | Element | Plik w `praca/rysunki/` | Status |
|---|---|---|---|
| Rys. 4.1 | wymiary znacznika Π | `znacznik_pi_wymiary.pdf` | ✅ |
| Rys. 4.2 | ERD (6 tabel) | `baza_erd.pdf` | ✅ zaktualizowany 28.10 |
| Rys. 4.3 | diagram klas | `diagram_klas.pdf` | ✅ zaktualizowany 28.10 |
| Rys. 4.4 | okno aplikacji z obszarami 1–4 | `interfejs_rejestracja.png` | ✍ zrzut (lista w `07_…`) |
| Alg. 5.1 | rejestracja | w tekście | ✅ |
| Rys. 5.1 | folia na zdjęciu i termowizji, kontury po rejestracji (para 14) | `rejestracja_para14.pdf` | ✅ |
| Tab. 5.1 | parametry uczenia M1 i M3 | w tekście | ✅ |
| Rys. 5.2 | krzywe uczenia M1 (ISIC 2018) | `panderm_trening.png` | ✅ (z Twoich wyników) |
| Alg. 5.2 | przeniesienie ROI i piksele | w tekście | ✅ |
| Tab. 6.1 | E1 i E2 | w tekście | ✅ |
| Rys. 6.1 | E4 – TRE czterech metod | `wyk_e4_tre.pdf` | ✅ |
| Rys. 6.2 | Dice M1 / M3 / detektor | `wyk_segmentacja.pdf` | ✅ |
| Tab. 6.2 | miary segmentacji | w tekście | ✅ |
| Rys. 6.3 | E2 a TRE | `wyk_e2_tre.pdf` | ✅ |
| Rys. 6.4 | para 14: maski E2, nałożenie w powiększeniu | `wyniki_para14.pdf` | ✅ |
| Tab. 6.3 | parametry znamion i piksele | w tekście | ✅ |
| Rys. 6.5 | piksele znamienia pary 14 | `piksele_para14.png` | ✅ |
| Tab. 6.4 | testy funkcjonalne | w tekście | ✅ (wynik z VM – potwierdź u siebie) |

Wykresy odtworzysz poleceniem: `python praca\rysunki\wykresy_wyniki.py "Claude outputs\dane_rozdz6" praca\rysunki` (Python z matplotlib, np. środowisko aplikacji).
