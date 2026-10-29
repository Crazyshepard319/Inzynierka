# Plan pracy: analiza stanu, literatura, spis treści (26.10.2026)

Status: spis treści zaakceptowany (26.10) z poprawkami (SQLite, dodatki w limicie, bez dodatku C); wariant B (U-Net dla termowizji) i baza SQLite **zrobione 26.10** – szczegóły i wyniki: `claude/notatki_unet_e2_baza.md`. Bibliografia propozycji: `claude/propozycje_v2.bib`. **Przydział literatury do rozdziału 2 – sekcja ★ poniżej.**

## ★ Przydział literatury do rozdziału 2 „Analiza stanu wiedzy” – wersja aktualna (26.10.2026)

Decyzje z 26.10: **usunięte z pracy** Karami i in. 2017 (arXiv, bez recenzji, jedna modalność), Gaens i in. 1998 (rejestracja niesztywna – nie dotyczy systemu), Zhu i in. 2023 (teledetekcja). Roche i in. 1998 – opcjonalny. **Pozycje B i C nie są używane** – w pracy zostaje 13 artykułów A + Twoje (★). Streszczenia wszystkich 23: `praca/materialy/03_streszczenia_artykulow.md`.

**Klucze cytowań (27.10).** W tekście pracy (`\cite`) obowiązują klucze z Twojego `.bib` (`praca/wzor/literatura_wzor.bib`, styl `acm.bst`). Karty i plan używają kluczy autor–rok; przejście:

| Klucz w kartach | Klucz w `\cite` |
|---|---|
| `celebi2019` | `dermoscopy` |
| `zhang2023` | `deep-learning` |
| `herman2011` | `visualization-detection-cancer` |
| `ring2012` | `infared-thermal-imaging` |
| `roche1998` | `correlation-ratio` |
| `hu2018` | `neural-networks` |
| `maurya2021` | `non-contact-breathing-monitoring` |
| `han2013` | `visible-and-infared` |
| `chen2021` | `deep-learning-in-registration` |

Pozostałe klucze (`magalhaes2019`, wszystkie pozycje A) są takie same w kartach i w `.bib`.

Oznaczenia: **★** – Twój artykuł (`praca/literatura/Ostatecznie użyte/`, klucz autor–rok, w `\cite` – klucz z tabeli powyżej; pełne wpisy w `praca/wzor/literatura_wzor.bib`); **(A)** – nowy artykuł (`praca/literatura/nowe_artykuły/`, klucz w `claude/propozycje_v2.bib`). Budżet rozdziału: ≤ 8 stron.

**Skutek rezygnacji z B/C (decyzje 26.10)** – elementy systemu bez własnego źródła:
- informacja wzajemna (badanie E4) – zostaje; cytować ogólnie przez `zitova2003`/`roche1998`, wariant Mattesa tylko jako metryka SimpleITK (`MattesMutualInformation`), bez cytatu;
- GrabCut – nazwy nie podawać; pisać ogólnie, np. „krawędź folii doprecyzowano segmentacją interaktywną z OpenCV”;
- transformer wizyjny (ViT) – tylko jako koder PanDerm, przez `yan2025panderm`;
- Bland–Altman – usunięty z pracy; zgodność pól zmian opisać prostymi statystykami (średnia różnica, SD, stosunek pól), bez nazwy metody i wykresu; kod zostaje;
- segmentacja termowizji (Mazur-Milecka 2020, praca promotorki) – nie dodawać;
- wzorzec-maska znacznika w IR (Vidas 2012) – opisać jako własne rozwiązanie, bez cytatu.

### 2.1 Obrazowanie zmian skórnych (≈1,5 s.)

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Ring i Ammer 2012 (`ring2012`) | ★ | Zasada termografii, emisyjność skóry 0,96–0,98; zastosowania kliniczne; wiarygodność zależy od standaryzacji i powtarzalnego wyznaczania ROI. |
| Herman i Pirtini Cetingul 2011 (`herman2011`) | ★ | Termografia dynamiczna (schłodzenie, sekwencja IR); bez schłodzenia zmiana niewidoczna na termogramie; rozdzielczość kamery krytyczna dla małych zmian. |
| Magalhaes i in. 2019 (`magalhaes2019`) | ★ | Termografia statyczna vs dynamiczna: 46 zmian (16 czerniaków, 30 znamion), SVM – dokładność 84,2%, czułość 91,3%; aklimatyzacja 10 min w 21 ± 1 °C; ROI ręcznie (40 × 40 px). Krótko – temperatury nie są częścią systemu. |
| Celebi i in. 2019 (`celebi2019`) | ★ | Dermatoskopia i analiza obrazów dermatoskopowych; zdjęcie kliniczne i dermatoskopia jako techniki komplementarne. Krótko. |
| Zhang i Demiris 2023 (`zhang2023`) | ★ | Jedno zdanie: obraz widzialny niesie teksturę, podczerwony – temperaturę (przejście do 2.2). |

### 2.2 Rejestracja obrazów wielomodalnych (≈2,5 s.)

**2.2.1 Modele transformacji i miary podobieństwa**

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Zitová i Flusser 2003 (`zitova2003`) | (A) | Definicja i etapy rejestracji; metody oparte na cechach i na intensywności; modele transformacji (sztywna → podobieństwa → afiniczna → projekcyjna). |
| Evangelidis i Psarakis 2008 (`evangelidis2008`) | (A) | Maksymalizacja rozszerzonego współczynnika korelacji (ECC) – metoda w `dopasowanie3.py` (afiniczna / homografia). |
| Roche i in. 1998 (`roche1998`) | ★ opcjonalny | Stosunek korelacyjny; niewypukłość funkcji kosztu miar statystycznych – tylko jeśli miary statystyczne opisujesz szerzej niż jednym akapitem. |

**2.2.2 Rejestracja RGB–termowizja i znaczniki referencyjne**

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Oniga i in. 2026 (`oniga2026`) | (A) | Najbliższa praca: rejestracja VIS/NIR/termowizja zmian skórnych z kwadratowym znacznikiem na skórze; 155 trójek od 62 pacjentów; termowizja–VIS trudniejsza niż NIR–VIS. |
| González-Pérez i in. 2021 (`gonzalezperez2021`) | (A) | 4 metody rejestracji termowizja–VIS (stopa cukrzycowa): afiniczna najlepsza (Dice 0,982), więcej stopni swobody ≠ lepiej; ocena masek Dice/IoU. |
| Herman i Pirtini Cetingul 2011 (`herman2011`) | ★ | Naklejany znacznik kwadratowy – narożniki do rejestracji zdjęcia z sekwencją IR; obrys zmiany przenoszony z obrazu widzialnego. |
| Han i in. 2013 (`han2013`) | ★ | Intensywności IR i ViS nie są powiązane; punkty SURF/Harris niepowtarzalne między modalnościami; transformacja z linii wymaga prostoliniowych struktur. |
| Maurya i in. 2021 (`maurya2021`) | ★ | Szablon kalibracyjny, wstępne dopasowanie skali, średni błąd 1,8 px (50 par); ROI w RGB przenoszony na termogram. |
| Zhang i Demiris 2023 (`zhang2023`) | ★ | Jedno zdanie: dokładne wyrównanie par widzialne–podczerwone to otwarty problem. |

**2.2.3 Metody oparte na uczeniu głębokim**

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Chen i in. 2021 (`chen2021`) | ★ | Przegląd głębokiej rejestracji: U-Net do pól deformacji, GAN do translacji modalności, brak danych jako bariera. Wystarcza jako główne źródło punktu. |
| Hu i in. 2018 (`hu2018`) | ★ krótko | Przykład: rejestracja słabo nadzorowana (etykiety tylko w treningu). Przy braku miejsca – pominąć. |
| Oniga i in. 2026 (`oniga2026`) | (A) | Głęboka rejestracja w dermatologii (punkty na znaczniku) – wymaga zbioru uczącego, którego tu nie ma. |
| Zhang i Demiris 2023 (`zhang2023`) | ★ | Jedno zdanie: wspólne uczenie rejestracji i fuzji jako kierunek badań. |

**2.2.4 Fuzja i wizualizacja nałożenia**

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Zhang i Demiris 2023 (`zhang2023`) | ★ | Poziomy fuzji (piksele, cechy, decyzje); fuzja pikselowa wymaga dokładnej rejestracji. |
| Maurya i in. 2021 (`maurya2021`) | ★ | Nakładanie zarejestrowanej mapy termicznej na obraz RGB. |

### 2.3 Segmentacja obrazów medycznych (≈2 s.)

**2.3.1 Metody klasyczne**

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Celebi i in. 2019 (`celebi2019`) | ★ | Segmentacja jako pierwszy etap analizy; trudności: włosy, oświetlenie. |
| Mirikharaji i in. 2023 (`mirikharaji2023`) | (A) | Metody sprzed głębokiego uczenia: progowanie adaptacyjne, kontury aktywne, rozrost obszaru, klasteryzacja, SVM – oparte na cechach projektowanych ręcznie (s. 2 PDF). Detekcję znacznika w systemie opisać jako metodę klasyczną; segmentację interaktywną z OpenCV – bez nazwy GrabCut. |

**2.3.2 U-Net i architektury koder–dekoder**

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Ronneberger i in. 2015 (`ronneberger2015`) | (A) | U-Net: koder–dekoder, połączenia skrótowe, augmentacja, mało danych – podstawa modelu M3. |
| Mirikharaji i in. 2023 (`mirikharaji2023`) | (A) | Przegląd głębokiej segmentacji zmian skórnych: architektury, funkcje straty, zbiory, metryki. |
| Chen i in. 2021 (`chen2021`) | ★ | Odwołanie: U-Net stosowany też w rejestracji (2.2.3). |

**2.3.3 Modele bazowe w dermatologii i zbiory danych**

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Yan i in. 2025 – PanDerm (`yan2025panderm`) | (A) | Model bazowy: ok. 2,1 mln obrazów z 11 źródeł i 4 modalności; segmentacja z dekoderem UperNet (ISIC 2018, HAM10000). |
| Xiao i in. 2018 – UperNet (`xiao2018upernet`) | (A) | Dekoder UperNet (piramida cech + moduł PPM). |
| Tschandl i in. 2018 – HAM10000 (`tschandl2018`) | (A) | Wymagany przez organizatorów ISIC 2018 cytat przy korzystaniu z ich danych (trening PanDerm). |
| Codella i in. 2019 – ISIC 2018 (`codella2019`) | (A, arXiv) | Drugi wymagany cytat (opis wyzwania, zadanie 1: segmentacja); jedyny wyjątek od źródeł recenzowanych. PDF: `nowe_artykuły/codella2018.pdf` (arXiv 1902.03368, zweryfikowany 26.10); plik `codella2019.pdf` to ISIC 2017 – nieużywany. Do 2.3.3/2.4: Jaccard progowany (próg 0,65, zgodność ekspertów 0,786), najlepszy wynik 0,802, porażki na ponad 10% obrazów. |

**2.3.4 Segmentacja obrazów termowizyjnych**

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Ring i Ammer 2012 (`ring2012`) | ★ | Powtarzalne wyznaczanie ROI na termogramach. |
| Herman 2011, Magalhaes 2019 | ★ | Zmiana niewidoczna na termogramie statycznym → w termowizji segmentuje się znacznik (uzasadnienie modelu M3). |

### 2.4 Miary oceny rejestracji i segmentacji (≈1,25 s.)

| Artykuł (klucz) | Status | Co z niego wziąć |
|---|---|---|
| Taha i Hanbury 2015 (`taha2015`) | (A) | Definicje i dobór miar: Dice, IoU, HD/HD95, średnia odległość konturów (ASSD). |
| Maier-Hein i in. 2024 – Metrics Reloaded (`maierhein2024`) | (A) | Dobór miar do problemu; łączenie miary pokrycia z miarą brzegową. |
| Fitzpatrick i in. 1998 (`fitzpatrick1998`) | (A) | TRE – błąd rejestracji w punktach docelowych (badanie E1). |
| González-Pérez i in. 2021 (`gonzalezperez2021`) | (A) | Ocena rejestracji przez Dice/IoU masek – odpowiednik badania E2. |
| Maurya 2021 (★) / Oniga 2026 (A) | – | Inne miary rejestracji w literaturze (błąd w pikselach, SSIM/MI) – kontrast z TRE w mm. |

### 2.5 Podsumowanie i luka badawcza (≈0,75 s.)

Tabela porównawcza prac RGB–termowizja: Herman 2011 ★, Han 2013 ★, Maurya 2021 ★, González-Pérez 2021 (A), Oniga 2026 (A) i niniejsza praca. Kolumny: zastosowanie, źródło korespondencji (znacznik / cechy / intensywność), miara oceny, niezależna weryfikacja zgodności ROI. Luka: brak systemu, który rejestruje zdjęcie z telefonu z termogramem na podstawie znacznika i weryfikuje zgodność ROI modelami segmentacji dedykowanymi każdej modalności (E2), bez adnotacji.

### Podsumowanie liczbowe

- **Twoje artykuły w pracy (10):** Herman 2011, Maurya 2021, Han 2013, Ring 2012, Magalhaes 2019, Celebi 2019, Zhang 2023, Chen 2021, Hu 2018 (krótko), Roche 1998 (opcjonalnie).
- **Usunięte (3):** Karami 2017, Gaens 1998, Zhu 2023.
- **A (13, PDF w `nowe_artykuły/`):** zitova2003, evangelidis2008, oniga2026, gonzalezperez2021, ronneberger2015, mirikharaji2023, yan2025panderm, xiao2018upernet, tschandl2018, codella2019, taha2015, maierhein2024, fitzpatrick1998.
- **B i C – nie są używane** (decyzja 26.10).


## 1. Stan projektu a stan tekstu

Kod (folder `Inzynierka/projekt`) realizuje cały system: 6 etapów (`analiza/system.py`: wejście → rejestracja → segmentacja → przeniesienie ROI → pomiary → raport), GUI w customtkinter z 6 zakładkami (`aplikacja.py`), potok wsadowy (`potok_pary.py`), raport zbiorczy z tabelami LaTeX (`raport_zbiorczy.py`).
Dane: 94 pary RGB–termowizja, 34 znamiona, adnotacje CVAT, foldy po znamionach. Wyniki (n = 92): TRE mediana 0,61 mm; Dice otworu znacznika 0,948; PanDerm vs CVAT Dice 0,870 ± 0,103 (mediana 0,896); E4: ECC mediana 0,62 mm vs MI Mattesa 3,47 mm.

PDF pracy (wersja z promotorką) opisuje **stary system**: rozdz. 2 – wymagania pod SimpleITK (20–30 s), stary GUI; rozdz. 3 – Otsu/HSV/kolistość + SimpleITK MI (dziś tylko metoda porównawcza E4). Rozdz. 4 i 5 puste. Brak: segmentacji, miar, bazy danych, diagramu klas, testów, instrukcji.

Do poprawy przy okazji:
- „Azam i współautorzy [8]” (podrozdz. 1.2.2 i 1.3.1) – Azam nie ma w bibliografii, [8] to Han.
- Rozdzielczość termowizji: tekst podaje 640×480 (FLIR A655sc), seria z 23.10 ma 320×240 – uzupełnić model kamery.
- `rozdzial1_skrocony.tex`: „znacznik o dowolnym kształcie, bez wyróżnionych punktów” – nieaktualne (Π, 8 narożników, skala mm, TRE).
- `rozdzial1_skrocony.tex` cytuje `karami2017`, `gaens1998`, `zhu2023` – usunąć te cytowania (decyzja 26.10).

| Wym. | Kod | Tekst |
|---|---|---|
| 1 Stan wiedzy: rejestracja / segmentacja (U-Net) / metryki | – | rejestracja tak; **segmentacja i metryki: brak artykułów** |
| 2 Wymagania F/NF | – | nieaktualne |
| 3 Technologie, baza danych, UI | gotowe | technologie stare, baza – brak |
| 4 Modele segmentacji per modalność | PanDerm+UperNet (ISIC 2018, test Dice 0,899), kandydaci; termowizja: detektor znacznika | brak |
| 5 Miary zgodności ROI | Dice, IoU, HD95, ASSD, środki, pola, TRE | brak |
| 6 Weryfikacja, wnioski | raport zbiorczy, tabele.tex | brak |
| 7 Dokumentacja + instrukcja | README | brak |
| 8 Moduł rejestracji + overlay | gotowe (`dopasowanie3.py`) | opis starej metody |
| 9 Prototyp GUI, UC, klasy, baza | gotowe | UC stary; klasy, baza – brak |
| 10 Opis analiz | – | częściowo |

## 2. Literatura – werdykt

Tak, trzeba dodać. 13 obecnych pozycji pokrywa termografię, dermatoskopię, rejestrację i fuzję, ale **żadna nie dotyczy segmentacji ani miar jej oceny** (wymaganie 1 wprost), a metody faktycznie użyte (ECC, GrabCut, PanDerm, UperNet, TRE) nie mają źródeł.

Uwagi o obecnych (decyzja 26.10): **usunięte** Karami [5] (arXiv, bez recenzji – zastępuje go Zitová i Flusser 2003), Gaens [7] (rejestracja niesztywna) i Zhu [12] (teledetekcja); Roche [6] opcjonalny; Hu [9] krótko. Pozostałe 9 zostaje.

Priorytet A (konieczne): evangelidis2008 (ECC), fitzpatrick1998 (TRE), oniga2026 (VIS/NIR/TH w dermatologii ze znacznikiem – najbliższa praca), gonzalezperez2021 (RGB–IR w medycynie, ocena Dice/IoU), ronneberger2015 (U-Net), mirikharaji2023 (przegląd segmentacji zmian skórnych), yan2025panderm, xiao2018upernet, taha2015, maierhein2024, tschandl2018 + codella2019 (dane ISIC 2018 – wymagane cytaty), zitova2003 (klasyfikacja metod rejestracji).
B i C: **nie są używane** (decyzja 26.10). Przydział do podrozdziałów: sekcja ★ na początku pliku. I (narzędzia do rozdz. 5, nie dotyczy rozdz. 2): lowekamp2013 (SimpleITK), paszke2019 (PyTorch), loshchilov2019 (AdamW), dettmers2022 – do potwierdzenia, czy zostają.

## 3. Proponowany spis treści (~35 stron)

Streszczenie, Abstract, Wykaz skrótów
1. Wstęp (≈2 s.) – 1.1 Motywacja; 1.2 Cel i zakres pracy; 1.3 Struktura pracy
2. Analiza stanu wiedzy (≤8 s.) – 2.1 Obrazowanie zmian skórnych (RGB, dermatoskopia, termografia statyczna i dynamiczna); 2.2 Rejestracja obrazów multimodalnych (2.2.1 Modele transformacji i miary podobieństwa; 2.2.2 Rejestracja RGB–termowizja i znaczniki referencyjne; 2.2.3 Metody głębokie; 2.2.4 Fuzja i wizualizacja nałożenia); 2.3 Segmentacja obrazów medycznych (2.3.1 Metody klasyczne; 2.3.2 U-Net i architektury koder–dekoder; 2.3.3 Modele bazowe w dermatologii i zbiory danych; 2.3.4 Segmentacja obrazów termowizyjnych); 2.4 Miary oceny rejestracji i segmentacji; 2.5 Podsumowanie i luka
3. Analiza projektowa (≈4,5 s.) – 3.1 Założenia i ograniczenia; 3.2 Wymagania funkcjonalne; 3.3 Wymagania pozafunkcjonalne; 3.4 Przypadki użycia; 3.5 Architektura systemu
4. Projekt systemu (≈4,5 s.) – 4.1 Dobór technologii; 4.2 Projekt znacznika referencyjnego Π; 4.3 Projekt bazy danych (SQLite, diagram ERD); 4.4 Diagram klas; 4.5 Projekt interfejsu użytkownika
5. Implementacja (≈6 s.) – 5.1 Akwizycja i przygotowanie danych; 5.2 Moduł rejestracji (5.2.1 Wstępne przetwarzanie; 5.2.2 Detekcja znacznika w obu modalnościach; 5.2.3 Inicjalizacja i doprecyzowanie ECC; 5.2.4 Resampling i wizualizacja nałożenia); 5.3 Modele segmentacji (5.3.1 Zdjęcie RGB: PanDerm + UperNet; 5.3.2 Obszar ze znacznika i wybór kandydatów; 5.3.3 Termowizja: U-Net M3 – segmentacja znacznika); 5.4 Przeniesienie ROI i skala metryczna; 5.5 Pomiary i miary zgodności; 5.6 Baza danych, raport i aplikacja
6. Testy i wyniki (≈6,5 s.) – 6.1 Zbiór danych i protokół oceny; 6.2 Dokładność rejestracji i porównanie metod; 6.3 Jakość segmentacji w obu modalnościach; 6.4 Zgodność ROI między modalnościami; 6.5 Parametry ilościowe znamion; 6.6 Testy funkcjonalne; 6.7 Dyskusja i ograniczenia
7. Podsumowanie (≈1,5 s.) – 7.1 Realizacja celów; 7.2 Wnioski; 7.3 Dalsze prace
Wykaz literatury, rysunków, tabel
Dodatek A: Instrukcja użytkownika (≈2 s.); Dodatek B: Dokumentacja techniczna (≈2 s.)

## Decyzje Mateusza (26.10)
- Baza danych: **SQLite** – zrobione (`analiza/baza.py`, `dane/baza.sqlite`, ERD: `praca/rysunki/baza_erd.png`); rozdz. 4.3 = projekt bazy + diagram ERD, implementacja w 5.6.
  Propozycja tabel: `znamie` (id, fold), `para` (id, znamie_id, plik_rgb, plik_termal, oryginal_heic, oryginal_seq, data), `adnotacja` (para_id, modalnosc, obiekt, sciezka_maski, narozniki), `analiza` (id, para_id, data, model_rejestracji, macierz_T, sciezka_raportu), `miara` (analiza_id, grupa, nazwa, wartosc, jednostka).
- Dodatki **liczą się** do limitu 30–40 stron. **Bez dodatku C.**
- Nowy budżet: Wstęp 2 · Stan wiedzy 8 · Analiza projektowa 4 · Projekt 4,5 · Implementacja 6 · Testy 6,5 · Podsumowanie 1,5 · Dodatek A (instrukcja) 2 · Dodatek B (dokumentacja) 2 ≈ 36,5 s.

## Model segmentacji dla termowizji – wybrany wariant B (zrobione 26.10)
Stan: RGB – znamię: PanDerm + UperNet (trenowany); RGB – znacznik: detektor klasyczny (barwa/tekstura + GrabCut); termowizja – znacznik: detektor klasyczny (ciemne/teksturowane obszary + wzorzec Π); termowizja – znamię: niewidoczne.
Problemy: (1) wymaganie 4 mówi o *treningu* modeli dla każdej modalności – dla termowizji nie ma wytrenowanego modelu; (2) automatyczna zgodność masek znacznika (Dice wewnętrzny z log-u rejestracji, stosunek pól otworu) porównuje te same maski, na których ECC wyznaczyło T – wynik jest wysoki z konstrukcji, więc nie jest niezależną weryfikacją. Niezależna jest tylko ocena względem CVAT (E1), która nie jest częścią systemu.
- Wariant A (bez nowej pracy): detektor klasyczny opisany jako metoda segmentacji dedykowana termowizji; weryfikacja względem CVAT. Ryzyko: brak treningu dla termowizji (wym. 4).
- Wariant B (zalecany, ok. 1–2 dni): mały U-Net segmentujący znacznik na termowizji, uczony na 94 maskach `maska_znacznik_termal.png` z CVAT, 5-krotna walidacja po znamionach (`znamiona.csv`). W systemie: maska znacznika ze zdjęcia przeniesiona przez T vs maska z U-Netu – model nie bierze udziału w wyznaczaniu T, więc porównanie jest niezależne. Dodaje 5.3.3 i część 6.3.

## Uwaga promotora z 28.10 – piksele znamienia na termowizji (zrobione 28.10)
- Dla każdego piksela termowizji objętego maską znamienia przeniesioną ze zdjęcia: x, y (kolumna, wiersz obrazu 320 × 240) i **intensywność = surowa wartość detektora z nagrania .SEQ** (uint16, pierwsza klatka; nie °C, nie wartość z `termal.jpg`).
- Kod: `analiza/pomiary.py` (`piksele_znamienia`, `statystyki_intensywnosci`, CSV), `analiza/dane.py` (`intensywnosc_surowa`: `dane/pary/N/termal_surowe.npy` albo odczyt SEQ przez flirpy), `system.zmierz()`, tabela `piksel` w bazie (schemat v2), sekcja i obraz `piksele_termal.png` w raporcie, zakładka „Piksele” w aplikacji, `baza_danych.bat eksport_piksele`.
- Piksel „w masce”, gdy znamię pokrywa ≥ 50% jego pola; CSV zawiera też piksele częściowe z kolumną `ulamek`.
- `termal_surowe.npy` wygenerowane dla 94 par (zgodne z `termal.jpg`). Do zrobienia na Windows: `potok_pary.bat 1-94 --z_zapisanych` (raporty, CSV i wpisy w bazie).
- Do pracy: nowe WF w rozdz. 3, tabela `piksel` w ERD i opisie bazy (rozdz. 4), opis w rozdz. 5, przykład w rozdz. 6.

## Wzór rozdziałów 4–7, dodatków i streszczeń (28.10)
- `praca/wzor/`: rozdz. 4 (zaktualizowany: A320, flirpy, 6 tabel bazy), 5, 6, 7, dodatki A i B, Streszczenie + Abstract, wykaz skrótów; rozdz. 1 i 3 uzupełnione o WF15 i kamerę FLIR A320 (obiektyw 18 mm, odczyt z nagrań .SEQ).
- Plany i zwroty: `materialy/06_plan_zwroty_rozdzialy_4_7.md`, `materialy/07_plan_dodatki_streszczenie_skroty.md`.
- Nowe rysunki w `praca/rysunki/`: wykresy E4, E2–TRE, segmentacji (`wykresy_wyniki.py`), rejestracja i wyniki pary 14, piksele pary 14, krzywe uczenia M1; zaktualizowane ERD, diagram klas, potok, architektura.
- Testy: `projekt/testy/test_systemu.py` + `uruchom_testy.bat` (18 testów; w VM 17 zaliczonych, T09 pominięty – brak wag U-Netu).
- Decyzje 28.10: narzędzia (OpenCV, PyTorch, SimpleITK, AdamW…) bez cytatów; zrzuty ekranu jako miejsca w tekście + lista; punkt „Podsumowanie oraz Abstract” = Streszczenie PL + Abstract EN.
- Podgląd całości (klasa report): rozdz. 1–7 + dodatki ≈ 45 s. – powyżej limitu 40; lista cięć w `wzor/README.md`.

## Materiały do pisania (26.10)
- `praca/materialy/`:
  - `01_materialy_rozdzialy_1_3_4.md` – co napisać i zwroty;
  - `02_zwroty_analiza_stanu_wiedzy.md`;
  - `03_streszczenia_artykulow.md` – 23 karty;
  - `04_rysunki_tabele_dane_rozdzial2.md` + `rysunki_z_artykulow/` (30 wycinków);
  - `05_rysunki_tabele_rozdzialy_1_3_4.md`.
- `praca/rysunki/`: diagram przypadków użycia, architektura, potok przetwarzania, diagram klas (.puml/.pdf/.png), znacznik Π z wymiarami, para 14 (RGB + termowizja).
- `praca/wzor/`: wzór rozdziałów 1–4 w LaTeX-u + `literatura_wzor.bib` + podgląd PDF.

## Otwarte pytania
- Do potwierdzenia z promotorką:
  - temperatury w raporcie;
  - grupa użytkowników;
  - pozycje I (SimpleITK, PyTorch, AdamW) w rozdz. 5.
