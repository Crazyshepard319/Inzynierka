# Streszczenia artykułów do rozdziału 2 „Analiza stanu wiedzy” – materiały (pkt 3)

Stan: 26.10.2026. Zakres: **23 artykuły** – 13 z grupy A (`praca/literatura/nowe_artykuły/`) i 10 Twoich (★, `praca/literatura/Ostatecznie użyte/`). Pozycji B i C nie ma w pracy (decyzja z 26.10). Kolejność: według podrozdziałów rozdziału 2.

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

To są **materiały, nie gotowy tekst**. Każda karta ma tę samą budowę:

- **Streszczenie** – o czym jest artykuł i co z niego wynika (do zrozumienia, nie do przepisania);
- **Co zawrzeć w pracy** – konkretne informacje z przypisaniem do podrozdziału;
- **Liczby i fakty do cytowania** – dokładne wartości ze stroną;
- **Związek z systemem z pracy** – jak artykuł uzasadnia albo kontrastuje decyzję w systemie;
- **Uważaj** – czego nie twierdzić, ograniczenia, błędy w samym artykule;
- **Rysunki i tabele (kandydaci)** – tylko te, które są w artykule (numer, strona, podpis). Ich ocenę i wybór do rozdziału zawiera osobny plik z pkt 4.

## Jak czytać numery stron

- **„(s. N)” = numer strony w pliku PDF** (licznik przeglądarki PDF), żeby szybko znaleźć miejsce. Nie wpisuj go do pracy jako numeru strony.
- **„(s. N/M)”** (tylko U-Net i UperNet) = strona przyciętego PDF / strona w tomie konferencyjnym.
- Liczby z innych artykułów oznaczono kluczem, np. „(mirikharaji2023, s. 28)”.
- Jeśli w pracy chcesz podać stronę (`\cite[s.~978]{zitova2003}`), przelicz ją na stronę drukowaną:

| Klucz | Plik PDF | Strony drukowane | Strona drukowana z PDF |
|---|---|---|---|
| zitova2003 | nowe_artykuły/zitova2003.pdf | 977–1000 | 976 + N |
| evangelidis2008 | nowe_artykuły/evangelidis2008.pdf | 1858–1865 | 1857 + N |
| fitzpatrick1998 | nowe_artykuły/fitzpatrick1998.pdf | 694–702 | 693 + N |
| roche1998 | Ostatecznie użyte/The Correlation Ratio[6].pdf | 1115–1124 | 1114 + N |
| han2013 | Ostatecznie użyte/Visible and infrared[8].pdf | 42–51 | 41 + N |
| maurya2021 | Ostatecznie użyte/Non-contact breathing[10].pdf | 1107–1122 | 1106 + N |
| celebi2019 | Ostatecznie użyte/Dermoscopy Image[3].pdf | 474–478 | 473 + N |
| zhang2023 | Ostatecznie użyte/Visible Deep Learning[4].pdf | 10535–10554 | 10534 + N |
| magalhaes2019 | Ostatecznie użyte/dynamic thermal imaging.pdf | 1700–1705 | 1699 + N |
| hu2018 | Ostatecznie użyte/Weakly-supervised convolutional[9].pdf | 1–13 | N |
| ring2012 | Ostatecznie użyte/Infared thermal[2].pdf | R33–R46 | R(31 + N) – s. 1 PDF to okładka wydawcy |
| chen2021 | Ostatecznie użyte/Deep learning[11].pdf | art. 012003 | N − 1 – s. 1 PDF to okładka wydawcy |
| ronneberger2015 | nowe_artykuły/ronneberger2015_unet_8str.pdf | 234–241 | 233 + N (podane jako M) |
| xiao2018upernet | nowe_artykuły/xiao2018_upernet_17str.pdf | 432–448 | 431 + N (podane jako M) |
| herman2011, taha2015, tschandl2018, gonzalezperez2021, oniga2026, mirikharaji2023 | odpowiednio nowe_artykuły / Ostatecznie użyte | numer artykułu, strony 1…n | N |
| yan2025panderm | nowe_artykuły/yan2025panderm.pdf – **wersja arXiv v3** | Nature Medicine 31, 2691–2702 | nie przeliczaj – cytuj bez strony |
| maierhein2024 | nowe_artykuły/maierhein2024.pdf – **wersja arXiv v8** | Nature Methods 21, 195–212 | nie przeliczaj – cytuj bez strony |
| codella2019 | nowe_artykuły/**codella2018.pdf** (arXiv:1902.03368v2 – ISIC 2018) | 1–12 | N |

Uwaga do PanDerm i Metrics Reloaded: w `.bib` są wersje czasopiśmiennicze, a PDF-y to preprinty arXiv. Treść jest zbliżona, ale numeracja stron, rysunków dodatkowych i czasem liczby mogą się różnić – liczby cytuj z ostrożnością albo sprawdź w wersji z czasopisma.

## Szybki przegląd

| Podrozdział | Klucz | Grupa | Po co w pracy (1 zdanie) |
|---|---|---|---|
| 2.1 | ring2012 | ★ | Podstawy termografii medycznej (emisyjność skóry, standaryzacja pomiaru, ROI). |
| 2.1 | herman2011 | ★ | Termografia dynamiczna zmian skórnych; bez schładzania zmiana jest niewidoczna; znacznik na skórze do rejestracji. |
| 2.1 | magalhaes2019 | ★ | Termografia statyczna vs dynamiczna w odróżnianiu znamion od czerniaków (kontekst kliniczny). |
| 2.1 | celebi2019 | ★ | Dermatoskopia i etapy automatycznej analizy obrazu zmiany (segmentacja jako pierwszy krok). |
| 2.2.1 | zitova2003 | A | Definicja i etapy rejestracji, modele transformacji, metody cechowe i intensywnościowe. |
| 2.2.1 | evangelidis2008 | A | Algorytm ECC – metoda rejestracji użyta w systemie. |
| 2.2.1 | roche1998 | ★ opcj. | Stosunek korelacyjny jako miara wielomodalna; tylko przy szerszym opisie miar statystycznych. |
| 2.2.2 | oniga2026 | A | Najbliższa praca: rejestracja VIS/NIR/termowizja zmian skórnych ze znacznikiem. |
| 2.2.2 | gonzalezperez2021 | A | Porównanie metod rejestracji termowizja–RGB; ocena przez Dice/IoU masek. |
| 2.2.2 | maurya2021 | ★ | Rejestracja RGB–termowizja z szablonem kalibracyjnym; ROI z RGB przenoszony na termogram. |
| 2.2.2 | han2013 | ★ | Dlaczego punkty charakterystyczne słabo działają między widzialnym a IR. |
| 2.2.3 | chen2021 | ★ | Przegląd głębokiej rejestracji – i dlaczego potrzebuje dużych zbiorów uczących. |
| 2.2.3 | hu2018 | ★ krótko | Rejestracja słabo nadzorowana (etykiety tylko w treningu) – przykład. |
| 2.2.4 | zhang2023 | ★ | Fuzja widzialne–podczerwień; fuzja pikselowa wymaga dokładnej rejestracji. |
| 2.3.2 | ronneberger2015 | A | U-Net – architektura modelu M3 (termowizja). |
| 2.3.2 | xiao2018upernet | A | Dekoder UperNet używany z koderem PanDerm. |
| 2.3.2, 2.3.3, 2.4 | mirikharaji2023 | A | Przegląd głębokiej segmentacji zmian skórnych: architektury, straty, zbiory, miary. |
| 2.3.3 | yan2025panderm | A | Model bazowy PanDerm – koder do segmentacji znamienia. |
| 2.3.3 | tschandl2018 | A | Zbiór HAM10000 (wymagany cytat ISIC 2018). |
| 2.3.3 | codella2019 | A (arXiv) | Wyzwanie ISIC 2018, Task 1 – dane do douczania PanDerm (wymagany cytat). |
| 2.4 | fitzpatrick1998 | A | Definicje FLE, FRE, TRE – podstawa badania E1. |
| 2.4 | taha2015 | A | Definicje i dobór miar segmentacji (Dice, IoU, HD95, ASSD). |
| 2.4 | maierhein2024 | A | Zasady doboru miar (Metrics Reloaded): miara pokrycia + miara brzegowa. |

## Znane błędy i niespójności w samych artykułach (sprawdzone w tekście)

- **oniga2026** – Table 4 („Final version”) ≠ Table 3/5; „4 przypadki ≈ 3,4%”, a 4/155 ≈ 2,6%.
- **gonzalezperez2021** – abstrakt: „Dice > 0,950 we wszystkich scenariuszach”, a w Table 1 jest 0,949 (homografia, 850 mm).
- **yan2025panderm** – 547 047 vs 537 047 kafelków; 200 vs 500 epok; n = 2074 / 7011 na wykresie vs 2594 w metodach.
- **taha2015** – zdanie „JAC is always larger than DICE” (s. 5) jest błędne (ze wzoru: JAC ≤ DICE) – nie cytować.
- **mirikharaji2023** – Table 1: HAM10000 „1113 non-melanomas, 8902 melanomas” (odwrócone) – nie cytować.
- **hu2018** – „all 9 median TREs are larger than 24 mm” vs 20,6 mm w Table 2 – cytować tabelę.
- **chen2021** – sprzeczne zdania o dokładności głębokiej rejestracji (s. 3 / 18 / 25).
- **codella2019** – zgłoszenia: abstrakt 115 / 25 / 159, wyniki 112 / 26 / 141; zdublowane numery rysunków (dwa „Fig. 2”, trzy „Fig. 4”).

## Uwagi o plikach

1. Opis ISIC 2018 (`codella2019`) jest w pliku `nowe_artykuły/codella2018.pdf`. Plik `codella2019.pdf` to praca o ISIC 2017 – w pracy nieużywana. Warto zamienić nazwy (propozycja w karcie `codella2019`).
2. `ronneberger2015_unet_8str.pdf` i `xiao2018_upernet_17str.pdf` to artykuły wycięte z tomów konferencyjnych.

---

## 2.1 Obrazowanie zmian skórnych

### Ring, Ammer, 2012 – Infrared thermal imaging in medicine
`ring2012` · Physiological Measurement, 33, R33–R46, 2012 · DOI: 10.1088/0967-3334/33/3/R33 · Podrozdział: 2.1, 2.3.4

**Streszczenie.** Przegląd (topical review) technologii termowizyjnej w medycynie, protokołów standaryzacji i zastosowań klinicznych (s. 2). Opisuje przejście od skanerów z chłodzonymi detektorami do kamer z matrycą detektorów (focal plane array, FPA) i mikrobolometrami, co poprawiło rozdzielczość przestrzenną (s. 3). Omawia normy IEC/ISO dla przesiewowego wykrywania gorączki, kontrolę jakości kamer i zasady prezentacji palet barw (s. 4–5). Podkreśla, że powtarzalność pozycji ciała i lokalizacji ROI wyraźnie wpływa na dokładność i precyzję pomiaru, a kształt, rozmiar i położenie ROI – na trafność diagnostyczną (s. 5). Przegląd zastosowań obejmuje m.in. zapalenia stawów, CRPS, zjawisko Raynauda, chirurgię płatów, gorączkę i nowotwory; czerniak jest łatwiej wykrywalny przy ogrzewaniu po schłodzeniu skóry (s. 11). Wniosek: standaryzacja musi obejmować także przetwarzanie obrazu i wybór powtarzalnych ROI (s. 12).

**Co zawrzeć w pracy.**
- 2.1: termogram to obraz rozkładu temperatury; skóra jest prawie ciałem doskonale czarnym (emisyjność 0,96–0,98), maksimum emisji 9–12 µm; skuteczne są zarówno detektory 2–5 µm, jak i bolometry do 15 µm (s. 3, 5–6).
- 2.1: termowizja daje tylko rozkład temperatury skóry, bez informacji z głębi ciała (s. 9–10).
- 2.1: czerniak to jedno z najstarszych zastosowań (1969); wcześniej wyniki były sprzeczne, nowsze badania pokazują różne wzorce zmian złośliwych i łagodnych, ale wymagają potwierdzenia na większych próbach (s. 11). Łącznik do `herman2011` i `magalhaes2019`.
- 2.3.4: ROI: atlas Glamorgan (24 pozycje ciała, 90 ROI); wpływ kształtu, rozmiaru i położenia ROI na wynik (s. 5); słaba powtarzalność ręcznego liczenia „gorących punktów”, sugestia wsparcia programowego (s. 8).
- 2.1: palety „iron” i „rainbow”; w medycynie zakres zwykle ok. 10 °C; skalę barw należy pokazywać przy obrazie (s. 4–5) – kontekst dla obrazów w palecie inferno.

**Liczby i fakty do cytowania.**
- Dawne skanery: 1–16 klatek/s, rozdzielczość temperaturowa 0,5 °C, przestrzenna ok. 5 mm przy polu 50 cm² (s. 3).
- Kamery FPA powszechne od lat 90. (s. 3).
- Próg niejednorodności matrycy 0,04% osiągalny tylko z korekcją programową (s. 4).
- Normy: IEC 2008 i ISO 2009 (przesiewowe wykrywanie gorączki) (s. 4); min. 9 pikseli w wewnętrznym kąciku oka (s. 10).
- Zalecane zewnętrzne źródła temperatury odniesienia, zwłaszcza dla niechłodzonych kamer (s. 4).
- Próba zimna: ponad 20 metod oceny; proponowany standard – woda 20 °C przez 1 min (s. 5).
- Termowizja w zastosowaniach niewojskowych od 1958 r. (s. 12).

**Związek z systemem z pracy.** Daje tło (2.1) i argument metodyczny: wynik termowizji zależy od powtarzalnego, dobrze zdefiniowanego ROI. System z pracy wyznacza ROI znamienia w TH automatycznie i powtarzalnie (przez rejestrację), zgodnie z postulatem standaryzacji przetwarzania i wyboru ROI.

**Uważaj.**
- Przegląd z 2012 r. – stan sprzętu i norm z tamtego czasu. Nie dotyczy rejestracji RGB–TH ani automatycznej segmentacji; cytować tylko jako tło i do standaryzacji ROI.
- s. 1 PDF to okładka IOP; strona czasopisma R33 = s. 2.

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 3): „(Left) Thermogram of lateral face recorded in 1995 with 320 × 240 pixels; (right) thermogram recorded in 2011 with a new 640 × 480 pixel infrared camera.” – wpływ rozdzielczości; przydatność: średnia (2.1; ta sama rozdzielczość co w pracy).
- Fig. 4 (s. 4): „The effects of stress on hand thermograms, (A) 10 min full normal recovery from 1 min immersion in water at 20 °C, (B) in a patient with Raynaud's phenomenon after 10 min…” – przykład termografii dynamicznej; niska/średnia.
- Fig. 2 (s. 3): „Thermograms of dorsal hand (left) recorded in 1990 with 240 × 320 pixels and right recorded in 2011 with modern focal plane array camera with 640 × 480 pixels.” – niska.
- Fig. 3 (s. 4): „(A) Chronic inflammation of the forefoot following a sports injury; (B) rheumatoid arthritis of one knee” – niska.

---

### Herman, Pirtini Cetingul, 2011 – Quantitative Visualization and Detection of Skin Cancer Using Dynamic Thermal Imaging
`herman2011` · Journal of Visualized Experiments, (51), e2679, 2011 · DOI: 10.3791/2679 · Podrozdział: 2.1, 2.2.2, 2.3.4

**Streszczenie.** Artykuł wideo z protokołem dynamicznej termografii do wykrywania czerniaka u pacjentów ze zmianą barwnikową zakwalifikowaną do biopsji (s. 1). Zmianę i otoczenie o średnicy 50 mm chłodzi się strumieniem zimnego powietrza przez 1 min, po czym co 2 s rejestruje się powrót temperatury trwający 3–4 min (s. 2). Zmiany nie widać w obrazie termowizyjnym bez chłodzenia, więc wokół niej przykleja się kwadratowy znacznik (s. 1). Narożniki znacznika wykrywa się na zdjęciu w świetle białym, wskazuje odpowiadające im punkty w referencyjnym obrazie IR i używa ich w kwadratowym modelu ruchu (quadratic motion model) do wyrównania sekwencji (s. 2). Zmianę segmentuje się interaktywnie metodą random walker, a jej obszar wyznacza w każdym zarejestrowanym obrazie IR (s. 2). Autorzy twierdzą, że wzmożoną aktywność metaboliczną czerniaka da się wykryć dynamicznym IR, a bez śledzenia ruchu nie zmierzyliby różnicy temperatur (s. 1, 3). Tekst nie zawiera wyników liczbowych.

**Co zawrzeć w pracy.**
- 2.1: termografia dynamiczna (bodziec zimna i faza powrotu) wobec statycznej; trudności dawnych prób opartych tylko na stanie ustalonym (s. 3).
- 2.2.2: prekursor rozwiązania z pracy: znacznik na skórze wokół znamienia, bo znamię jest niewidoczne w TH bez chłodzenia (s. 1); narożniki znacznika jako punkty orientacyjne (landmarks) do rejestracji zdjęcie–IR (s. 2).
- 2.3.4: segmentacja na obrazie widzialnym i przeniesienie obrysu na obrazy IR zamiast segmentacji zmiany w TH (s. 2).
- 2.1: rozdzielczość przestrzenna kamery IR jest krytyczna dla małych zmian (s. 3).

**Liczby i fakty do cytowania.**
- 68 720 rozpoznań czerniaka w USA w 2010 r., ok. 8650 zgonów (s. 1).
- Chłodzenie 1 min, obszar o średnicy 50 mm; powrót 3–4 min; obrazy IR co 2 s (s. 2).
- Kamera Merlin średniej podczerwieni 3–5 µm; zdjęcie Canon PowerShot G11; dermatoskop DermLite Foto System (s. 1–2).
- Kontrola temperatury pomieszczenia i skóry termoparami (s. 1).

**Związek z systemem z pracy.** Najbliższy historyczny odpowiednik potoku z pracy: znacznik → narożniki → rejestracja → przeniesienie obrysu z obrazu widzialnego na TH. Praca automatyzuje kroki, które tu są półręczne (punkty w IR, interaktywna segmentacja), i nie stosuje chłodzenia.

**Uważaj.**
- Brak liczb o dokładności rejestracji czy diagnozy – nie przypisywać im wyników ilościowych.
- Czy punkty w IR wskazywano ręcznie, nie wiadomo („we identified the corresponding points”, s. 2 – niepewne). Kamera MWIR z pomiarem temperatur – system z pracy temperatur nie mierzy.

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 2): „a) The infrared imaging system HRIS in the clinical trial room, b) photograph of the larger body surface area with a cluster of pigmented lesions and the template frame applied for imaging, c) reference infrared image of the region at ambient temperature, d) the same area after cooling and e) magnified section of the melanoma lesion and surroundings” – znacznik i obraz IR przed/po chłodzeniu; przydatność: wysoka (2.1, 2.2.2).
- Fig. 3 (s. 3): „Cooling the lesion and the surrounding skin tissue by blowing a stream of cold air from a vortex tube.” – średnia (2.1).
- Fig. 2 (s. 3): „Exam room with our thermal imaging system.” – niska.

---

### Magalhaes, Vardasca, Rebelo i in., 2019 – Distinguishing melanocytic nevi from melanomas using static and dynamic infrared thermal imaging
`magalhaes2019` · Journal of the European Academy of Dermatology and Venereology (JEADV), 33, 1700–1705, 2019 · DOI: 10.1111/jdv.15611 · Podrozdział: 2.1, 2.3.4

**Streszczenie.** Badanie kliniczne (IPO Porto): termogramy statyczne i dynamiczne (po schłodzeniu) czerniaków i znamion melanocytowych posłużyły do klasyfikacji uczeniem maszynowym (s. 1–2). Kamera FLIR E60sc 320 × 240; chłodzenie krążkiem aluminiowym przez 1 min, obraz przed bodźcem i co minutę do 5 min (s. 2). Analiza w ręcznie umieszczanym oknie 40 × 40 pikseli: statycznie profil temperatur po przekątnych, średnia i SD, dynamicznie maksymalna różnica temperatur centrum–obwód (s. 2–3). Zbiór: 46 zmian (16 czerniaków, 30 znamion) w analizie statycznej, 41 (12/29) w dynamicznej; rozpoznania potwierdzone histopatologicznie (s. 2–4). Najlepiej: SVM (SMO, jądro wielomianowe) na cechach statycznych – dokładność 84,2%, czułość 91,3% (s. 1, 5). Autorzy uznają klasyfikację za wykonalną, ale czułość i swoistość wymagają poprawy (s. 6).

**Co zawrzeć w pracy.**
- 2.1: definicje: termografia statyczna (bez stymulacji) i dynamiczna (po bodźcu chemicznym, termicznym lub mechanicznym) (s. 1).
- 2.1: zmiany łagodne zwykle hipotermiczne, złośliwe – hipertermiczne (s. 2); profil czerniaka z wyraźną „kopułą” w centrum (s. 4).
- 2.3.4: ROI w termogramie wyznaczany ręcznie – okno 40 × 40 px umieszcza i centruje użytkownik (s. 2); przykład braku automatycznej lokalizacji zmiany w TH, motywacja do przenoszenia ROI ze zdjęcia.
- 2.1: warunki akwizycji: aklimatyzacja 10 min, 21 ± 1 °C, wilgotność ≤ 50%, kalibracja ciałem doskonale czarnym (s. 2).
- 2.5: autorzy postulują łączenie termografii z innymi modalnościami, np. dermoskopią (s. 6).

**Liczby i fakty do cytowania.**
- FLIR E60sc: 320 × 240, NETD < 50 mK przy 30 °C, niepewność 2% odczytu; ciało czarne ISOTECH HYPERION R 982 (s. 2).
- Krążek aluminiowy: średnica 50 mm, wysokość 20 mm; bodziec 1 min (s. 2).
- Okno 40 × 40 px, część centralna 20 × 20 px; 41 cech statycznych, 14 dynamicznych; podział 60/40 (s. 2–3).
- Table 1 (s. 5): SMO-Poly (statyczne + AvT) ACC 84,2%, SN 91,3%; perceptron wielowarstwowy (statyczne + StdT) 84,2% / 77,8%; iBk k = 1 (dynamiczne) 70,6% / 33,3%; SMO-RBF, iBk k = 7, iBk k = √n – 64,7% / 0,0%.
- Najwyższa swoistość: perceptron wielowarstwowy, SP = 66,7% (s. 5).
- Średnia temperatura okna niższa dla czerniaków niż znamion; autorzy tłumaczą to małym rozmiarem czerniaków, czyli większym udziałem zdrowej skóry w oknie (s. 4).
- Nie wszystkie zmiany chłodzono (ryzyko urazu, brak dostępu) (s. 4).

**Związek z systemem z pracy.** Daje kontekst kliniczny termografii zmian barwnikowych (2.1). Pokazuje też, że ROI w TH wyznacza się ręcznie stałym oknem, które przy małej zmianie obejmuje dużo zdrowej skóry; system z pracy daje obrys znamienia w TH przez rejestrację. Ta sama rozdzielczość kamery (320 × 240) co w pracy.

**Uważaj.**
- Temperatury i klasyfikacja nie są częścią systemu – tylko kontekst. Mała próba (16 czerniaków), jeden podział 60/40; czułość zerowa dla większości klasyfikatorów, zwłaszcza na cechach dynamicznych (s. 4). Dla części klasyfikatorów cechy dynamiczne dały wyższą dokładność (s. 4).
- Podpis Table 1 mówi „accuracy and specificity”, a kolumny to ACC i SN (s. 5); 91,3% to czułość. Niska swoistość SMO-Poly widoczna tylko na Fig. 7c (ok. 10% – odczyt z wykresu, niepewne).
- Tekst nie mówi, jak lokalizowano zmianę na termogramie przy ustawianiu okna – nie twierdzić, że była widoczna.

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 2): „Stages involved in the acquisition protocol.” – schemat protokołu statyczny/dynamiczny; przydatność: średnia (2.1).
- Fig. 3 (s. 3): „Scheme of image partition and scanning performed during dynamic image analysis, using a melanoma lesion as example…” – ROI w TH; średnia (2.3.4).
- Fig. 4 (s. 4): „Static thermal profile representative of melanoma and melanocytic naevus lesions.” – średnia.
- Fig. 6 (s. 5): „Thermal behaviour of melanoma and melanocytic naevus lesions during stimulation stage: (a) maximum temperature difference; (b) average lesion temperature; and (c) average standard deviation of lesion temperature.” – krzywe powrotu; średnia.
- Table 1 (s. 5): „Acquired accuracy and specificity values, according to the implemented machine learning algorithm” – średnia.
- Fig. 2 (s. 3), Fig. 5 (s. 4), Fig. 7 (s. 5) – niska.

---

### Celebi, Codella, Halpern, 2019 – Dermoscopy Image Analysis: Overview and Future Directions
`celebi2019` · IEEE Journal of Biomedical and Health Informatics, 23(2), 474–478, 2019 · DOI: 10.1109/JBHI.2019.2895803 · Podrozdział: 2.1, 2.3.1

**Streszczenie.** Krótki przegląd analizy obrazów dermatoskopowych (DIA, *dermoscopy image analysis*): segmentacji, ekstrakcji cech i klasyfikacji, z kierunkami rozwoju (s. 1). Dermatoskopia to nieinwazyjna technika uwidaczniająca cechy zmian barwnikowych niewidoczne gołym okiem; ogranicza odbicie powierzchniowe (s. 1). Przez dwie dekady DIA rozwijała się wolno, bo brakowało publicznych zbiorów, oprogramowania i mocy obliczeniowej. Przyspieszyły ją zbiór ISIC (2016), biblioteki CNN i tanie GPU (s. 1). Segmentacja jest pierwszym krokiem analizy i jest trudna (s. 1). Zwykłe zdjęcia z bliska również pozwalają skutecznie stosować AI (s. 2). Proponowane kierunki rozwoju (s. 2–3):
- standaryzacja barwy i wyjaśnialność;
- wykrywanie przypadków spoza rozkładu (OOD);
- wyszukiwanie obrazów po treści (CBIR) i fotografia całego ciała;
- wykorzystanie metadanych klinicznych.

**Co zawrzeć w pracy.**
- 2.1: dane epidemiologiczne jako motywacja (s. 1).
- 2.1, dermatoskopia: poprawia diagnostykę przeszkolonych specjalistów, ale jest trudna do nauczenia i subiektywna (s. 1). Urządzenia eliminują odblaski, a przy kontakcie kontrolują oświetlenie (s. 2).
- 2.1, nowsze techniki: obrazowanie w podczerwieni, multispektralne i mikroskopia konfokalna mają potencjał wyższej dokładności (s. 1). Zwykła fotografia (tekstura powierzchni) i dermatoskopia (struktury podpowierzchniowe) powinny się teoretycznie uzupełniać; podobnie OCT i RCM (s. 2–3).
- 2.3.1, segmentacja (*lesion border detection*): lokalizacja zmiany, zwykle pierwszy krok po preprocessingu. Wymaga mało wiedzy dziedzinowej, stąd wiele prac (s. 1).
- 2.3.1, trudności segmentacji: zmienność kształtu, rozmiaru i barwy zmian, typy i tekstury skóry, naczynia, włosy, niejednolite warunki obrazowania (s. 1).
- 2.3.1, metody: historycznie dominowały klasteryzacja i progowanie (s. 1–2). Nie wykazano jednoznacznie, że dokładna segmentacja jest potrzebna do cech (s. 1). DL umożliwia klasyfikację bez segmentacji, ale segmentacja pozostaje ważna w analizie zmian w czasie (s. 2).
- 2.3.1/2.3.3: brakuje standaryzacji barwy. Normalizacja po akwizycji nie daje stabilnie dobrych wyników; standaryzacja przy akwizycji jest prawdopodobnie skuteczniejsza; w DL można stosować augmentację barwną (s. 2).

**Liczby i fakty do cytowania.**
- USA: ponad 5 mln przypadków raka skóry rocznie. Czerniak: ok. 91 000 nowych przypadków i ponad 9 000 zgonów rocznie, leczenie kosztuje ponad 3 mld USD rocznie (s. 1).
- Australia: ponad 14 000 przypadków czerniaka i prawie 2 000 zgonów rocznie. Europa: ponad 100 000 przypadków i 22 000 zgonów rocznie (s. 1).
- W USA zapadalność na czerniaka wzrosła o 225% w latach 1990–2018 (s. 1).
- Od 2015 r. CNN są podstawowym klasyfikatorem w DIA. ISIC 2018 Part 3 obejmowała 7 klas (s. 2).
- Dawne zbiory: atlas Argenziano (1999, ok. 1 000 obrazów), atlas Menziesa (2003, ok. 200), PH2 (2013, 200), razem ok. 1 400 (s. 2).
- ISIC Archive: najpierw ponad 10 000 obrazów, obecnie ponad 24 000 (s. 2). Konkursy: ISBI 2016 i 2017 oraz MICCAI 2018. W ISIC 2018 było ponad 1 000 zarejestrowanych użytkowników; w 3 lata powstało ponad 100 prac na danych ISIC (s. 2).

**Związek z systemem z pracy.** Model segmentacji jest douczony na ISIC, czyli na kontekście dermatoskopowym (s. 2), a stosowany do zdjęć z telefonu. Celebi potwierdza, że zwykłe zdjęcia z bliska nadają się do AI (s. 2). Mimo to różnica domen i brak standaryzacji barwy (s. 2) uzasadniają osobną ocenę na zdjęciach z telefonu względem CVAT. Wzmianka o obrazowaniu w podczerwieni (s. 1) daje punkt zaczepienia dla termowizji w 2.1.

**Uważaj.**
- Artykuł jest krótki (ok. 3 strony tekstu), bez wyników własnych.
- Podczerwień wymieniono tylko ogólnie. Nie przypisuj autorom tez o termowizji znamion.
- Nie ma szczegółów ISIC 2018 Task 1 (liczba obrazów do segmentacji) – są w `codella2019` (s. 2: 2594 / 100 / 1000).
- Statystyki dotyczą USA, Australii i Europy, nie Polski.

**Rysunki i tabele (kandydaci).**
- Brak – w tekście nie ma podpisów Fig./Table.

## 2.2.1 Modele transformacji i miary podobieństwa

### Zitová, Flusser, 2003 – Image registration methods: a survey
`zitova2003` · Image and Vision Computing, t. 21, s. 977–1000, 2003 (numeru zeszytu brak w tekście) · DOI: 10.1016/S0262-8856(03)00137-9 · Podrozdział: 2.2.1, 2.4 (pomocniczo 2.2.2)

**Streszczenie.** Przegląd klasycznych i nowszych (do 2003 r.) metod rejestracji obrazów, niezależnie od dziedziny zastosowań. Rejestracja to nakładanie dwóch lub więcej obrazów tej samej sceny wykonanych w różnym czasie, z różnych punktów widzenia lub różnymi sensorami, czyli geometryczne dopasowanie obrazu referencyjnego (*reference*) i rejestrowanego (*sensed*) (s. 1). Metody są klasyfikowane według charakteru (obszarowe – *area-based*, cechowe – *feature-based*) oraz według czterech etapów: detekcja cech, dopasowanie cech, estymacja modelu transformacji, transformacja i przepróbkowanie (s. 1–2). Przegląd omawia miary podobieństwa, optymalizację, modele odwzorowań (globalne, lokalne, RBF/TPS, elastyczne), interpolację i ocenę dokładności. Nie zawiera eksperymentów porównawczych (s. 1). Wnioski: automatyczna rejestracja pozostaje problemem otwartym, a rejestracja multimodalna należy do najtrudniejszych zadań (s. 19).

**Co zawrzeć w pracy.**
- 2.2.1 (wstęp): definicja rejestracji i podział zastosowań według sposobu akwizycji: wiele punktów widzenia, różne chwile czasu, różne sensory (*multimodal analysis*), scena–model; przypadek z pracy to rejestracja multimodalna (s. 1–2).
- 2.2.1: cztery etapy rejestracji (s. 2, Fig. 1 s. 3). Propozycja odniesienia do systemu: detekcja znacznika → dopasowanie do wzorca Π → ECC (estymacja macierzy T) → przeniesienie ROI.
- 2.2.1: modele transformacji – podobieństwo, afiniczne, perspektywiczne; warunki stosowalności modelu afinicznego i perspektywicznego (s. 14–15). Na tym oprzeć wybór „afiniczne albo homografia”.
- 2.2.1: obszarowe a cechowe. Metody cechowe nadają się, gdy spodziewane są zmiany oświetlenia lub analiza wielosensorowa (s. 4). Metody obszarowe wymagają, by funkcje intensywności były identyczne lub przynajmniej statystycznie zależne (s. 13).
- 2.2.2: w obrazach medycznych brak wyrazistych obiektów rozwiązuje się m.in. przez cechy zewnętrzne sztywno związane z pacjentem (*skin markers, screw markers, dental adapters*) (s. 5) – bezpośrednie uzasadnienie znacznika Π.
- 2.4: rodzaje błędów: lokalizacji, dopasowania, wyrównania. CPE jest słabą miarą (zerowe CPE można uzyskać przez nadmierne dopasowanie), TPE liczy się na punktach wyłączonych z estymacji; „target points” Fitzpatricka (s. 18).

**Liczby i fakty do cytowania.**
- Ponad 1000 prac o rejestracji w ciągu ostatnich 10 lat wg bazy ISI (s. 1).
- „It is impossible to design a universal method applicable to all registration tasks” (s. 2).
- Środki ciężkości regionów są niezmiennicze względem obrotu, skalowania i pochylenia oraz stabilne przy szumie i zmianach poziomu szarości (s. 4).
- Podobieństwo = obrót + przesunięcie + skala, wyznaczone przez 2 punkty kontrolne (CP) (s. 14). Afiniczne: 3 niewspółliniowe CP, zachowuje proste i równoległość. Wymaga dużej odległości kamery względem obszaru, kamery otworkowej, płaskiej sceny i braku lokalnych zniekształceń (s. 14).
- Perspektywiczne: dokładnie opisuje płaską scenę fotografowaną kamerą otworkową, której oś optyczna nie jest prostopadła do sceny. Wyznaczone przez 4 CP; przy nadmiarze CP stosuje się MNK (s. 15).
- Korelacja znormalizowana dokładnie dopasowuje tylko obrazy przesunięte, toleruje lekki obrót i skalę. Wady: płaskie maksimum miary i duży koszt obliczeniowy (s. 6).
- MI: $MI(X,Y)=H(X)+H(Y)-H(X,Y)$; „leading technique in multimodal registration” (s. 8). Jako metoda obszarowa ma jednak zasadnicze ograniczenia (s. 19).
- Zwykle stosuje się przepróbkowanie wsteczne, które nie daje dziur ani nakładek (s. 16). Interpolacja dwuliniowa daje najlepszy kompromis dokładność/koszt. Najbliższego sąsiada należy unikać, chyba że obraz ma mało poziomów intensywności i nie chcemy „syntetycznych” wartości (s. 17–18). Odniesienie tego do masek to wniosek własny.
- „Without quantitative evaluation, no registration method can be accepted for practical utilization” (s. 19).

**Związek z systemem z pracy.** System jest hybrydą: cechowa detekcja sztucznego znacznika (odpowiednik *skin markers*, s. 5), potem obszarowe ECC na maskach. Maski sprowadzają obie modalności do „podobnych funkcji intensywności”, czego metody obszarowe wymagają (s. 13). TRE na narożnikach znacznika odpowiada TPE/target points z s. 18.

**Uważaj.**
- ECC nie występuje w przeglądzie. Nie przypisywać Zitovej oceny ECC.
- Teza, że metody obszarowe w praktyce obsługują tylko przesunięcie i mały obrót (s. 13), dotyczy przeszukiwania wyczerpującego. Nie stosować jej wprost do iteracyjnego ECC z inicjalizacją.
- Stan wiedzy z 2003 r. (brak metod głębokich). Założenie płaskiej sceny dla modelu perspektywicznego na skórze spełnione jest tylko w przybliżeniu.

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 3): „Four steps of image registration: … feature detection … feature matching by invariant descriptors … transform model estimation … image resampling and transformation” – schemat czterech etapów; przydatność: wysoka.
- Fig. 2 (s. 7): „Area-based matching methods: registration of small template to the whole image using normalized cross-correlation … and phase correlation …” – pokazuje, że NCC może zawieść dla danych multimodalnych; przydatność: średnia.
- Fig. 3 (s. 8): „Mutual information: MI criterion …”; Fig. 4 (s. 10): „Feature-based method using invariant descriptors …”; Fig. 6 (s. 17): „Image interpolation methods …”; przydatność: niska.
- Fig. 5 (s. 14): „Examples of various mapping functions: similarity …, affine …, perspective projection …, and elastic transform” – wizualizacja modeli transformacji; przydatność: wysoka.
- Tabel brak.

---

### Evangelidis, Psarakis, 2008 – Parametric Image Alignment Using Enhanced Correlation Coefficient Maximization
`evangelidis2008` · IEEE Transactions on Pattern Analysis and Machine Intelligence, 30(10), 1858–1865, 2008 (Short Papers) · DOI: 10.1109/TPAMI.2008.113 · Podrozdział: 2.2.1

**Streszczenie.** Autorzy proponują zmodyfikowany współczynnik korelacji (*enhanced correlation coefficient*, ECC) jako funkcję celu w parametrycznym dopasowaniu obrazów. Kryterium jest niezmiennicze względem zniekształceń fotometrycznych jasności i kontrastu (s. 1–2). ECC jest nieliniowe względem parametrów, więc zaproponowano dwa schematy iteracyjne: *forward additive* (FA-ECC) i *inverse compositional* (IC-ECC), z rozwiązaniem w postaci zamkniętej w każdej iteracji (s. 1, 3–4). Testy są symulacyjne: obraz „Takeo”, 5000 realizacji par, transformacje afiniczne, szum gaussowski, porównanie z Forward Additive Lucas–Kanade (FA-LK) i Simultaneous Inverse Compositional (SIC) (s. 5–6). FA-ECC osiąga niższy błąd, szybszą zbieżność i więcej zbieżnych przebiegów, zwłaszcza przy silnych deformacjach i zniekształceniu fotometrycznym. IC-ECC dorównuje SIC przy niższej złożoności (s. 6–7). Wniosek autorów: proponowane schematy są lepsze od odpowiednich wariantów LK (s. 7).

**Co zawrzeć w pracy.**
- 2.2.1: sformułowanie problemu. Rozwiązanie ma dwa kroki: wybór parametrycznego modelu geometrycznego (afiniczny i jego szczególne przypadki; homografia jako alternatywa) oraz wybór funkcji celu (s. 1).
- 2.2.1: definicja ECC (wzory 4–5, s. 2). Wektory intensywności z obszaru docelowego są pozbawione średniej i znormalizowane, stąd niezmienniczość względem przesunięcia jasności (*bias*) i wzmocnienia (*gain*) (s. 2). Autorzy powołują się też na odporność statystyczną na obserwacje odstające wg [22] (s. 2).
- 2.2.1: związek z SSD. Minimalizacja SSD z optymalną kompensacją jasności i kontrastu ($\alpha_1\ge 0$) daje $E(\mathbf p)=\|\bar{\mathbf i}_r\|^2\{1-[\max\{\rho(\mathbf p),0\}]^2\}$, czyli maksymalizację ECC (s. 4–5). Kryterium LK zawiera dodatkowy człon $\|\bar{\mathbf i}_w(\mathbf p)\|^2$, przez który może utknąć w obszarach jednorodnych i na korelacjach ujemnych (s. 5).
- 2.2.1: optymalizacja gradientowa z linearyzacją Taylora (Jakobian $G$), twierdzeniem 1 i lematem 1. Lemat 1 dobiera krok tak, by korelacja rosła i była nieujemna. Iteracje kończą się, gdy $\|\Delta\mathbf p_j\|<T$ (Table 1, s. 3–4).
- 2.2.1: ograniczenia metod gradientowych: obszary jednorodne, pojedyncze krawędzie (problem apertury) i duże przesunięcia (s. 1). Uzasadnia to wstępne dopasowanie wzorca Π jako inicjalizację ECC.

**Liczby i fakty do cytowania.**
- $E_{ECC}(\mathbf p)=\left\|\frac{\bar{\mathbf i}_r}{\|\bar{\mathbf i}_r\|}-\frac{\bar{\mathbf i}_w(\mathbf p)}{\|\bar{\mathbf i}_w(\mathbf p)\|}\right\|^2$; równoważnie maksymalizacja $\rho(\mathbf p)=\frac{\bar{\mathbf i}_r^t\bar{\mathbf i}_w(\mathbf p)}{\|\bar{\mathbf i}_r\|\|\bar{\mathbf i}_w(\mathbf p)\|}$ (s. 2).
- Złożoność na iterację: FA-ECC $O(KN^2)$, IC-ECC $O(KN)$ (s. 4), SIC $O(K(N+2)^2)$ (s. 7). $K$ to liczba pikseli, $N$ liczba parametrów.
- Algorytmy odwrotne stosują się tylko do określonych klas transformacji i są bardziej wrażliwe na szum niż wersje „forward” (s. 4).
- Eksperymenty: 3 punkty zaburzane szumem $N(0,\sigma_p^2)$; 5000 realizacji; szum intensywności $\sigma_i=8$ poziomów szarości; $j_{max}=15$, $T_{MSD}=1$ piksel² (s. 5–6).
- Przy średnich i silnych deformacjach poziom MSD dla FA-ECC jest o 3 dB niższy niż dla wersji odwrotnych i nieco niższy niż dla FA-LK (s. 6).
- Przy $j_{MAX}=100$ i $T_{MSD}=(1/18\ \text{piksela})^2$ (≈ −25 dB) wszystkie algorytmy przy słabych deformacjach są niemal zawsze zbieżne po 10. iteracji (s. 6).
- Nieliniowe zniekształcenie fotometryczne $I\leftarrow(I+20)^{0.9}$: FA-ECC prawie bez zmian. Przy zniekształconym obrazie referencyjnym poziom MSD jest o 3 dB niższy niż FA-LK i o 5 dB niższy niż algorytmy odwrotne. Przy zniekształconym obrazie warped wszystkie algorytmy osiągają ten sam poziom (s. 6).
- Bez szumu FA-ECC ≈ algorytmy odwrotne > FA-LK; różnica istotna dla $\sigma_p\ge 6$ (s. 7).

**Związek z systemem z pracy.** System wywołuje `cv2.findTransformECC` (afinicznie albo homografią) na maskach znacznika. Artykuł uzasadnia wybór: kryterium jest szybkie dzięki zamkniętemu krokowi, odporne na szum, a w wersji forward bardziej niezawodne od LK. Konieczność dobrej inicjalizacji (s. 1, Fig. 1d) uzasadnia wcześniejszy etap dopasowania kształtu Π.

**Uważaj.**
- Ścisła niezmienniczość dotyczy tylko liniowych zmian (*bias/gain*) (s. 2). Przy nieliniowych zmianach jest tylko empiryczna odporność (s. 6). Nie twierdzić, że ECC „radzi sobie z multimodalnością” RGB–termowizja; w systemie działa dzięki porównywaniu masek.
- Testy wyłącznie syntetyczne: jeden obraz, transformacje afiniczne, brak homografii, masek binarnych i danych medycznych. Maski mają duże obszary jednorodne, a autorzy wymieniają je jako słabość metod gradientowych (s. 1).
- Artykuł nie opisuje implementacji OpenCV (piramidy, filtr wstępny). PoC spada wraz z $\sigma_p$, więc zbieżność nie jest gwarantowana (s. 6).

**Rysunki i tabele (kandydaci).**
- Table 1 (s. 4): „Outline of the Proposed Forward Additive ECC (FA-ECC) Refinement Algorithm” – kroki S1–S4 algorytmu; przydatność: wysoka (do opisu ECC/pseudokodu).
- Fig. 1 (s. 6): „MSD in decibels as a function of number of iterations under the presence of noise (σi = 8 gray levels). (a) σp = 2. (b) σp = 6. (c) σp = 10. In (d), PoC as a function of σp” – zbieżność ECC vs LK/SIC; przydatność: średnia.
- Fig. 2 (s. 7): „MSD in decibels … for photometrically distorted reference (solid lines) and warped (dashed lines) image under the presence of noise …” – odporność fotometryczna; przydatność: średnia.
- Fig. 3 (s. 7): „PoC as a function of iterations …”; przydatność: niska.

---

### Roche, Malandain, Pennec i in., 1998 – The Correlation Ratio as a New Similarity Measure for Multimodal Image Registration
`roche1998` · materiały konferencyjne (nazwy konferencji brak w PDF; paginacja ok. s. 1115–1124). Wykaz literatury pracy, poz. [6], podaje „MICCAI'98, 2006”: rok 2006 = data utworzenia pliku PDF, prawdopodobnie błąd · DOI: brak w tekście · Podrozdział: 2.2.1 (opcjonalny)

**Streszczenie.** Zakładając zależność funkcyjną między intensywnościami obrazów, autorzy wyprowadzają z teorii prawdopodobieństwa stosunek korelacyjny (*correlation ratio*, CR) jako miarę podobieństwa do rejestracji multimodalnej (s. 1, 3–4). Na syntetycznym eksperymencie „grey stripe” pokazują, że informacja wzajemna (MI) może mieć wiele równoważnych maksimów, a CR ma jedno maksimum globalne (s. 2–3). Testy objęły sztywną rejestrację 3D obrazów mózgu 10 pacjentów (MR T1, MR T2, CT, PET) ze złotym standardem znacznikowym (s. 6–7). Porównano CR, MI, współczynnik korelacji (CC) i kryterium Woodsa. Tylko MI i CR dały sensowną dokładność dla wszystkich par modalności; MI było lepsze dla CT–T1, CR dla PET–T1 (s. 7). Wniosek autorów: CR daje dobry kompromis między dokładnością a odpornością (s. 1).

**Co zawrzeć w pracy.**
- 2.2.1: miary oparte na najmniejszych kwadratach i korelacji zakładają liniową zależność intensywności, co w rejestracji multimodalnej jest zbyt grubym założeniem (s. 1).
- 2.2.1: MI. Nie zakłada rodzaju zależności, tylko jej przewidywalność (s. 2). Wada: traktuje intensywności czysto jakościowo, bez pojęcia bliskości w przestrzeni intensywności, co może dawać niedookreśloną miarę z wieloma maksimami lokalnymi (s. 2–3).
- 2.2.1: definicja CR, jego własności (zakres 0–1, niezmienniczość na mnożenie Y, asymetria) i związek z CC: $\eta(Y|X)\ge\rho(X,Y)$ (s. 4–5). Daje to kolejność CC → CR → MI według coraz słabszych założeń o zależności intensywności.

**Liczby i fakty do cytowania.**
- $\eta(Y|X)=\frac{Var[E(Y|X)]}{Var(Y)}=1-\frac{Var[Y-E(Y|X)]}{Var(Y)}$ (wzór 3, s. 4); obliczanie: $1-\eta(Y|X)=\frac{1}{N\sigma^2}\sum_i N_i\sigma_i^2$ (wzór 4, s. 5).
- Złożoność: MI $O(n_x n_y)$, CR $O(n_x)$ (s. 5).
- „Grey stripe”: binarny obraz A 40 × 30 pikseli i gradientowy B 30 × 30. Każde przesunięcie całkowite daje maksymalne MI = 1 (górna granica), a CR ma maksimum tylko przy pełnym nałożeniu (s. 2–3).
- Błąd ε to średnia z 8 punktów przy powierzchni czaszki względem transformacji znacznikowej (s. 7).
- Table 1 (średnia/mediana ε w mm): T1–T2: MI 4,30/1,48; CR 1,93/1,46; OW 2,65/2,00; CC 2,42/2,37. CT–T1: MI 2,52/2,00; CR 3,27/3,24. PET–T1: MI 5,87/5,58; CR 4,60/3,65; OW 7,69/7,62 (s. 7).
- CC dało bezsensowne wyniki dla CT–T1 i PET–T1, MI zawiodło w 2 przypadkach T1–T2 (s. 7). CR było mniej wrażliwe na podpróbkowanie niż MI i OW (wynik jakościowy z [11]) (s. 8).

**Związek z systemem z pracy.** Artykuł daje literaturowe tło dla wyniku E4 (MI Mattesa wyraźnie gorsze od ECC). MI bywa niedookreślone i ma maksima lokalne, a gdy da się założyć zależność funkcyjną intensywności, prostsza miara statystyczna może działać lepiej (s. 3, 7). Przy porównywaniu masek zależność jest wręcz liniowa, co sprzyja mierze korelacyjnej. To interpretacja, nie wynik autorów.

**Uważaj.**
- CR ≠ ECC: autorzy nie badali ECC. CC w ich eksperymencie to zwykły współczynnik korelacji na surowych obrazach, w dodatku zdefiniowany jako $Cov^2/(Var\,Var)$ (s. 5).
- Dla CT–T1 MI było lepsze od CR (s. 7), więc nie pisać, że MI jest „ogólnie gorsze”. Dane: 3D, mózg, rejestracja sztywna; MI z histogramu + PV to inna implementacja niż MI Mattesa w SimpleITK.

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 2): „'Grey stripe' registration experiment” – obrazy A i B; przydatność: średnia (tylko razem z Fig. 2).
- Fig. 2 (s. 3): „'Grey stripe' registration experiment. Left, plot of mutual information I(A, BT) vs. horizontal translation. Right, the correlation ratio …” – wiele maksimów MI vs jedno maksimum CR; przydatność: średnia.
- Table 1 (s. 7): „Mean and median of the registration typical errors (based on positions of stereotaxic markers) obtained over ten intra-patient experiments”; przydatność: średnia.
- Fig. 3 (s. 8): „Multimodal registration by maximization of CR …”; Table 2 (s. 8): „The correlation ratio performances depending on resolution”; przydatność: niska.

## 2.2.2 Rejestracja RGB–termowizja i znaczniki referencyjne

### Oniga, Rus, Condorovici i in., 2026 – A heatmap-based deep learning framework for multi-modal registration of VIS, NIR, and thermal images in dermatological imaging
`oniga2026` · Frontiers in Artificial Intelligence, 9, art. 1807482, 2026 · DOI: 10.3389/frai.2026.1807482 · Podrozdział: 2.2.2, 2.2.3, 2.4, 2.5

**Streszczenie.** Autorzy rejestrują trójki obrazów zmian skórnych: światło widzialne (VIS), bliska podczerwień (NIR) i termowizja (TH, długofalowa podczerwień – LWIR), wykonane trzema różnymi kamerami, do układu obrazu VIS (s. 1, 3). Na skórze wokół zmiany umieszczony jest kwadratowy znacznik referencyjny (fiducial marker); detektor YOLOv8n lokalizuje go w każdej modalności i na tej podstawie wycina się obszar zainteresowania (ROI) (s. 4, 7). Właściwa rejestracja to sieć typu ResU-Net z modułami uwagi CBAM i dwoma dekoderami (NIR, TH), przewidująca mapy cieplne (heatmaps) punktów kluczowych; z punktów wyznaczana jest homografia metodą RANSAC (s. 5–7). Brak ręcznych korespondencji, więc nadzór stanowią pseudo-etykiety (pseudo-ground-truth) z dopasowań MINIMA-LoFTR (s. 4). Zbiór: 155 trójek (465 obrazów) od 62 pacjentów; znamiona (NV), znamiona dysplastyczne (DN), czerniaki (MM) (s. 3). Ocena tylko miarami podobieństwa obrazów SSIM, MI, NMI; dla TH SSIM 0,395 vs 0,209 dla MINIMA-LoFTR (s. 13, Table 5). NIR–VIS stale lepsze niż TH–VIS; autorzy przyznają, że wyniki „nie są tak wysokie, jak można by oczekiwać” (s. 15).

**Co zawrzeć w pracy.**
- 2.2.2: najbliższy odpowiednik systemu z pracy – znacznik na skórze wokół zmiany jako wspólna kotwica VIS/TH. W TH znacznik „często mniej widoczny, z zaokrąglonymi narożnikami”, dlatego klasyczna detekcja narożników okazała się nieprzydatna do wycinania (s. 7); w TH zmiany często niewidoczne, a znacznik daje „tylko uproszczony kształt geometryczny” (s. 14).
- 2.2.1/2.2.2: uzasadnienie homografii: mały fragment skóry ze sztywnym kwadratowym znacznikiem jest lokalnie quasi-płaski; model afiniczny nie oddaje perspektywy przy kilku sensorach, a deformowalny wymaga gęstych korespondencji lub silnej regularyzacji (s. 7). Gotowy argument do wyboru afiniczne/homografia w pracy.
- 2.2.3: przykład rejestracji DL: detektor + sieć map cieplnych + RANSAC, porównanie z DeepConvFeatures, VISMATCH i MINIMA-LoFTR (s. 10). Punkty kluczowe leżą głównie na krawędziach i narożnikach znacznika (s. 8) – sieć de facto „patrzy” na znacznik.
- 2.4: SSIM/MI/NMI są niezależne od pseudo-etykiet (s. 11), ale nie są miarami geometrycznymi; brak TRE i miar nakładania masek (Dice/IoU) – kontrast z pracą (TRE w mm, Dice).
- 2.4: test t Welcha i 95% przedziały ufności (s. 11, 13); podział zbioru na poziomie pacjenta, by uniknąć przecieku danych (s. 10, 14) – analogia do walidacji krzyżowej po znamionach.
- 2.5: autorzy deklarują pierwszy zbiór VIS-NIR-TH zmian skórnych (s. 13); trudności: niewidoczna zmiana w TH, trzy różne kamery, zmieniający się sprzęt (s. 14).
- 2.2.1 (pobocznie): metody obszarowe (area-based), cechowe (feature-based) i hybrydowe (s. 2).

**Liczby i fakty do cytowania.**
- Kamery: VIS – moduł USB 3.0 2 MP (Sony IMX385), 1920 × 1080; NIR – FLIR Blackfly S, 2448 × 2048, LED 940 nm; TH – Optris PI450i (382 × 288) i PI640i (640 × 480), czułość 0,04 K (s. 3).
- Zbiór do detekcji znacznika: 100 trójek (300 obrazów) w laboratorium, ramki w LabelImg (s. 4).
- YOLOv8n osobno: mAP50-95 VIS 0,8220, NIR 0,8594, TH 0,8615; F1 0,9472 / 0,9962 / 0,9972 (s. 8, Table 1). Model wspólny: mAP50-95 0,8489, mAP50 0,9950, mAP75 0,9924, F1 0,9838 (s. 8, Table 2).
- Ręczna korekta ramki w 4 przypadkach TH, w tekście „ok. 3,4%” ze 155 trójek – etap półautomatyczny (s. 8).
- Wejście sieci: tylko VIS w skali szarości 256 × 256 (s. 5); strata: 0,8·MSE + 0,6·Focal + 0,4·Cons + 0,3·Cont + 0,2·Perc (s. 6–7).
- Podział: 49/13 pacjentów → 126/29 trójek; najlepiej LR 1e-5, 30 epok, batch 8 (s. 10).
- Table 5 (s. 13), średnia ± SD, metoda własna: NIR SSIM 0,496 ± 0,110, MI 1,073 ± 0,283, NMI 0,154 ± 0,036; TH SSIM 0,395 ± 0,180, MI 0,732 ± 0,306, NMI 0,112 ± 0,044. MINIMA-LoFTR (SSIM/MI/NMI): NIR 0,440/0,936/0,202; TH 0,209/0,683/0,154. VISMATCH: NIR 0,213/0,626/0,141; TH 0,083/0,240/0,073. DeepConvFeatures: NIR 0,202/0,700/0,160; TH 0,123/0,460/0,118.
- Ocenianych trójek: 29 (metoda własna, DeepConvFeatures, MINIMA), 7 (VISMATCH) (s. 10).
- Przewaga nad VISMATCH i DeepConvFeatures istotna (p < 0,05) dla SSIM i MI; nad MINIMA-LoFTR nieistotna (s. 11).
- Dopasowane punkty w przykładach: NIR 164, 192, 181 vs TH 44, 9, 23 (s. 10); limit 100 punktów na obraz (s. 13).

**Związek z systemem z pracy.** Ten sam pomysł (znacznik przy zmianie jako kotwica VIS–TH, homografia, ROI w obrębie znacznika), ale inna realizacja: zamiast jawnej segmentacji znacznika i dopasowania znanego kształtu – detekcja ramki i sieć uczona na pseudo-etykietach. Praca może się wyróżnić oceną geometryczną (TRE w mm na narożnikach znacznika, Dice masek), której u Oniga brak, oraz wykorzystaniem znanej geometrii znacznika.

**Uważaj.**
- Nie zestawiać SSIM/MI z TRE/Dice jako „dokładności” – to inne miary; artykuł nie podaje błędu w pikselach ani mm.
- Znacznik w tekście to tylko „squared marker”/„rigid square reference”; materiał i wymiary nie są podane (protokół i system akwizycji odsyłają do Sultana i in. 2025, s. 3). Z Fig. 3–4 widać (obserwacja z rysunku, nie z tekstu) kwadratową ramkę z okienkiem i podziałką, ciemniejszą od skóry w TH – nie przypisywać jej folii aluminiowej.
- Niespójności: Table 4 „Final version” (NIR-SSIM 0,4648, TH-SSIM 0,3211) ≠ Table 3/5 (0,496; 0,395) (s. 10, 12); NMI metody własnej niższe niż MINIMA (dla TH także niż DeepConvFeatures); 4/155 ≈ 2,6%, nie 3,4%. Opis inferencji niejasny: sieć dostaje tylko VIS (s. 5), a zwraca punkty dla NIR i TH dopasowywane „po bliskości przestrzennej” (s. 6–7) – nie dopowiadać.

**Rysunki i tabele (kandydaci).**
- Fig. 3 (s. 4): „Acquired image triplet: VIS image (left), NIR image (middle), and TH image (right).” – znacznik w trzech modalnościach; przydatność: wysoka (2.2.2, porównanie ze znacznikiem Π).
- Table 5 (s. 13): „Comparison of registration performance across methods.” – wysoka (2.2.3, 2.4).
- Fig. 1 (s. 3): „The proposed pipeline for multimodal image triplet registration.” – schemat; średnia.
- Fig. 7 (s. 9): „Examples of squared marker detection with YOLOv8n: (a) correctly detected markers and (b) missed or incorrectly detected markers.” – błędy detekcji; średnia.
- Fig. 9 (s. 11): „Comparison of multimodal registration results. (A) Favorable case and (B) challenging case.” – mapy różnic; średnia.
- Pozostałe (Fig. 2, 4–6, 8, 10, 11; Table 1–4, 6) – niska.

---

### González-Pérez, Perea Ström, Arteaga-Marrero i in., 2021 – Assessment of Registration Methods for Thermal Infrared and Visible Images for Diabetic Foot Monitoring
`gonzalezperez2021` · Sensors, 21, art. 2264, 2021 · DOI: 10.3390/s21072264 · Podrozdział: 2.2.2, 2.4

**Streszczenie.** Porównano cztery metody rejestracji obrazów termowizyjnych i RGB z taniego prototypu do monitorowania stopy cukrzycowej: translację geometryczno-optyczną (GOT), homografię, ICP (Iterative Closest Point) i przekształcenie afiniczne z adaptacyjnym stochastycznym spadkiem gradientu (Affine-ASGD) (s. 1). Kamery Intel RealSense D415 (1280 × 720) i Thermal Expert TE-Q1 Plus (384 × 288) są sztywno zamocowane (s. 3). GOT i homografia korzystają z punktów specjalnej szachownicy kalibracyjnej widocznej w obu widmach; ICP i Affine-ASGD – z masek stóp (s. 4–6). Ocena: 12 obrazów (6 VIS + 6 IR) w sześciu odległościach 760–850 mm; referencją są ręczne segmentacje dwóch badaczy połączone algorytmem STAPLE; miary: Dice, Jaccard (IoU), podobieństwo objętości, FN, FP (s. 3, 6, 11). Przy płaszczyźnie ostrości 800 mm Dice: GOT 0,968, homografia 0,980, ICP 0,979, Affine-ASGD 0,982 (s. 7–9). Poza 800 mm wszystkie metody się pogarszają, najszybciej homografia (s. 12). Wnioski: więcej stopni swobody nie znaczy lepiej, a metody oparte na obrazie nie wymagają ponownej kalibracji szachownicą (s. 14).

**Co zawrzeć w pracy.**
- 2.2.2: wzorzec widoczny w VIS i TH: szachownica z PVC (kwadraty i koła wycięte ploterem laserowym) przed czarną płytą aluminiową schłodzoną w lodówce, co daje kontrast cieplny (s. 4, Fig. 1); detekcja punktów detektorem plam (blob detector) + RANSAC z OpenCV (s. 5). Analogia do folii aluminiowej w znaczniku Π.
- 2.2.2: metody oparte na szachownicy są „przywiązane” do płaszczyzny kalibracji (800 mm), a niska rozdzielczość tanich kamer TH ogranicza liczbę rozpoznawalnych cech wzorca (s. 13–14) – argument za rejestracją dla każdej pary ze znacznika w kadrze zamiast jednorazowej kalibracji.
- 2.2.1: hierarchia modeli: translacja, sztywny (ICP: obrót + przesunięcie, stała skala), afiniczny (6 parametrów), homografia (8 parametrów) (s. 5–6). Homografia, mimo największej liczby stopni swobody, najgorzej generalizuje poza obrazy referencyjne – dopasowuje parametry do błędów niemodelowanych, np. nieliniowych zniekształceń optyki (s. 12–13).
- 2.2.2: Affine-ASGD (Elastix) liczony na binarnych maskach, z maską TH jako obrazem referencyjnym (s. 9); na surowych obrazach różnych widm ASGD nie zbiega poprawnie, bo opiera się na podobieństwie pikseli (s. 13) – bezpośrednie uzasadnienie ECC na maskach znacznika.
- 2.4: Dice/Jaccard masek jako miara rejestracji, STAPLE do łączenia adnotacji (s. 3, 6). Dice rośnie z liczbą pikseli obiektu przy tym samym błędzie rejestracji (s. 12) – ważne przy porównaniu Dice znamienia i folii znacznika.

**Liczby i fakty do cytowania.**
- Odległości: 760, 780, 800, 820, 835, 850 mm; optimum 800 mm (s. 3, 10).
- Jaccard przy 800 mm: GOT 0,938, homografia 0,961, ICP 0,959, Affine-ASGD 0,965 (s. 11, Table 1).
- Dice przy 850 mm: 0,953 / 0,949 / 0,959 / 0,966; przy 760 mm: 0,961 / 0,981 / 0,972 / 0,972 (s. 11, Table 1).
- FP przy 800 mm: Affine-ASGD 0,008 vs GOT 0,034 (s. 11, Table 1).
- Transformacje wyznaczone przy 800 mm stosowano bez zmian do pozostałych odległości (s. 10).

**Związek z systemem z pracy.** Wspiera dwie decyzje: obiekt referencyjny widoczny w obu widmach dzięki aluminium oraz rejestrację na maskach zamiast na intensywnościach. Różnica: tam kamery są sztywno połączone i transformację wyznacza się raz; w pracy telefon i kamera TH są niezależne, więc T trzeba liczyć dla każdej pary ze znacznika.

**Uważaj.**
- Bardzo mała próba (6 par); tekst mówi o „the subject” – liczba osób niepodana jasno (niepewne). Dice dotyczy całych stóp (duże obiekty), więc wartości > 0,95 nie są porównywalne z Dice znamienia; brak TRE.
- Niespójności: abstrakt i wnioski „Dice > 0,950 we wszystkich scenariuszach”, a homografia przy 850 mm ma 0,949 (s. 1, 14 vs Table 1, s. 11); GOT przy 800 mm: 0,968 (s. 7, Table 1) vs 0,966 we wnioskach (s. 14).

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 4): „Custom built checkerboard keypoint detection and matching. … Notice the black aluminum plate behind the checkerboard in the RGB image and its corresponding cold contrast signature in the thermal image.” – wzorzec widoczny w obu widmach; przydatność: wysoka (2.2.2).
- Table 1 (s. 11): „Overlap performance with varying subject's feet distance for different registration methods.” – wysoka (2.4).
- Fig. 2 (s. 7): „Fusion of thermal IR images with the feet segmentation of the visible image after applying each registration method (masks highlighted in color) analyzed at 800 mm.” – nałożenie maski na TH; średnia (2.2.4).
- Fig. 3 (s. 8): „Dice coefficient and Jaccard index metrics for the four registration methods obtained with the subject located at the sensors focal plane (800 mm).” – średnia.
- Fig. 5 (s. 10): „Affine-ASGD method registration pipeline.” – rejestracja na maskach; średnia.
- Fig. 6 (s. 11): „Dice coefficient metric with varying patient feet distance for each registration method.” – średnia.
- Fig. 4 (s. 9): potok ICP – niska.
- Uwaga: s. 4 PDF ma nakładający się tekst; opis szachownicy odczytany z powtórzeń, zgodny z podpisem Fig. 1.

---

### Maurya, Mahapatra, Chawla, 2021 – Non-contact breathing monitoring by integrating RGB and thermal imaging via RGB-thermal image registration
`maurya2021` · Biocybernetics and Biomedical Engineering, 41, 1107–1122, 2021 · DOI: 10.1016/j.bbe.2021.07.002 · Podrozdział: 2.2.2, 2.2.4

**Streszczenie.** Bezkontaktowy pomiar częstości oddechu: obszar nozdrzy wykrywany i śledzony w obrazie RGB jest odwzorowany na obraz termowizyjny przez rejestrację RGB–termowizja, a sygnał oddechowy to średnia wartość pikseli TH w tym obszarze (s. 1, 6). Rejestracja jest dwuetapowa: wstępne przekształcenie skali z punktów kontrolnych wyznaczonych automatycznie na ramie kalibracyjnej (calibration rig), którą badany trzyma na początku nagrania, oraz rejestracja dokładna cechami opartymi na zgodności fazy (phase congruency, filtry log-Gabora) z dopasowaniem FSC (fast sample consensus) (s. 3–6). Kamery: FLIR E-60 (320 × 240, 30 Hz) i Logitech C922 (960 × 720, 30 Hz) (s. 7). Średni TRE 1,817 piksela (błąd standardowy 0,3672) na 50 parach, lepiej niż EOH, PCEHD, LGHD (s. 8). Wykrywalność ROI: mediana 100% w fazach 1 i 3, 99,87% (2A), 99,93% (2B) (s. 8). Względem pasa oddechowego MAE 0,11 bpm w spoczynku i 1,46 / 2,08 / 1,69 bpm w trudniejszych fazach (s. 1). Wniosek: detekcja i śledzenie w RGB omijają ubogą teksturę TH.

**Co zawrzeć w pracy.**
- 2.2.2: rama kalibracyjna to „regularny kwadrat wycięty z cienkiego materiału słabo przewodzącego ciepło”, służy do automatycznego wyznaczenia punktów kontrolnych RGB–TH (s. 3). Ten sam pomysł co znacznik w pracy.
- 2.2.2: autorzy zauważają, że punkty kontrolne skupione w obszarze ramy, nierówno rozłożone w obrazie, mogą dawać niedopasowanie, stąd etap dokładny (s. 3).
- 2.2.2: krytyka stałej rejestracji (parametry z pierwszej klatki lub fazy kalibracji stosowane do całego nagrania): silnie zależy od odległości kamera–obiekt (s. 3, 12).
- 2.2.1/2.2.2: cechy odporne na różnice modalności: zgodność fazy (log-Gabor), EOH, PCEHD, LGHD, RIFT (s. 3).
- 2.2.4: zasada „wykrywaj w RGB, mierz w TH”: ROI z detektora MTCNN (5 punktów twarzy) przenoszony na TH parametrami transformacji, bo obraz TH ma mniej tekstury i niższą rozdzielczość (s. 2, 6) – analogia do przenoszenia ROI znamienia.
- 2.4: definicja TRE = ‖r_g − r_p‖ (za Maurer i in. 1998) (s. 8).

**Liczby i fakty do cytowania.**
- FLIR E-60: 320 × 240, 30 Hz, 7,5–13 µm, czułość < 0,05 °C przy 30 °C; C922 nad kamerą TH, równolegle, na statywie; odległość ok. 1,80 m (s. 6–7).
- TRE 1,817 px (SE 0,3672); 50 par RGB–TH, losowa klatka z każdego nagrania (s. 8).
- Uczestnicy: faza 1 – 20 osób, faza 2 – 12, faza 3 – 6 (s. 7–8); łącznie 210 pomiarów (s. 13).
- Faza 1: MAE 0,1106 ± 0,0688, RMSE 0,1305 ± 0,0741, korelacja 0,9995 (s. 8–9).
- ROI: okulary (n = 8) 99,96%, zarost (n = 28) 99,93%, turban (n = 5) 100% (s. 8).
- Automatyczna korekcja niejednorodności (NUC) chwilowo zamraża obraz TH, ale nie wpływa na ROI, bo śledzenie odbywa się w RGB (s. 12).

**Związek z systemem z pracy.** Uzasadnia architekturę: wyznaczanie obszaru w RGB i przeniesienie go macierzą transformacji do TH oraz użycie obiektu kalibracyjnego widocznego w obu modalnościach. W pracy znacznik jest przy znamieniu przez cały pomiar, a ROI leży wewnątrz obszaru znacznika, więc problem punktów „skupionych w ramie” jest mniej istotny.

**Uważaj.**
- TRE w pikselach, nie w mm; nie opisano, jak wyznaczono punkty referencyjne ani w którym obrazie liczono piksele (niepewne). Wartości dla EOH/PCEHD/LGHD są tylko na Fig. 4.
- Typ transformacji opisany jako „linear mapping” – nie podano wprost, czy afiniczna, czy projekcyjna (niepewne).
- Zastosowanie: twarz i oddech, ROI prostokątny; nie zmiany skórne i nie obrys.

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 4): „The overview of the proposed method.” – schemat z ramą kalibracyjną i przenoszeniem ROI; przydatność: wysoka (2.2.2, 2.2.4).
- Fig. 2 (s. 5): „The algorithmic steps in pre-transformation.” – wyznaczanie punktów z ramy; średnia.
- Fig. 4 (s. 8): „Average of target registration errors (TRE) for all 50 RGB-thermal image pairs (The image pair is a randomly selected frame of each recorded video).” – porównanie metod; średnia (2.4).
- Fig. 3, 5–12, Table A.1 (s. 14) – dotyczą oddechu; niska.

---

### Han, Pauwels, de Zeeuw, 2013 – Visible and infrared image registration in man-made environments employing hybrid visual features
`han2013` · Pattern Recognition Letters, t. 34, s. 42–51, 2013 (online 4.04.2012; numeru zeszytu brak w tekście) · DOI: 10.1016/j.patrec.2012.03.022 · Podrozdział: 2.2.2

**Streszczenie.** Artykuł dotyczy rejestracji obrazów widzialnych (ViS) i podczerwonych długofalowych (IR) w środowiskach zurbanizowanych (s. 1–2). Autorzy pokazują, że typowe punkty charakterystyczne (SURF, Harris) i deskryptory łat (intensywność, moduł i orientacja gradientu) nie wyznaczają wiarygodnych odpowiedników między IR a ViS (s. 2–3). Metoda ma dwa etapy. Najpierw proste wykryte na krawędziach Canny’ego są dopasowywane konfiguracjami po 4 linie, co daje globalną transformację perspektywiczną (s. 4–6). Następnie punkty Harrisa (maksimum w każdej komórce 32 × 32) są rzutowane przez tę transformację i lokalnie poprawiane, a odwzorowania afiniczne na trójkątach Delaunaya tworzą model lokalnie adaptowany (s. 6–8). Na 9 parach IR–ViS zarejestrowano wszystkie poza nocną (s. 8). Lokalna adaptacja zmniejszyła błąd, np. „Home” z 1,78 do 0,76 piksela (s. 8). Metoda porównawcza (SURF + deskryptory gradientowe + RANSAC) prawie zawsze zawodziła (s. 9).

**Co zawrzeć w pracy.**
- 2.2.2: fizyczna przyczyna trudności. Jasność w IR zależy od temperatury i emisyjności obiektów, w ViS od światła odbitego, więc intensywności nie mają bezpośredniego związku (s. 2).
- 2.2.2: punkty charakterystyczne i porównywanie łat 15 × 15 są zawodne dla pary LWIR–ViS (Fig. 1, s. 2–3; porównanie GM/GO, s. 9). Argument przeciw podejściu SIFT/SURF w systemie.
- 2.2.2: rozwiązanie autorów to struktury geometryczne widoczne w obu modalnościach (proste z granic obiektów) (s. 2, 4). Analogicznie praca wprowadza sztuczny znacznik widoczny w obu modalnościach. Skóra nie ma prostych, a metoda autorów zawodzi tam, gdzie brakuje linii (s. 2).
- 2.2.1/2.2.2: model perspektywiczny jest dokładny dla płaskiej sceny i dobrym przybliżeniem, gdy różnice głębokości są małe względem odległości od kamery. Homografia ma 8 stopni swobody i wymaga co najmniej 4 odpowiedników (s. 4).
- 2.2.1: transformacja globalna (mało parametrów, spójność) a lokalna (lokalne deformacje, ale koszt i brak gwarancji spójności) (s. 4).
- 2.4: ocena na 8 ręcznie oznaczonych punktach, ze średnią i SD błędu (s. 8). To analogia do 8 narożników znacznika w CVAT.

**Liczby i fakty do cytowania.**
- 9 par (6 zewnętrznych, 3 wewnętrzne), w tym wideo „Bridge” (50 klatek) i „Factory” (30 klatek) (s. 8).
- Table 1 (piksele, μ; σ), globalna → lokalna: Home 1,78; 1,82 → 0,76; 1,11. Office 1 6,40; 2,76 → 4,63; 2,43. Shop 2,92; 2,73 → 1,50; 1,58. Bridge 5,28; 3,22 → 4,28; 4,01. Rozdzielczość 384 × 288 (s. 8).
- Deskryptor GM zawiódł dla wszystkich par, GO zadziałał tylko dla „office 1” i „office 2”. „Bridge”: 14 dopasowań wstępnych → 4 po RANSAC → 1 poprawne (s. 9).
- 4–10 par obrazów/s przy niezbyt złożonej scenie (IR 384 × 288, ViS 656 × 490) (s. 9).

**Związek z systemem z pracy.** Artykuł uzasadnia, dlaczego system nie opiera się na naturalnych punktach charakterystycznych. W parze LWIR–ViS wspólne są struktury geometryczne (granice obiektów), a nie lokalna tekstura. Stąd sztuczny znacznik Π z folią, dobrze widoczny w obu modalnościach. Wybór homografii jako modelu dla w przybliżeniu płaskiej sceny ma to samo uzasadnienie (s. 4).

**Uważaj.**
- Dane to sceny zurbanizowane, a dopasowanie linii zakłada kamery na wspólnej platformie (s. 5). Błędy podano w pikselach (średnia ± SD), nie w mm ani jako medianę, więc nie są porównywalne z TRE z pracy.
- Na s. 2 tekst mówi „the majority of extracted interest points is unfortunately shared”, co przeczy kontekstowi. To prawdopodobnie błąd w oryginale (miało być „not shared”), więc nie cytować dosłownie.
- Niespójność: według s. 8 dla „ostatniej pary” zastosowano tylko transformację globalną, a Table 1 podaje dla „Bridge” wynik lokalny (niepewne, której pary dotyczy uwaga).

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 3): „Image statistics that imply problems for IR and ViS image registration. (a) Interest point detection … SURF and Harris … (b) … distribution of Intensity, Gradient Magnitudes, Gradient Orientations” – dlaczego cechy lokalne zawodzą; przydatność: wysoka.
- Fig. 6 (s. 7): „Registration and intermediate results … warped image (from IR to ViS) …” – przykłady nałożenia IR–ViS; przydatność: średnia.
- Fig. 7 (s. 8): „(a) Image pair for which our algorithm fails … (b) … gradient orientation based descriptor”; przydatność: średnia.
- Fig. 8 (s. 9): „(a) Statistics by using two existing descriptors …” – mało poprawnych dopasowań SURF+GM/GO; przydatność: średnia.
- Table 1 (s. 8): „The measurement for transform errors, in which the unit is pixel”; przydatność: średnia.
- Fig. 2 (s. 4), 3 (s. 5), 4 (s. 6), 5 (s. 7), 9 (s. 9): schemat metody, wykrywanie linii, etapy estymacji lokalnej, lokalna adaptacja punktów, czas obliczeń; przydatność: niska.

## 2.2.3 Metody oparte na uczeniu głębokim

### Chen, Diaz-Pinto, Ravikumar i in., 2021 – Deep learning in medical image registration
`chen2021` · Progress in Biomedical Engineering, 3, art. 012003, 2021 · DOI: 10.1088/2516-1091/abd37c · Podrozdział: 2.2.3, 2.3.2

**Streszczenie.** Przegląd metod głębokiej rejestracji obrazów medycznych (DLIR) obejmujący 77 prac, w większości po 2016 r. (s. 6). Rejestracja polega na znalezieniu transformacji, która odwzorowuje obraz ruchomy (*moving*) na stały (*fixed*). Metoda klasyczna to iteracja: model transformacji + miara podobieństwa + optymalizator (s. 2–3, Fig. 1). Autorzy dzielą DLIR na trzy grupy (s. 7):
- sieci jako miara podobieństwa (*deep similarity*);
- sieci parametryzujące transformację: nadzorowane, słabo nadzorowane i nienadzorowane;
- inne zastosowania: cechy, nowa reprezentacja obrazu, uczenie ze wzmocnieniem.

Podstawowe bloki to koder–dekoder (U-Net), STN i GAN (s. 3–6). Po treningu rejestracja wymaga jednego przejścia sieci, zwykle poniżej 1 s na parę (s. 18). Główne wyzwania to różne przetwarzanie wstępne, brak narzędzi klinicznych i mało danych, zwłaszcza wielomodalnych (s. 24). Jako kierunki autorzy wskazują łączenie metod klasycznych z DL oraz wiedzę a priori, np. słabe etykiety (s. 25).

**Co zawrzeć w pracy.**
- 2.2.3: taksonomia DLIR (s. 7, Fig. 6). *Deep similarity* poprawia odporność, ale proces pozostaje iteracyjny i wolny w inferencji (s. 8). Parametryzacja transformacji siecią daje rejestrację w czasie rzeczywistym (s. 8).
- 2.2.3, nadzór pełny: transformacje referencyjne (GT) pochodzą z metod klasycznych albo z danych syntetycznych (s. 8). Bywają nierealistyczne lub ograniczone jakością metody klasycznej (s. 10). Dla rejestracji sztywnej/afinicznej GT łatwo syntetyzować losowymi rotacjami, translacjami i skalowaniem (s. 10).
- 2.2.3, brak nadzoru: do treningu wystarczają pary obrazów. Strata to niepodobieństwo plus regularyzacja, w schemacie „CNN+STN” (s. 11), np. VoxelMorph (U-Net+STN) (s. 11). Problemem są fałdy, czyli ujemny wyznacznik Jakobianu; pomaga regularyzacja gładkości i odwracalności oraz SVF (s. 11–13).
- 2.2.3, słaby nadzór: maski segmentacji lub punkty orientacyjne są używane tylko w treningu. Strata liczona jest między zdeformowaną etykietą ruchomą a stałą (s. 15). Hu i in. (T2W–TRUS) to pierwsza DLIR ze słabymi etykietami (s. 15). Słaby nadzór zwykle daje lepsze wyniki niż wariant nienadzorowany, bez kosztu czasu wykonania (s. 25).
- 2.2.3, GAN: dyskryminator może pełnić rolę uczonej miary podobieństwa. Translacja obrazów (np. Cycle-GAN) sprowadza problem wielomodalny do jednomodalnego (s. 6, 14).
- 2.3.2: U-Net to najczęściej używana architektura w medycznej segmentacji i rejestracji. Ma koder (konwolucje + pooling), dekoder (dekonwolucje) i połączenia skip (s. 4). W rejestracji wejściem jest konkatenacja obrazu ruchomego i stałego, a wyjściem pole deformacji (s. 4, Fig. 2).
- 2.2.3, ograniczenia:
  - publiczne zbiory wielomodalne są tylko trzy (RIRE, VISCERAL Anatomy3, MM-WHS), a większość badań wielomodalnych używa danych prywatnych (s. 20);
  - żadne narzędzie DL nie jest wdrożone klinicznie tak jak ANTs czy Elastix, a sieci są trudne do interpretacji (s. 24).

**Liczby i fakty do cytowania.**
- Przegląd obejmuje prace od 2013 r. (s. 2); 77 prac, większość po 2016 r. (s. 6).
- Pierwsze metody (2013, 2015) używały CNN tylko do ekstrakcji cech; pierwsze sieci przewidujące pola deformacji pojawiły się w 2016 r. (s. 23).
- Rozwój dziedziny przebiegał w czterech etapach: cechy → nadzór → brak/słaby nadzór → dokładność i gładkość (s. 23–24).
- Rejestracja deformowalna jest problemem źle postawionym (*ill-posed*) i nie ma GT dla pola deformacji (s. 3).
- PDD-Net dał poprawę nakładania Dice o 15% (s. 15).

**Związek z systemem z pracy.** System stosuje klasyczną rejestrację globalną: ECC na maskach znacznika, transformacja afiniczna lub homografia. Przegląd wskazuje, że DL ograniczają brak GT i brak wielomodalnych danych publicznych (s. 10, 20, 24). To wspiera ten wybór przy 94 parach. Oparcie korespondencji na maskach przypomina ideę słabego nadzoru (s. 15), ale bez uczenia. U-Net do segmentacji znacznika ma oparcie w s. 4.

**Uważaj.**
- Teksty o dokładności są sprzeczne. Na s. 3 DL nie dało przełomu w dokładności, tylko przyspieszenie. Na s. 18 większość badań pokazuje wyższą dokładność. Na s. 25 w części zadań dokładność jest co najwyżej porównywalna. Cytuj ostrożnie.
- Przegląd dotyczy głównie 3D MRI/CT; nie obejmuje RGB–termowizji ani dermatologii.
- Tabele są w tekście rozbite na kolumny, więc trzeba je sprawdzić w PDF.

**Rysunki i tabele (kandydaci).** Artykuł jest na licencji CC BY 4.0 (s. 2).
- Fig. 1 (s. 3): „A flowchart of medical image registration framework.” – klasyczna pętla rejestracji; przydatność: wysoka (2.2.1/2.2.3).
- Fig. 2 (s. 4): „An example of the U-Net framework used for brain MRI image registration…” – U-Net przewiduje pole deformacji; wysoka (2.2.3/2.3.2).
- Fig. 6 (s. 7): „Categories of deep learning-based image registration methods.” – taksonomia; wysoka.
- Fig. 3 (s. 4) STN, Fig. 4 (s. 5) „An example of GAN-based image registration…”, Table 3 (s. 14) „A summary of weakly-supervised DL methods” – średnia.
- Fig. 5 (s. 6), 7 (s. 18), 9 (s. 23): liczby publikacji; Fig. 8 (s. 19): przykład Voxelmorph-diff; Table 1 (s. 9), 2 (s. 12), 4 (s. 17), 5 (s. 21–22): metody nadzorowane, nienadzorowane, inne użycia, zbiory danych – niska.

---

### Hu, Modat, Gibson i in., 2018 – Weakly-supervised convolutional neural networks for multimodal image registration
`hu2018` · Medical Image Analysis, 49, 1–13, 2018 · DOI: 10.1016/j.media.2018.07.002 · Podrozdział: 2.2.3

**Streszczenie.** W rejestracji wielomodalnej brakuje GT korespondencji na poziomie wokseli, a miary intensywnościowe są zawodne (s. 1–2). Autorzy proponują sieć CNN 3D, która z pary obrazów przewiduje gęste pole przemieszczeń (DDF). Sieć uczy się przez dopasowanie etykiet anatomicznych (narządy, granice, punkty specyficzne dla pacjenta). Etykiety są potrzebne tylko w treningu, a w inferencji wystarczają same obrazy (s. 1, 4). Strata to wieloskalowy Dice plus regularyzacja energią zginania, bez członu intensywnościowego (s. 3–4, 6). Dane: 108 par MR T2 – TRUS 3D od 76 pacjentów z rakiem prostaty (s. 6). Ocena: 12-krotna walidacja krzyżowa na poziomie pacjentów (s. 7). Wynik: mediana TRE 3,6 mm i mediana Dice gruczołu 0,87 (s. 1, 8). Sieć wykonuje około 4 rejestracji 3D na sekundę (s. 8).

**Co zawrzeć w pracy.**
- 2.2.3: wzorcowy przykład rejestracji słabo nadzorowanej. Etykiety wyższego poziomu łatwiej oznaczyć wiarygodnie niż korespondencję wokselową (s. 1–2). Podobieństwo etykiet nie zależy od modalności (s. 4).
- 2.2.3/2.2.1: argument przeciw miarom intensywnościowym. Różne procesy akwizycji mogą dawać korelację statystyczną struktur, które anatomicznie sobie nie odpowiadają (s. 1–2). Generyczne FFD z NMI/NCC/SSD zawiodło na tych danych (s. 10–11).
- 2.4 (pomocniczo): Dice, Jaccard i entropia krzyżowa nie uwzględniają odległości, gdy obiekty się nie nakładają (s. 4).
- 2.4 (pomocniczo): TRE liczono jako RMS odległości środków ciężkości par landmarków na pacjenta, a Dice dla gruczołu (s. 7). Rzadkie landmarki traktuje się jako próbki błędu gęstej rejestracji; to standardowa praktyka (s. 11).

**Liczby i fakty do cytowania.**
- Adnotowano 834 pary etykiet: 108 (12,9%) gruczoł, 213 (25,5%) wierzchołek/podstawa, 214 (25,7%) granice stref, 37 (4,4%) cewka, 262 (31,4%) struktury specyficzne dla pacjenta (s. 6).
- Adnotacja trwała ponad 200 h (s. 6); to średnio ok. 8 par landmarków na obraz (s. 11).
- Wokseli 0,8 × 0,8 × 0,8 mm³ (s. 6); trening 48 h na GPU 12 GB (s. 6).
- Wariant Baseline: TRE mediana 3,6 mm (kwartyle 2,3 i 6,5), DSC 0,87 (0,82 i 0,89) (s. 8).
- Global-Net (tylko transformacja afiniczna): TRE 5,8 mm, DSC 0,77 (Table 1, s. 8).
- TRE przed rejestracją: 34,8 mm. Wyrównanie środków gruczołu: 19,6 mm. Następnie FFD z NMI/NCC/SSD: 20,6/24,7/25,6 mm (s. 10–11).
- Wcześniejsze metody dedykowane osiągały oczekiwany TRE 1,4–2,8 mm na 8–29 przypadkach (s. 10).
- Przy α = 0,5 nie wystąpiły ujemne wyznaczniki Jakobianu (s. 10).

**Związek z systemem z pracy.** System także opiera korespondencję na etykietach (maskach znacznika), a nie na intensywnościach, ale robi to klasycznie (ECC), bez uczenia. Słabszy wynik MI Mattesa w badaniu E4 jest zgodny z obserwacją autorów o miarach intensywnościowych. Schemat oceny (TRE na punktach + Dice struktury) odpowiada badaniom E1 i E2.

**Uważaj.**
- Artykuł dotyczy rejestracji 3D, deformowalnej, MR–TRUS prostaty. Nie porównuj bezpośrednio 3,6 mm z 0,62 mm z pracy.
- W tekście jest sprzeczność: „all 9 median TREs are larger than 24 mm” (s. 10), a dla NMI po inicjalizacji podano 20,6 mm. Cytuj wartości z Table 2.
- Nie było niezależnego zbioru testowego, tylko walidacja krzyżowa (s. 11).

**Rysunki i tabele (kandydaci).** Licencja CC BY (s. 1).
- Fig. 2 (s. 3): „The upper part illustrates the training strategy of the proposed weakly-supervised registration framework… The lower part depicts the resulting inference…” – etykiety tylko w treningu; przydatność: wysoka (2.2.3).
- Table 2 (s. 11): „Summary of the results from the intensity-based nonrigid image registrations and those from other previous studies” – średnia.
- Table 1 (s. 8): „Summary of the cross-validation results…”; Fig. 9 (s. 9): przykładowe przekroje MR / MR po deformacji / TRUS – średnia.
- Fig. 1 (s. 3) landmarki; Fig. 3 (s. 4) wieloskalowe etykiety; Fig. 4 (s. 5) architektura; Fig. 5–7 (s. 7) warianty, Global-Net, Composite-Net; Fig. 8 (s. 8) wykresy pudełkowe; Fig. 10 (s. 10) Jakobian/DDF – niska.

## 2.2.4 Fuzja i wizualizacja nałożenia

### Zhang, Demiris, 2023 – Visible and Infrared Image Fusion Using Deep Learning
`zhang2023` · IEEE Transactions on Pattern Analysis and Machine Intelligence, 45(8), 10535–10554, 2023 · DOI: 10.1109/TPAMI.2023.3261282 · Podrozdział: 2.1, 2.2.2, 2.2.3, 2.2.4

**Streszczenie.** Przegląd głębokich metod fuzji obrazów widzialnych i podczerwonych (VIF, *visible and infrared image fusion*). Przez „infrared” autorzy rozumieją podczerwień termiczną (s. 1). Autorzy przeczytali ponad 200 prac (s. 2) i dzielą metody według modelu (CNN, autoenkodery, GAN, transformery), według nadzoru (nadzorowane/nienadzorowane) oraz na metody end-to-end i pozostałe (s. 2–3). Nie istnieje obraz referencyjny fuzji (*ground truth*), dlatego większość metod jest nienadzorowana, a funkcje straty buduje się z metryk jakości fuzji (s. 2, 11, 12). Na benchmarku VIFB najnowsze metody głębokie nie były lepsze od starszych, a część metod klasycznych (LatLRR, LP_SR, NSCT_SR) okazała się konkurencyjna (s. 15). Autorzy uznają wyrównanie (rejestrację) obrazów VIS–IR za wciąż otwarty problem i wskazują wspólne uczenie rejestracji i fuzji jako kierunek rozwoju (s. 16).

**Co zawrzeć w pracy.**
- 2.1 (1 zdanie): obraz widzialny ma bogatą teksturę, ale zależy od oświetlenia; obraz IR niesie informację termiczną niezależną od oświetlenia, ale ma za mało szczegółów tekstury (s. 1).
- 2.2.2 (1 zdanie): wyrównanie VIS–IR jest „open question”, a idealne wyrównanie jest bardzo trudne (s. 16). Przyczyny to różne mechanizmy obrazowania i różne parametry kamer (s. 11). Nawet popularne zbiory RGB–IR (LasHeR, RGBT234, M3FD) mają błędy wyrównania (s. 16).
- 2.2.3: wspólne uczenie rejestracji i fuzji:
  - Wang i in. [111] tworzą obraz pseudo-IR przez transfer stylu, a potem uczą pole przemieszczeń (DVF) między IR a pseudo-IR, czyli „łatwiejszy” problem jednomodalny. Strata składa się z członów: transfer stylu + regularyzacja + rejestracja + fuzja (s. 11).
  - RFNet [164]: fuzja daje sprzężenie zwrotne dla rejestracji, ale metoda dotyczy bliskiej podczerwieni, nie termowizji (s. 11).
  - SuperFusion [199] łączy rejestrację, fuzję i zadanie docelowe (s. 16).
- 2.2.4: trzy poziomy fuzji (s. 2):
  - pikselowy: najpierw obraz fuzji, potem zadanie;
  - cech: fuzja wyekstrahowanych cech;
  - decyzji: zadanie wykonane osobno w każdej modalności, potem łączenie wyników.
  W literaturze „VIF” oznacza zwykle fuzję pikselową (s. 2).
- 2.2.4: metoda VIF ma trzy etapy: ekstrakcja cech → fuzja cech → rekonstrukcja obrazu (s. 2, Fig. 4). Klasyczne grupy metod: multiscale transform, sparse representation, subspace, saliency, hybrydowe (s. 1).
- 2.2.4 (wizualizacja barwna): większość metod łączy tylko obrazy w skali szarości. RGB konwertuje się do YCbCr, kanał Y łączy z IR, a Cb/Cr zwykle łączy się metodami klasycznymi, co grozi utratą informacji (s. 12–13).
- 2.2.4: w praktyce częściej występuje obraz VIS o wysokiej i IR o niskiej rozdzielczości. Część metod wymaga stosunku rozdzielczości równego 4 (s. 11).

**Liczby i fakty do cytowania.**
- Fuzja obrazów jest badana od ponad 30 lat (s. 2).
- Liczba prac DL-VIF szybko rosła w latach 2018–2022 (s. 1, Fig. 2).
- GAN wprowadzono do VIF w 2019 r. (FusionGAN), a transformery w 2021 r. (s. 7, 9, 11).
- VIFB to 21 par obrazów, 20 metod i 13 metryk (s. 12, 14).
- Brak powszechnie uznanej metryki, a wyniki ilościowe często nie zgadzają się z oceną wizualną (s. 14).

**Związek z systemem z pracy.** Znamię nie jest widoczne na termowizji, co zgadza się z uwagą autorów, że IR ma za mało tekstury (s. 1). To uzasadnia segmentację na zdjęciu i przeniesienie ROI przez macierz T. System nie tworzy obrazu fuzji pikselowej. Nakładka ROI jest raczej łączeniem wyników – to moja interpretacja, nie teza artykułu. Rejestracja znacznikiem odpowiada na problem wyrównania, który przegląd uznaje za otwarty.

**Uważaj.**
- Przegląd dotyczy scen naturalnych (śledzenie, detekcja, jazda), nie medycyny ani skóry.
- Autorzy nie podają liczbowych wyników rejestracji; metody [111], [164] tylko opisują.
- Tabele I–III są w PDF grafikami, więc w tekście nie ma ich treści. Wartości trzeba sprawdzić w PDF; przedruk rysunków wymaga zgody IEEE (s. 1).

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 1): „The benefit of visible and infrared image fusion…” – rzędy: VIS, IR, wynik fuzji MGFF; przydatność: średnia (2.1/2.2.4, sceny niemedyczne).
- Fig. 4 (s. 3): „Three stages of VIF methods, i.e., feature extraction, feature fusion, and image reconstruction.” – schemat; przydatność: średnia (2.2.4).
- Fig. 2 (s. 2), 3 (s. 3), 5 (s. 3), 6 (s. 5), 7 (s. 7), 8 (s. 8), 9 (s. 10), 10 (s. 12), 11 (s. 13): statystyka prac, oś czasu, architektury jedno-/dwugałęziowe oraz CNN/AE/GAN/transformer, VIF jakościowe vs zorientowane na zastosowanie, frameworki – niska.
- Table I (s. 4) „An overview of representative deep learning-based VIF methods”, Table II (s. 14) „Some VIF methods published in top journals…”, Table III (s. 15) „Quantitative performance comparison on VIFB” – niska.

## 2.3.2 U-Net i architektury koder–dekoder

### Ronneberger, Fischer, Brox, 2015 – U-Net: Convolutional Networks for Biomedical Image Segmentation
`ronneberger2015` · MICCAI 2015, Part III, LNCS 9351, s. 234–241, 2015 (Springer) · DOI: 10.1007/978-3-319-24574-4_28 · Podrozdział: 2.3.2

Numeracja: (s. N/M) = strona PDF N / strona tomu M.

**Streszczenie.** Problem: segmentacja obrazów biomedycznych przy bardzo małej liczbie oznaczonych obrazów (s. 1/234). Metoda: sieć w pełni konwolucyjna w kształcie U – ścieżka kurcząca (contracting path) zbiera kontekst, symetryczna ścieżka rozszerzająca (expanding path) zapewnia precyzyjną lokalizację, a cechy wysokiej rozdzielczości z kodera są konkatenowane z cechami dekodera (s. 1/234, s. 2/235). Uczenie opiera się na intensywnej augmentacji, głównie deformacjach sprężystych (elastic deformations), i ważonej entropii krzyżowej wymuszającej naukę granic między stykającymi się komórkami (s. 3/236, s. 5/238). Na wyzwaniu ISBI 2012 (mikroskopia elektronowa, 30 obrazów treningowych 512 × 512) U-Net uzyskał najlepszy błąd deformacji (warping error) 0,0003529 (s. 6/239). W ISBI Cell Tracking Challenge 2015: IoU 92% (PhC-U373, 35 obrazów) i 77,5% (DIC-HeLa, 20 obrazów) wobec 83% i 46% drugiej metody (s. 7/240). Wniosek autorów: dzięki deformacjom sprężystym sieć potrzebuje bardzo niewielu oznaczonych obrazów, a trening trwa ok. 10 h (s. 7/240).

**Co zawrzeć w pracy.**
- 2.3.2, motywacja: przesuwane okno (sliding window, Ciresan i in.) jest wolne i wymusza kompromis lokalizacja–kontekst; U-Net rozwija FCN (fully convolutional network), zastępując pooling zwiększaniem rozdzielczości (s. 2/235).
- 2.3.2, architektura: koder – dwa sploty 3 × 3 bez dopełnienia (unpadded) + ReLU, max pooling 2 × 2 z krokiem 2, podwajanie kanałów; dekoder – zwiększenie rozdzielczości + splot 2 × 2 („up-convolution”) połowiący kanały, konkatenacja z przyciętą mapą z kodera, dwa sploty 3 × 3 + ReLU; na końcu splot 1 × 1; brak warstw w pełni połączonych (s. 3/236, s. 4/237).
- 2.3.2, połączenia skrótowe (skip connections): cechy wysokiej rozdzielczości z kodera umożliwiają lokalizację; duża liczba kanałów w dekoderze przenosi kontekst do wyższych rozdzielczości, stąd symetryczny kształt U (s. 2/235, s. 3/236).
- 2.3.2, augmentacja: przesunięcia, obroty, deformacje, zmiany jasności; losowe deformacje sprężyste nazwane „kluczową koncepcją” przy bardzo małej liczbie obrazów (s. 5/238) – argument za własnym U-Netem na małym zbiorze termogramów.
- 2.3.2, strata: softmax po pikselach + entropia krzyżowa z mapą wag w(x) równoważącą częstość klas i podkreślającą granice (wzory 1–2) (s. 4/237, s. 5/238).

**Liczby i fakty do cytowania.**
- 23 warstwy splotowe; końcowy splot 1 × 1 mapuje 64-składnikowy wektor cech na klasy (s. 4/237).
- SGD (Caffe), batch = 1 obraz (preferowane duże kafle), momentum 0,99 (s. 4/237).
- Mapa wag: w0 = 10, σ ≈ 5 pikseli; inicjalizacja Gaussa o odchyleniu √(2/N) (s. 5/238).
- Deformacje: przesunięcia na siatce 3 × 3, odchylenie 10 pikseli, interpolacja dwusześcienna; dropout na końcu ścieżki kurczącej (s. 5/238, s. 6/239).
- ISBI EM (średnia z 7 obróconych wersji wejścia, bez pre-/post-processingu): warping error 0,0003529, Rand error 0,0382 vs Ciresan i in. 0,000420 i 0,0504 (s. 6/239).
- Cell Tracking 2015: IoU 0,9203 (PhC-U373) i 0,7756 (DIC-HeLa) (Table 2, s. 7/240).
- < 1 s na obraz 512 × 512 (s. 1/234); trening 10 h na NVidia Titan 6 GB (s. 7/240).

**Związek z systemem z pracy.** Własny mały U-Net do segmentacji znacznika na termogramach 320 × 240 realizuje główną tezę artykułu: koder–dekoder z połączeniami skrótowymi i silną augmentacją da się wytrenować na bardzo małym zbiorze (w pracy 94 pary). To źródło pierwotne architektury, względem którego trzeba opisać zmiany we własnym wariancie.

**Uważaj.**
- Oryginał używa splotów bez dopełnienia – wyjście jest mniejsze od wejścia, mapy z kodera są przycinane (s. 4/237). Dopełnienie, mniej kanałów/poziomów, BN czy strata Dice we własnym modelu to modyfikacje, nie cechy oryginału.
- U-Net był pierwszy w rankingu EM według warping error, ale w Rand error lepsze były metody z post-processingiem specyficznym dla zbioru (s. 6/239) – nie pisz „najlepszy we wszystkich miarach”.
- Brak Dice, dermatologii i termowizji – wyniki dotyczą mikroskopii (EM, kontrast fazowy, DIC).

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 2/235): „U-net architecture (example for 32x32 pixels in the lowest resolution)…” – schemat U z liczbą kanałów i rozmiarami map; przydatność: wysoka (lepiej przerysować schemat własnego modelu z odwołaniem do oryginału).
- Table 2 (s. 7/240): „Segmentation results (IOU) on the ISBI cell tracking challenge 2015.” – przydatność: średnia (wystarczy liczba w tekście).
- Fig. 2 (s. 3/236): „Overlap-tile strategy for seamless segmentation of arbitrary large images…”; Fig. 3 (s. 5/238): „HeLa cells on glass recorded with DIC… (d) map with a pixel-wise loss weight…”; Fig. 4 (s. 7/240): „Result on the ISBI cell tracking challenge…”; Table 1 (s. 6/239): „Ranking on the EM segmentation challenge (march 6th, 2015), sorted by warping error.” – przydatność: niska.

---

### Xiao, Liu, Zhou i in., 2018 – Unified Perceptual Parsing for Scene Understanding
`xiao2018upernet` · ECCV 2018, LNCS 11209, s. 432–448, 2018 (Springer) · DOI: 10.1007/978-3-030-01228-1_26 · Podrozdział: 2.3.3

Numeracja: (s. N/M) = strona PDF N / strona tomu M.

**Streszczenie.** Artykuł wprowadza zadanie ujednoliconego parsowania percepcyjnego (Unified Perceptual Parsing, UPP): jednoczesnego rozpoznania sceny, obiektów, części, materiałów i tekstur (s. 1/432, s. 4/435). Proponuje wielozadaniową sieć UPerNet – piramidę cech FPN (Feature Pyramid Network) z modułem PPM (Pyramid Pooling Module) z PSPNet na ostatniej warstwie szkieletu ResNet – i uczenie z heterogenicznych anotacji: w każdej iteracji losowane jest jedno źródło danych i aktualizowana tylko związana z nim ścieżka (s. 2/433, s. 7/438, s. 9/440). Dane: Broden+ – 57 095 obrazów z ADE20K, Pascal-Context, Pascal-Part, OpenSurfaces i DTD; 51 617 treningowych i 5 478 walidacyjnych (s. 4/435, s. 6/437). W segmentacji semantycznej ADE20K (ResNet-50) FPN + PPM + fuzja osiąga mIoU 41,22% i dokładność pikselową 79,98% (s. 10/441) – prawie jak PSPNet przy 63% czasu treningu (s. 8/439). Dodanie PPM do FPN daje +4,87/+3,09 pkt mIoU/P.A. (s. 11/442). Sieć posłużyła też do odkrywania relacji między pojęciami, np. scena–obiekt (s. 12/443–15/446).

**Co zawrzeć w pracy.**
- 2.3.3: UPerNet w oryginale to sieć do parsowania scen naturalnych ze szkieletem CNN (ResNet), nie model medyczny (s. 1/432, s. 8/439).
- Budowa: szkielet daje mapy C2–C5, FPN – P2–P5 o krokach próbkowania 4, 8, 16, 32; PPM przed gałęzią top-down FPN; połączenia boczne (lateral connections) wnoszą semantykę wysokiego poziomu do niższych poziomów (s. 7/438, s. 8/439).
- PPM: empiryczne pole recepcyjne głębokiej CNN jest znacznie mniejsze od teoretycznego, PPM wnosi globalny kontekst (s. 7/438).
- Fuzja: P2–P5 skalowane interpolacją dwuliniową do rozmiaru P2, konkatenowane i łączone splotem; fuzja wszystkich poziomów daje najlepszy wynik (s. 8/439, s. 11/442).
- Krytyka sieci dylatacyjnych: duży koszt obliczeń i pamięci oraz użycie tylko najgłębszej mapy cech, podczas gdy niższe warstwy niosą cechy lokalne (krawędzie, kolory), a wyższe – złożone wzorce (s. 9/440, s. 10/441) – uzasadnienie dekodera wieloskalowego.

**Liczby i fakty do cytowania.**
- Broden+: ADE20K 22 210, Pascal-Context/Part 10 103, OpenSurfaces 19 142, DTD 5 640 obrazów (s. 4/435, s. 5/436); 365 scen, 335 obiektów, 152 części, 26 materiałów, 47 tekstur (Table 1, s. 5/436).
- Miary: dokładność pikselowa (P.A.), mIoU, mIoU-bg, top-1 (s. 6/437).
- Trening: polityka „poly” (lr 0,02, potęga 0,9), weight decay 0,0001, momentum 0,9, krótszy bok losowany z {300, …, 600}, szkielet wstępnie uczony na ImageNet, 8 GPU × 2 obrazy, zsynchronizowana BN (s. 9/440); warstwy dodatkowe 512 kanałów + BN (s. 8/439).
- ADE20K, ResNet-50 (mIoU/P.A., %): FCN 29,39/71,32; PSPNet 41,68/80,04 (61,1 h); FPN (/4) 35,26/76,52 (21,2 h); FPN + PPM 40,13/79,61 (27,8 h); FPN + PPM + Fusion 41,22/79,98 (38,7 h) (Table 2, s. 10/441).
- UPP: obiekty 24,72/78,03; materiały 52,78/84,32 → 54,19/84,45 przy treningu łącznym; scena top-1 71,35%; tekstura 35,10 (s. 11/442, s. 12/443).

**Związek z systemem z pracy.** System używa dekodera UperNet nad koderem PanDerm (ViT-L); artykuł jest źródłem pierwotnym dekodera i uzasadnia łączenie cech wielu poziomów (FPN) z globalnym kontekstem (PPM). Nie dostarcza wyników dla obrazów medycznych.

**Uważaj.**
- Oryginał: szkielet ResNet, sceny naturalne (ADE20K, Broden+); brak ViT i dermatologii – połączenie z ViT/PanDerm cytuj z innych źródeł.
- FPN (Lin i in.) i PPM (PSPNet, Zhao i in.) nie są wkładem tego artykułu (s. 7/438); wkładem są zadanie UPP, sieć UPerNet i strategia uczenia z heterogenicznych anotacji (s. 3/434).
- Oryginalna pisownia: „UPerNet”. Table 3 jest w wyciągniętym tekście nieczytelna – liczby UPP pochodzą z tekstu (s. 11/442–12/443).

**Rysunki i tabele (kandydaci).**
- Fig. 4 (s. 7/438): „UPerNet framework for Unified Perceptual Parsing. Top-left: The Feature Pyramid Network (FPN) with a Pyramid Pooling Module (PPM) appended on the last layer of the back-bone network…” – schemat architektury i głów zadań; przydatność: wysoka (przerysować tylko FPN + PPM + fuzję).
- Table 2 (s. 10/441): „Detailed analysis of our framework based on ResNet-50 v.s. state-of-the-art methods on ADE20K dataset…” – ablacja FPN/PPM/fuzji; przydatność: średnia.
- Fig. 1 (s. 2/433, przykład parsowania wielopoziomowego), Fig. 2 (s. 5/436), Fig. 3 (s. 6/437), Fig. 5 (s. 13/444), Fig. 6 (s. 14/445), Table 1 (s. 5/436), Table 3 (s. 11/442): statystyki i przykłady Broden+, predykcje, grafy relacji, wyniki UPP – przydatność: niska.

---

### Mirikharaji, Abhishek, Bissoto i in., 2023 – A survey on deep learning for skin lesion segmentation
`mirikharaji2023` · Medical Image Analysis 88 (2023), art. 102863 · DOI: 10.1016/j.media.2023.102863 · Podrozdział: 2.3.2, 2.3.3, 2.4

**Streszczenie.** Przegląd 177 prac (2014–2022) o głębokiej segmentacji zmian skórnych na obrazach dermatoskopowych i klinicznych, analizowanych pod kątem danych (zbiory, preprocessing, dane syntetyczne), modelu (architektury, moduły, straty) i oceny (anotacje, miary) (s. 1, s. 2). Trudności: artefakty (włosy, znaczniki chirurgiczne, ciemne rogi, pęcherzyki), zmienność kształtu i rozmiaru, różne kolory skóry, niski kontrast, niejednoznaczne granice i brak dużych zbiorów z maskami ekspertów; zadanie jest niemal zawsze binarne (s. 2). Zbiory ISIC wykorzystuje 168 ze 177 prac, PH2 – 56 (s. 6). Najczęstsze moduły to połączenia skip (112 prac) i rezydualne (70), najczęstsze straty – entropia krzyżowa (96) i Dice (53) (s. 10, s. 14). Omówiono zmienność anotatorów, łączenie wielu masek i własności miar (s. 16–17, s. 28–29). Autorzy uznają problem za otwarty (najlepszy progowany Jaccard na tablicy ISIC 2018: 83,6%) i postulują badania na obrazach klinicznych, lekkie modele mobilne i miary brzegowe (s. 29–30).

**Co zawrzeć w pracy.**
- 2.3.2: FCN i U-Net jako podstawa większości modeli; koder–dekoder; połączenia skip zachowują lokalizację przy granicach i dają ostrzejsze kontury (s. 9). Pyramid pooling – równoległe poolingi o różnych rozmiarach, upsampling, konkatenacja (s. 11) – pomost do UperNet.
- 2.3.2: Transformery w segmentacji zmian skórnych od 2021 r. (12 prac): TransUNet, Swin-Unet, TransFuse, FAT-Net (s. 10, s. 13) – kontekst dla kodera ViT.
- 2.3.3: zbiory z maskami (Table 1): PH2, ISIC 2016–2018, HAM10000, DermoFit, DermQuest (s. 4–5); nakładanie się zbiorów ISIC i ich ograniczenia (mała różnorodność geograficzna/etniczna, zaszumione maski) (s. 5).
- 2.1/2.3.3: obrazy kliniczne (zwykły aparat, telefon) są łatwo dostępne, ale gorszej jakości; dermoskopia usuwa odbicia i ujawnia struktury podpowierzchniowe (s. 2, s. 3). Większość modeli trenowano i oceniano na dermoskopii z powodu braku dużych klinicznych zbiorów z maskami (s. 30, Fig. 10) – luka badawcza (2.5).
- 2.4: definicje miar przez TP/FP/FN/TN (Table 2, s. 17); J = F/(2 − F), więc Dice i Jaccard razem nie wnoszą niezależnej informacji; 1 − J jest metryką, 1 − F nie; dokładność (AC) faworyzuje klasę większościową (s. 28).
- 2.4: miary regionowe są mało czułe na nieregularność brzegu; miary brzegowe prawie nieużywane poza symetryczną odległością Hausdorffa (wrażliwą na szum); autorzy postulują ich użycie (s. 29) – uzasadnienie HD95/ASSD.
- 2.4: zmienność anotatorów ogranicza osiągalną zgodność; z powodu kosztów ocenia się zwykle względem jednej maski (s. 16); najczęstsza anotacja to ręczne obrysowanie na komputerze, m.in. wielokątem (s. 16) – odniesienie do CVAT.

**Liczby i fakty do cytowania.**
- PH2: pierwszy publiczny zbiór z maskami; 200 obrazów dermatoskopowych (20% czerniaków, 40% znamion atypowych, 40% zwykłych), 768 × 560 pikseli (s. 4).
- DermoFit: 1300 obrazów klinicznych, 10 kategorii diagnostycznych, kontrolowane oświetlenie (s. 4).
- ISIC 2016: 1279 obrazów (900/379); ISIC 2017: 2750 (2000/150/600) (s. 4); ISIC 2018 (segmentacja): 2594/100/1000, 0,5–29 Mpx (s. 5).
- HAM10000: 10 015 obrazów, maski jednego dermatologa – największy publiczny zbiór do segmentacji (s. 5).
- Nakładanie ISIC 2016–2018: 1940 obrazów w ≥ 2 zbiorach, 706 we wszystkich 3 (s. 5).
- ISIC 2017 najpopularniejszy (117 prac); 36 prac z oceną międzyzbiorową (s. 6).
- Nadzór: 163 prace w pełni nadzorowane, 9 pół-/słabo nadzorowanych, 5 samonadzorowanych (s. 8).
- Straty: 65 prac łączy straty (CE + Dice 27, CE + Jaccard 11) (s. 14).
- Augmentacja: obrazy zmian są izotropowe, więc można stosować odbicia pionowe i obroty o duże kąty (s. 6).
- Fortina i in.: 12 dermatologów, 77 obrazów, średnia parowa niezgodność XOR ≈ 15%, w 10% przypadków > 28% (s. 16).
- ISIC 2016/2017: ranking wg Jaccarda; ISIC 2018: progowany Jaccard, próg 0,65 (s. 28).
- Kod publiczny w 38/177 prac (21,47%) (s. 30).

**Związek z systemem z pracy.** Przegląd uzasadnia douczanie na ISIC 2018 Task 1 (standardowy podział, dominująca rodzina zbiorów) i wskazuje lukę, którą praca adresuje: ocenę na zdjęciach klinicznych z telefonu, dla których brak dużych zbiorów z maskami (s. 30). Wspiera też zestaw miar: Dice/IoU jako standard, HD95/ASSD jako rzadkie miary brzegowe (s. 29).

**Uważaj.**
- Table 1 (s. 5) podaje dla HAM10000 „1113 non-melanomas, 8902 melanomas”, co przeczy tekstowi (czerniaki 11,1%) – nie cytuj. Wymiary PH2 w Table 1 (553 × 763 do 577 × 769) różnią się od tekstu (768 × 560, s. 4).
- Brak HD95/ASSD z nazwy, modeli bazowych (foundation models) i PanDerm; prace tylko do 2022 r.
- Table 3 podaje Jaccard (czasem przeliczony z Dice) na różnych zbiorach – nie porównuj wprost z Dice z pracy.

**Rysunki i tabele (kandydaci).**
- Fig. 10 (s. 30): „Number of skin lesion images with ground-truth segmentation maps per year categorized based on modality…” – stagnacja danych klinicznych; przydatność: wysoka (2.3.3/2.5).
- Table 1 (s. 5): „Public skin lesion datasets with lesion segmentation annotations…” – przydatność: wysoka (w skrócie: PH2, ISIC 2018, HAM10000, DermoFit).
- Fig. 1 (s. 3): „Factors that complicate dermoscopy image segmentation.” – przydatność: średnia.
- Fig. 9 (s. 17): „Sample segmentation results demonstrating inter-annotator disagreements…” – przydatność: średnia (2.4).
- Table 2 (s. 17): „Definitions of true positive, false negative, false positive, and true negative pixels…” – przydatność: średnia (2.4).
- Fig. 2 (s. 4), 3 (s. 6), 4 (s. 7), 5 (s. 8), 6 (s. 10), 7 (s. 10), 8 (s. 14): struktura przeglądu, użycie zbiorów, augmentacje, poziomy nadzoru, taksonomia, moduły, straty; Table 3 (s. 18–28): 177 prac – przydatność: niska (liczby lepiej w tekście).

## 2.3.3 Modele bazowe w dermatologii i zbiory danych

### Yan, Yu, Primiero i in., 2025 – A Multimodal Vision Foundation Model for Clinical Dermatology
`yan2025panderm` · preprint arXiv:2410.15038v3 [cs.CV], 13.04.2025 (75 s.: artykuł, metody, Extended Data, bibliografia) · DOI: brak w tekście · Podrozdział: 2.3.3 (pomocniczo 2.3.2, 2.2.1)

**Streszczenie.** Autorzy wskazują, że dotychczasowe modele AI w dermatologii rozwiązują pojedyncze zadania na jednej modalności (np. diagnostykę raka z dermatoskopii), co ogranicza ich użyteczność kliniczną (s. 2–3). Proponują PanDerm – multimodalny model bazowy (foundation model) z koderem ViT-Large, pretrenowany samonadzorowanie (self-supervised learning) na 2 149 706 nieoznaczonych obrazach z 11 źródeł w 4 modalnościach: kafelki TBP (total body photography), dermatopatologia, zdjęcia kliniczne i dermatoskopowe (s. 17–18). Pretrening łączy przewidywanie reprezentacji zamaskowanych łat (masked latent modeling) z dopasowaniem do cech nauczyciela CLIP-Large (s. 4, 20–21). Model oceniono na 28 zbiorach testowych (benchmarks): przesiew, stratyfikacja ryzyka, diagnostyka różnicowa, segmentacja zmian, monitorowanie w czasie, predykcja przerzutów i rokowanie (s. 2). W segmentacji, z dekoderem UperNet, uzyskał Dice 0,910 i Jaccard 0,846 na ISIC2018 oraz 0,949 i 0,910 na HAM10000 – lepiej niż SL-ImageNet, autoSMIM i BATFormer oraz nieznacznie lepiej niż MedSAM (s. 12, 56–57). Najlepszemu z pozostałych modeli dorównywał przy 5% danych treningowych (s. 12). W badaniach z udziałem lekarzy (reader studies) m.in. podniósł trafność diagnoz klinicystów na obrazach dermatoskopowych o 11% (s. 2). Autorzy wnioskują, że modele bazowe wyspecjalizowane w jednej dziedzinie mogą być praktyczniejsze niż ogólne modele biomedyczne (s. 16).

**Co zawrzeć w pracy.**
- 2.3.3 – definicja modelu bazowego wg autorów: duże sieci pretrenowane samonadzorowanie na dużych, zróżnicowanych, często nieoznaczonych danych, które pozwalają douczać modele przy małej liczbie etykiet (s. 3). Autorzy celowo unikali obrazów z internetu, by ograniczyć przeciek zbiorów testowych (np. ISIC) do pretreningu (s. 15).
- 2.3.3 – dane pretreningu: 757 890 kafelków TBP (35,3%), 547 047 kafelków dermatopatologii (25,4%), 460 328 zdjęć klinicznych (21,4%), 384 441 obrazów dermatoskopowych (17,9%) (s. 5, 18); źródła m.in. kohorty MYM i HOP, MMT (>150 klinik w Australii i Nowej Zelandii), ISIC2024, TCGA-SKCM (s. 18–20).
- 2.3.3 – architektura: koder ViT-Large (24 bloki, osadzenia 1024-wymiarowe, wejście 224 × 224), regresor zamaskowanych łat (cross-attention), nauczyciel CLIP-Large; maskowanie 50% łat; straty dopasowania reprezentacji łat widocznych i zamaskowanych do cech CLIP (s. 20–21). Start z wag ImageNet-1K, 500 epok, 4 × H100 (s. 21). W zadaniach docelowych używany jest tylko koder (s. 22).
- 2.3.3 / 2.3.2 – segmentacja: koder PanDerm + dekoder UperNet „following the official ViT implementation” (tak samo dla bazowego ViT-L z wagami ImageNet, tj. SL-ImageNet); wejście 224 × 224; augmentacja (color jitter, obrót, odbicie); AdamW, lr 5e-4, weight decay 0,01, 100 epok, wybór modelu wg walidacji (s. 6, 25). Segmentacja wymaga pełnego douczania (fine-tuning), nie liniowego próbkowania (linear probing) (s. 22).
- 2.3.3 – wyniki segmentacji: przewaga w Jaccardzie o 3,1 i 1,9 nad drugim najlepszym modelem (ISIC2018, HAM10000; P < 0,001); względem MedSAM +0,5; przetwarzanie ok. 4–5 razy szybsze niż MedSAM; bez treningu specjalnie pod segmentację (s. 12). Efektywność etykiet: przy 5% danych treningowych (104 obrazy ISIC2018, 350 HAM10000) dorównuje najlepszemu z pozostałych modeli (s. 12, 37).
- 2.2.1 (marginalnie) – w potoku wykrywania zmian w czasie obrazy dermatoskopowe rejestrowano cechami AKAZE + RANSAC z modelem euklidesowym (obrót + przesunięcie) (s. 23).

**Liczby i fakty do cytowania.**
- Pretrening: 2 149 706 obrazów, 4 modalności, 11 źródeł (s. 17–18); ocena na 28 zbiorach testowych (s. 2).
- Lepszy od SwAVDerm przy o 33% mniejszych danych; najlepszy wynik po 200 epokach wobec 500–800 dla MILAN, DINOv2, MAE (s. 4).
- ISIC2018: 3694 obrazy – 2594 trening, 100 walidacja, 1000 test, oficjalny podział (s. 32). HAM10000: 10 015 obrazów z maskami, losowo 64% / 16% / 20% (s. 32).
- ISIC2018, DSC / JAC: SL-ImageNet 0,876 / 0,807; autoSMIM 0,848 / 0,769; BATFormer 0,884 / 0,815; PanDerm 0,910 / 0,846 (s. 56).
- HAM10000, DSC / JAC: SL-ImageNet 0,927 / 0,875; autoSMIM 0,920 / 0,865; BATFormer 0,937 / 0,891; PanDerm 0,949 / 0,910 (s. 56).
- MedSAM, DSC / JAC: ISIC2018 0,904 / 0,841 (PanDerm lepszy: p = 0,017 i 0,025); HAM10000 0,949 / 0,905 (różnice nieistotne: p = 0,793 i 0,112) (s. 57).
- Trening (A6000): PanDerm 2 h 11 min (ISIC2018) vs MedSAM 8 h 32 min; inferencja 52 s vs 2 min 8 s (s. 57).
- Wyniki segmentacji: średnie z 5 powtórzeń z różnymi ziarnami, 95% CI, dwustronny test t (s. 37).

**Związek z systemem z pracy.** System z pracy powtarza konfigurację z artykułu: koder PanDerm (ViT-L) + dekoder UperNet douczany na ISIC 2018 Task 1 z oficjalnym podziałem (s. 25, 32); uzyskany w pracy Dice 0,899 na zbiorze testowym jest bliski wartości 0,910 podanej przez autorów (s. 56). Obecność 460 328 zdjęć klinicznych w pretreningu (s. 18) uzasadnia użycie modelu na zdjęciach z telefonu, a wyniki przy 5% etykiet (s. 12) – douczanie gotowego kodera zamiast trenowania od zera.

**Uważaj.**
- Segmentację oceniono wyłącznie na obrazach dermatoskopowych (ISIC2018, HAM10000), w rozdzielczości 224 × 224 (s. 25, 32) – artykuł nie podaje wyników segmentacji na zdjęciach klinicznych/z telefonu; Dice 0,87 na zdjęciach z telefonu to wyłącznie wynik pracy.
- „3,1% i 1,9%” oraz „0,5%” to bezwzględne różnice Jaccarda (np. 0,846 − 0,815), czyli punkty procentowe; przewaga nad MedSAM jest istotna statystycznie tylko na ISIC2018 (s. 12, 56–57).
- Niespójności w tekście – cytuj ostrożnie: kafelki dermatopatologii 547 047 (s. 5) vs 537 047 (s. 18; suma 2 149 706 zgadza się z 547 047); „200 epok” w porównaniu metod (s. 4) vs 500 epok finalnego pretreningu (s. 21); na wykresie efektywności etykiet n = 2074 (ISIC2018) i n = 7011 (HAM10000) obrazów treningowych (s. 37) zamiast 2594 / 64% z metod (s. 32); BATFormer cytowany jako [33] (s. 12), a poprawnie [74] (s. 25). Strony dotyczą wersji arXiv v3.

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 5, podpis s. 6): „Overview of this study” – a–c: dane pretreningu wg modalności, źródeł, instytucji; e: architektura (ViT-L, regresor, nauczyciel CLIP); f: skalowanie; g: wyniki na 28 zbiorach; przydatność: wysoka (panele a, e).
- Fig. 2–5 (s. 7, 9, 11, 13): klasyfikacja, wykrywanie zmian i przerzuty, TBP, badanie 128 chorób; przydatność: niska.
- Extended Data Fig. 1 (s. 37): „Quantitative skin lesion segmentation results” – DSC/JAC 4 modeli na ISIC2018 i HAM10000 oraz wyniki w funkcji % danych treningowych; przydatność: wysoka.
- Extended Data Fig. 2 (s. 38): „Qualitative skin lesion segmentation results” – kontury wzorca i predykcji na przykładach z HAM10000; przydatność: średnia.
- Extended Data Fig. 12 (s. 44): „Longitudinal dermoscopic image-based lesion change detection using PanDerm” – potok z rejestracją i segmentacją; przydatność: niska (2.2).
- Extended Data Table 18 i 19 (s. 56): „Lesion segmentation performance of different models on ISIC2018 / HAM10000 dataset”; przydatność: wysoka.
- Extended Data Table 20 i 21 (s. 57): porównanie z MedSAM – jakość oraz czasy treningu/inferencji; przydatność: średnia / niska.

---

### Tschandl, Rosendahl, Kittler, 2018 – The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions
`tschandl2018` · Scientific Data 5:180161, 2018 · DOI: 10.1038/sdata.2018.161 · Podrozdział: 2.3.3 (pomocniczo 2.1)

**Streszczenie.** Autorzy wskazują, że uczenie sieci do automatycznej diagnostyki zmian barwnikowych utrudniają małe i mało zróżnicowane zbiory obrazów dermatoskopowych, zdominowane przez czerniaki i znamiona (s. 1–2). Publikują zbiór HAM10000 („Human Against Machine with 10000 training images”): 10 015 obrazów dermatoskopowych zebranych w ciągu 20 lat w dwóch ośrodkach – Klinice Dermatologii Uniwersytetu Medycznego w Wiedniu i gabinecie C. Rosendahla w Queensland (Australia) (s. 2). Dane pochodziły z różnych nośników (PowerPoint, skanowane diapozytywy, system MoleMax HD), dlatego zastosowano półautomatyczne potoki – m.in. sieć InceptionV3 oddzielającą obrazy dermatoskopowe od zbliżeń i zdjęć poglądowych – oraz ręczną kontrolę jakości (s. 1–4). Diagnozy ujednolicono do 7 klas, obejmujących ponad 95% zmian barwnikowych w codziennej praktyce obu ośrodków (s. 4). Ponad połowę zmian (53,3%) potwierdzono histopatologicznie, pozostałe – obserwacją w czasie, konsensusem ekspertów lub mikroskopią konfokalną in vivo (s. 1, 5–6). Zbiór udostępniono jako zbiór treningowy wyzwania klasyfikacyjnego ISIC 2018 (MICCAI, Granada) oraz przez archiwum ISIC (s. 2, 4).

**Co zawrzeć w pracy.**
- 2.3.3 – opis zbioru: 10 015 obrazów, 2 ośrodki, 20 lat, 7 klas z licznościami (Table 1) (s. 2, 5); licencja CC BY-NC 4.0 (s. 5); dostęp przez archiwum ISIC i Harvard Dataverse (s. 4).
- 2.3.3 – weryfikacja diagnozy (4 typy wzorca, ground truth): histopatologia (ocena dermatopatologów, ręczna kontrola wiarygodności, wykluczenie diagnoz niejednoznacznych); obserwacja (brak zmian w 3 wizytach kontrolnych lub przez 1,5 roku – tylko znamiona); konsensus dwóch autorów (PT, HK) dla typowych zmian łagodnych; mikroskopia konfokalna (część łagodnych keratoz twarzy) (s. 5–6).
- 2.3.3 – związek z ISIC 2018: HAM10000 to zbiór treningowy wyzwania klasyfikacyjnego ISIC 2018, dostępny także dla grup spoza wyzwania (s. 2).
- 2.3.3 – tło: wcześniejsze zbiory – PH2 (200 obrazów: 160 znamion, 40 czerniaków), archiwum ISIC (13 786 obrazów, w tym 12 893 znamiona lub czerniaki) (s. 2, 5).
- 2.1 – dermatoskopia poprawia diagnostykę względem oceny gołym okiem (s. 2); obrazy z różnych dermatoskopów, w świetle spolaryzowanym i niespolaryzowanym (s. 6).
- 2.3.3 – charakter danych: zmiana zwykle (nie zawsze) w centrum, nie usuwano włosów ani zmian „tła” (s. 6); usunięto obrazy nieostre i zbyt słabo powiększone, więc obrazy mogą odbiegać od tych, które dostarczyłby użytkownik końcowy (s. 8).

**Liczby i fakty do cytowania.**
- 10 015 obrazów dermatoskopowych; 53,3% z weryfikacją histopatologiczną (s. 5).
- Klasy (Table 1): akiec 327, bcc 514, bkl 1099, df 115, mel 1113, nv 6705, vasc 142 (s. 5).
- Podzbiory: Rosendahl 2259 (100% histopatologii), ViDIR Legacy 439 (100%), ViDIR Current 3363 (77,1%), ViDIR MoleMax 3954 (1,2%) (s. 5).
- Filtracja: przesiano >30 000 obrazów; InceptionV3 douczony na 1501 ręcznie oznaczonych obrazach, top-1 98,68% (s. 4).
- Obrazy przycięte do 800 × 600 px (72 DPI), zmiana wyśrodkowana (s. 3–4).
- Wykluczono zmiany niebarwnikowe, zmiany oka, podpaznokciowe i błon śluzowych oraz obrazy umożliwiające identyfikację (s. 4).

**Związek z systemem z pracy.** HAM10000 to jeden z dwóch zbiorów, na których autorzy PanDerm oceniali segmentację (yan2025panderm, s. 32), i ilustruje typowe dane dziedziny: kadrowane obrazy dermatoskopowe z wyśrodkowaną zmianą. Kontrastuje to z danymi pracy (zdjęcia telefonem bez dermatoskopu, ze znacznikiem na skórze), co uzasadnia osobną ocenę segmentacji na własnych zdjęciach.

**Uważaj.**
- Artykuł nie opisuje masek segmentacji – HAM10000 przedstawiono jako zbiór do klasyfikacji. Wg mirikharaji2023 (s. 29) maski segmentacji HAM10000 udostępniono dopiero w 2020 r. (Tschandl i in., 2020; ViDIR Dataverse) – nie przypisywać ich temu artykułowi.
- Liczba obrazów ≠ liczba zmian (ta sama zmiana w różnych powiększeniach, kątach, aparatach) (s. 7–8) – przy losowym podziale grozi przeciek danych; PanDerm w klasyfikacji używał „czystej” wersji podziału (yan2025panderm, s. 28).
- „Ponad 50% histopatologii” dotyczy całości – w podzbiorze MoleMax tylko 1,2% (s. 5); zbiór jest silnie niezrównoważony (nv 6705 z 10 015) (s. 5).

**Rysunki i tabele (kandydaci).**
- Table 1 (s. 5): „Summary of publicly available dermatoscopic image datasets in comparison to HAM10000.” – liczby obrazów, licencje, odsetek weryfikacji histopatologicznej i liczności klas dla PH2, Atlas, ISIC 2017 i podzbiorów HAM10000; przydatność: wysoka.
- Figure 1 (s. 3): „Schematic flow of dataset workup methods.” – potok porządkowania danych; przydatność: niska.
- Figure 2 (s. 3), Figure 3 (s. 6): korekta skanu diapozytywu, estymacja barwy oświetlenia; przydatność: niska.
- Figure 4 (s. 7): „Example triplet of the same lesion.” – ta sama zmiana w różnych powiększeniach i kątach; przydatność: niska.

---

### Codella, Rotemberg, Tschandl i in., 2019 – Skin Lesion Analysis Toward Melanoma Detection 2018: A Challenge Hosted by the International Skin Imaging Collaboration (ISIC)
`codella2019` · arXiv:1902.03368v2 [cs.CV], 29.03.2019 (12 s.: artykuł s. 1–8, materiały dodatkowe s. 9–12) · 12 autorów: N. Codella, V. Rotemberg, P. Tschandl, M. E. Celebi, S. Dusza, D. Gutman, B. Helba, A. Kalloo, K. Liopyris, M. Marchetti, H. Kittler, A. Halpern · Podrozdział: 2.3.3, 2.4

> **Plik:** `nowe_artykuły/codella2018.pdf` (mimo nazwy pliku to praca o ISIC **2018**, arXiv 2019 → klucz `codella2019`). Plik `nowe_artykuły/codella2019.pdf` to opis wcześniejszego wyzwania ISIC 2017 – w pracy nieużywany. Proponowana zmiana nazw: `codella2018.pdf` → `codella2019_isic2018.pdf`, `codella2019.pdf` → `codella2018_isic2017.pdf`. Strony PDF = strony w nagłówku artykułu.

**Streszczenie.** Artykuł podsumowuje wyzwanie ISIC 2018 z analizy obrazów dermatoskopowych, zorganizowane na konferencji MICCAI w Granadzie (s. 1). Wyzwanie miało 3 zadania: segmentację zmiany (Part 1), wykrywanie cech dermatoskopowych (Part 2) i klasyfikację chorób (Part 3) (s. 2). Udostępniono ponad 12 500 obrazów uczących i ponad 2000 testowych; zarejestrowało się 900 zespołów, a wszystkich zgłoszeń było 299 (s. 7). Względem poprzednich edycji zmieniono kryteria oceny (s. 2, 7):
- w segmentacji wprowadzono Jaccard progowany (*Thresholded Jaccard*), który zeruje wynik segmentacji poniżej progu T = 0,65;
- w klasyfikacji – zbalansowaną dokładność;
- dodano zewnętrzny zbiór testowy z ośrodków spoza zbioru uczącego.

Najlepsze zgłoszenie w segmentacji uzyskało Jaccard progowany 0,802, ale większość metod nadal źle segmentuje ponad 10% obrazów, najczęściej rogowacenie łojotokowe (s. 4–5). Wniosek autorów: Jaccard progowany lepiej oddaje odsetek porażek niż zwykły Jaccard i zmienia ranking zgłoszeń (s. 5, 7).

**Co zawrzeć w pracy.**
- 2.3.3 – zbiór ISIC 2018 Task 1: 2594 obrazy dermatoskopowe z maskami do uczenia; 100 obrazów walidacyjnych i 1000 testowych, udostępnionych bez masek (s. 2). Na tym zbiorze douczono w pracy dekoder UperNet z koderem PanDerm.
- 2.4 – Jaccard progowany: działa jak zwykły Jaccard, ale gdy wynik dla obrazu spada poniżej progu T, przyjmuje się zero. T wyznacza granicę, od której segmentację uznaje się za „niepoprawną” (s. 3).
- 2.4 – uzasadnienie progu:
  - wcześniejsza praca zmierzyła średni Jaccard między 3 ekspertami na 100 obrazach z wyzwania 2016: 0,743, 0,754 i 0,861, średnio 0,786, rozstęp 0,118 (s. 3);
  - T = 0,65 otrzymano, zaokrąglając najniższą zgodność do 0,75 i odejmując zaokrąglony rozstęp 0,10 (s. 3).
- 2.4 – maski wzorcowe obarczone są zmiennością między- i wewnątrzobserwatorową; idealnie należałoby porównywać predykcję z wieloma maskami od różnych anotatorów, co jest jednak zbyt pracochłonne (s. 2–3). To argument za ostrożną interpretacją Dice względem jednej adnotacji CVAT.
- 2.4 / 2.3.3 – średnia ukrywa porażki: wysoka średnia Jaccarda (powyżej 0,8, więcej niż zgodność ekspertów 0,786) nie wyklucza porażek na ponad 10% obrazów (s. 4–5). Uzasadnia to raportowanie w pracy rozkładów, median i odsetka par z niską zgodnością.
- 2.3.3 – zbiór uczący zadania klasyfikacji to HAM10000 (10 015 obrazów, 7 klas) (s. 4, poz. [11] = `tschandl2018`).

**Liczby i fakty do cytowania.**
- Ponad 12 500 obrazów uczących w 3 zadaniach, ponad 2000 testowych; 900 zespołów; 299 zgłoszeń (s. 7).
- Part 1: 2594 / 100 / 1000 obrazów (s. 2); 112 zgłoszeń (s. 4); najlepszy Jaccard progowany 0,802, wiele zgłoszeń ok. 0,8 (s. 4).
- Table 1 (s. 10) – 5 najlepszych zgłoszeń Part 1:
  - odsetek porażek (F) 0,079–0,093 na całym zbiorze testowym;
  - Jaccard progowany 0,796–0,802, zwykły Jaccard 0,834–0,838;
  - dla rogowacenia łojotokowego F = 0,195–0,310, a dla znamion łagodnych 0,053–0,069.
- Jaccard progowany ma nachylenie zależności od odsetka porażek bliższe 1 niż zwykły Jaccard (Fig. 2A, s. 5).
- Part 3: 10 015 / 193 / 1512 obrazów; zbiór testowy podzielony na część wewnętrzną (1196) i zewnętrzną (316); najlepsza zbalansowana dokładność 0,885 (s. 4, 6).
- Wczesne wykrycie czerniaka: 5-letnie przeżycie do 99%, przy opóźnionej diagnozie 23% (s. 1, za American Cancer Society 2018).

**Związek z systemem z pracy.**
- Na danych ISIC 2018 Task 1 douczono model M1 (PanDerm + UperNet); w pracy Dice testowy 0,899 przy standardowym podziale 2594 / 100 / 1000.
- Próg 0,65 i zgodność ekspertów 0,786 to punkt odniesienia dla wyników na zdjęciach z telefonu. Dice 0,87 odpowiada Jaccardowi ok. 0,77 (przeliczenie własne, J = D/(2 − D)), czyli powyżej progu porażki i blisko zgodności ekspertów.
- Analiza odsetka porażek uzasadnia raportowanie w pracy par z niską zgodnością (np. E2 Dice < 0,9), a nie samych średnich.

**Uważaj.**
- To preprint arXiv (bez recenzji). Cytuj go jako wymagany opis zbioru danych.
- **Niespójności w tekście:**
  - zgłoszenia: w abstrakcie 115 / 25 / 159 (Part 1 / 2 / 3) (s. 1), a w wynikach 112 / 26 / 141 (s. 4–6);
  - podpisy rysunków są zdublowane: dwa razy „Fig. 2” (s. 4 i 5), trzy razy „Fig. 4” (s. 6–7);
  - w tekście o Part 3 jest odwołanie do „Fig. 7”, który pokazuje AUC, a nie BACC.

  Przy liczbie zgłoszeń podawaj wartości z wyników (112) albo pisz „ponad 100”. Przy rysunkach podawaj stronę.
- Zgodność ekspertów 0,786 pochodzi z wcześniejszej pracy i danych z 2016 r., a nie z ISIC 2018 (s. 3).
- Odsetek porażek dotyczy zgłoszeń konkursowych na obrazach dermatoskopowych – nie przenosić go wprost na zdjęcia z telefonu.

**Rysunki i tabele (kandydaci).** Obejrzane na stronach PDF; wycinki w `rysunki_z_artykulow/`.
- Fig. 1 (s. 3): „Example training data and ground truth from Part 1: Lesion Segmentation, Part 2: Attribution Detection, and Part 3: Disease Classification.” – obrazy dermatoskopowe i maski; przydatność: średnia (kontrast ze zdjęciami z telefonu). Plik `R20_codella2019_fig1.png`.
- Fig. 2 (s. 4): „Histograms of submissions for Part 1: Lesion Segmentation…” – rozkłady odsetka porażek, Jaccarda progowanego i Jaccarda; przydatność: średnia. Plik `R21_codella2019_fig2_histogramy.png`.
- Fig. 2 (s. 5, drugi rysunek o tym numerze): „Assessment of new Threshold Jaccard metric. A) Proportion of segmentation failures (X-axis) vs. various metric values (Y-axis). B) Participant ranking by Thresholded Jaccard (X-axis) vs. Jaccard (Y-axis).” – przydatność: średnia (2.4). Plik `R22_codella2019_fig2_tj.png`.
- Table 1 (s. 10): „Top 5 submissions to Part 1: Lesion Segmentation…” – odsetek porażek, Jaccard progowany i Jaccard, w podziale na choroby; przydatność: wysoka (liczby do tekstu albo tabeli). Plik `T08_codella2019_tab1.png`.
- Fig. 3–7, Table 2 (s. 5–12): Part 2 i Part 3 – przydatność: niska.

## 2.4 Miary oceny rejestracji i segmentacji

### Fitzpatrick, West, Maurer, 1998 – Predicting Error in Rigid-Body Point-Based Registration
`fitzpatrick1998` · IEEE Transactions on Medical Imaging, 17(5), 694–702, 1998 · DOI: brak w tekście (PII S 0278-0062(98)09087-9) · Podrozdział: 2.4 (pomocniczo 2.2.2)

**Streszczenie.** Artykuł dotyczy nawigacji chirurgicznej z rejestracją sztywną opartą na punktach wyznaczonych przez znaczniki referencyjne (*fiducial markers*) (s. 1). Zwrotną informacją dla chirurga jest zwykle FRE, a autorzy pokazują, że to wskaźnik zawodny, a nawet mylący (s. 1–2). Z rachunku zaburzeń wyprowadzają przybliżone wyrażenie na oczekiwany kwadrat TRE w funkcji FLE, liczby znaczników N, ich konfiguracji i położenia celu (wzór 31, s. 5). Podają też wyrażenie na oczekiwany kwadrat FRE pojedynczego znacznika (wzór 40, s. 6). Symulacje dla N = 3, 4, 10, 20, 50 (po 10⁶ powtórzeń) potwierdzają predykcje: TRE w granicach 1 odchylenia standardowego, FRE_i w granicach 2 (s. 7–8). Wniosek: FRE nie zależy od konfiguracji znaczników, a TRE jest oczekiwanie najgorsze w pobliżu najlepiej dopasowanych znaczników (s. 1, 8).

**Co zawrzeć w pracy.**
- 2.4: definicje. **FRE** to średniokwadratowa odległość odpowiadających sobie znaczników po rejestracji (wzór 1, s. 2). **FLE** to odległość wyznaczonego punktu od rzeczywistego (nieznanego) położenia znacznika przed rejestracją (s. 3). **TRE(r)** to odległość punktu r od odpowiadającego mu punktu w drugiej przestrzeni po rejestracji; cel to dowolny punkt, np. zmiana do usunięcia (s. 3). Wg abstraktu chodzi o punkty inne niż centroidy znaczników (s. 1).
- 2.4: $\langle FRE^2\rangle=(1-2/N)\langle FLE^2\rangle$ (3D, wzór 10, s. 3). Zależność nie obejmuje konfiguracji znaczników, więc mały FRE może maskować złą konfigurację (s. 1, 3).
- 2.4: wzór na TRE (31, s. 5) i jego postać dla 3D (46, s. 8). Dla ruchu czysto 2D nawias redukuje się do $1+d^2/(2f^2)$ (s. 8).
- 2.4: wnioski jakościowe. TRE jest minimalne w centroidzie konfiguracji i rośnie z odległością od niego. Rośnie, gdy konfiguracja się zmniejsza. Konfiguracja prawie współliniowa daje duże TRE z dala od linii. Izolinie są elipsoidalne (s. 7–8).
- 2.4: zależność $\langle FRE_i^2\rangle=\langle FLE^2\rangle-\langle TRE^2(\hat x_i)\rangle$ (s. 6). Uzasadnia mierzenie TRE na punktach niebiorących udziału w estymacji.
- 2.2.2: dokładność rejestracji opartej na znacznikach zależy od liczby, rozmieszczenia i dokładności lokalizacji znaczników, a nie od obrazowanego obiektu (s. 2).

**Liczby i fakty do cytowania.**
- $FRE^2=\frac1N\sum_{i=1}^N|R x_i+t-y_i|^2$ (s. 2); optymalne przesunięcie $t=\bar y-R\bar x$ (s. 2); obrót z SVD (Schönemann 1966) (s. 3).
- $\langle FLE^2\rangle=K\epsilon^2\sigma^2$ (wzór 9, s. 3). Dla dowolnego wymiaru K: $\sum_i\langle FRE_i^2\rangle=(N-\tfrac12(K+1))\langle FLE^2\rangle$ (wzór 45, s. 7). Podstawienie K = 2 daje $(1-\tfrac{3}{2N})\langle FLE^2\rangle$ – przeliczenie własne, nie ma go w artykule.
- $\langle TRE^2(r)\rangle\approx\langle FLE^2\rangle\left(\frac1N+\frac1K\sum_{i=1}^K\sum_{j\ne i}^K\frac{r_i^2}{\Lambda_{ii}^2+\Lambda_{jj}^2}\right)$ (31, s. 5).
- $\langle TRE^2(r)\rangle\approx\frac{\langle FLE^2\rangle}{N}\left(1+\frac13\sum_{k=1}^3\frac{d_k^2}{f_k^2}\right)$, gdzie $d_k$ to odległość celu od k-tej osi głównej, a $f_k$ to rms odległości znaczników od tej osi (46, s. 8).
- Minimum TRE² w centroidzie wynosi $\langle FLE^2\rangle/N$ (s. 7). Przy skalowaniu konfiguracji o $s$ i dużym $r/s$: $\langle TRE^2\rangle\sim(r/s)^2$ (s. 7). Zależność $N^{-1/2}$ (s. 4, 8).
- Symulacje: znaczniki losowane w sześcianie o boku 200 mm, cel w sześcianie 400 mm; składowe FLE ~ N(0, 1/3 mm²); 1 000 000 powtórzeń × 10 symulacji (s. 7).
- Table I: np. N = 3: 4,7205 ± 0,0040 (symulacja) vs 4,7186 mm² (predykcja); N = 50: 0,0870 ± 0,0001 vs 0,0870 mm² (s. 7).

**Związek z systemem z pracy.** W systemie T pochodzi z ECC na maskach, a 8 narożników z CVAT nie bierze udziału w estymacji. Mierzone TRE jest więc miarą na punktach testowych, a nie FRE, które według autorów jest mylące. Wynik autorów, że błąd jest najmniejszy w centroidzie konfiguracji, jest jakościowo korzystny dla znamienia leżącego między ramionami Π. To jednak analogia, nie wynik przeniesiony wprost.

**Uważaj.**
- Wzory dotyczą sztywnej transformacji (obrót + przesunięcie), estymacji punktowej i FLE izotropowego, i.i.d., obecnego tylko w jednej przestrzeni (s. 3–4). W systemie jest transformacja afiniczna/homografia z ECC, więc wzorów (31)/(46) nie stosować liczbowo.
- TRE autorów liczone jest względem prawdziwych położeń. W pracy TRE liczone jest względem adnotacji CVAT, które same zawierają błąd lokalizacji w obu obrazach.
- TRE zależy od położenia celu (s. 7–8). TRE na narożnikach znacznika ≠ TRE w miejscu znamienia. Kontekst artykułu to 3D i neurochirurgia; wartości w mm z symulacji nie są porównywalne z wynikami pracy.

**Rysunki i tabele (kandydaci).**
- Fig. 1 (s. 6): „Geometrical relationship between εFi, FRE, and TRE” – trójkąt zależności FLE/FRE/TRE; przydatność: wysoka (do 2.4, można przerysować).
- Table I (s. 7): „Mean squared TRE values from simulation versus predicted squared TRE value from (31) (all values in mm²)”; przydatność: niska.
- Table II (s. 8): „Simulated mean squared FRE values versus simulated values of ⟨FLE²⟩ − ⟨TRE²⟩ (all values in mm²)”; przydatność: niska.

---

### Taha, Hanbury, 2015 – Metrics for evaluating 3D medical image segmentation: analysis, selection, and tool
`taha2015` · BMC Medical Imaging, 15:29 (28 s.), 2015 · DOI: 10.1186/s12880-015-0068-x · Podrozdział: 2.4

**Streszczenie.** Autorzy przejrzeli literaturę i wybrali 20 miar oceny segmentacji medycznych obrazów 3D – tylko takie, które miały co najmniej dwa przykłady użycia. Podzielili je na sześć kategorii (s. 3–4). Każdą miarę zdefiniowali w jednolity sposób, także dla segmentacji rozmytej (fuzzy), i pokazali, że w literaturze ta sama nazwa bywa używana dla różnych definicji (s. 3–11). Wszystkie miary zaimplementowali w otwartym narzędziu EvaluateSegmentation (C++/ITK). Na 840 dużych wolumenach VISCERAL narzędzie przeliczyło wszystkie przypadki, a implementacja ITK tylko 17% (s. 14). Autorzy porównali też rankingi 16 miar na 4833 segmentacjach MRI/CT. Miary układają się w silnie skorelowane grupy, a decyduje o tym głównie to, czy miara uwzględnia prawdziwie negatywne piksele (TN) (s. 16). Na podstawie analizy własności miar podają zalecenia ich doboru (s. 19–25, Table 5). Wniosek autorów: żadna pojedyncza miara nie wystarcza. Dobór zależy od danych i celu segmentacji, a miary należy łączyć z różnych kategorii (s. 24, 26).

**Co zawrzeć w pracy.**
- 2.4 – podział miar na 6 kategorii (s. 3; Table 1 s. 4):
  - oparte na pokryciu (overlap),
  - objętościowe (volume),
  - oparte na zliczaniu par (pair-counting),
  - informacyjne (information theoretic: MI, VOI),
  - probabilistyczne (probabilistic),
  - odległościowe (spatial distance).

  Celem podziału jest wybieranie miar z różnych grup, żeby uniknąć obciążonych wyników.
- 2.4 – wzory w notacji artykułu. S_g^1 to klasa obiektu w segmentacji referencyjnej, S_t^1 – w ocenianej (s. 3):
  - DICE = 2|S_g^1 ∩ S_t^1| / (|S_g^1| + |S_t^1|) = 2TP / (2TP + FP + FN) (6) (s. 5)
  - JAC = |S_g^1 ∩ S_t^1| / |S_g^1 ∪ S_t^1| = TP / (TP + FP + FN) (7); JAC = DICE/(2 − DICE) (8); DICE = 2JAC/(1 + JAC) (9) (s. 5)
  - HD(A,B) = max(h(A,B), h(B,A)) (48), gdzie h(A,B) = max_{a∈A} min_{b∈B} ‖a − b‖ (49) (s. 9)
  - AVD(A,B) = max(d(A,B), d(B,A)) (50), gdzie d(A,B) = (1/N) Σ_{a∈A} min_{b∈B} ‖a − b‖ (51) (s. 10)
- 2.4 – DICE i JAC dają ten sam ranking, więc podawanie obu nie wnosi informacji (s. 5). F1 jest równoważna DICE (s. 6).
- 2.4 – HD jest wrażliwa na obiekty odstające (outliers) i nie zaleca się stosowania jej wprost. Metoda kwantylowa Huttenlochera zastępuje maksimum q-tym kwantylem odległości, a q dobiera się do zastosowania. AVD jest stabilniejsza i mniej wrażliwa na outliery (s. 10).
- 2.4 – miary pokrycia nie widzą błędów obrysu. Para gwiazda–koło i para gwiazda–obrócona gwiazda dają te same FP i FN, więc te same wartości miar pokrycia; HD i AVD odróżniają te przypadki (s. 19–20, Fig. 6). Gdy liczy się kontur, zaleca się miary odległościowe (s. 24).
- 2.4 – małe obiekty. Gdy oczekiwany błąd położenia jest porównywalny z rozmiarem obiektu, miary pokrycia i objętościowe przy zerowym pokryciu dają tę samą wartość niezależnie od tego, jak daleko są segmenty. Obiekt uznaje się za mały, gdy jego najmniejszy wymiar jest wyraźnie mniejszy od wymiaru siatki (np. < 5%). Dotyczy to także obiektów cienkich w jednym wymiarze. Zalecane są wtedy miary odległościowe (s. 19, 22).
- 2.4 – miary uwzględniające TN (TNR, RI, GCE) zależą od niezrównoważenia klas: nagradzają małe segmenty, a karzą duże (s. 16, 24). TPR i TNR karzą błędy w małych segmentach mocniej niż w dużych (s. 5).

**Liczby i fakty do cytowania.**
- Miary wybrano według kryterium: co najmniej 2 źródła użycia w ocenie segmentacji medycznej (s. 3). DICE to według autorów najczęściej używana miara (s. 5).
- Korelacja rankingów (4833 segmentacje, 20 struktur anatomicznych) (s. 16):
  - grupa bez TN: ARI, KAP, ICC, DICE, AVD, MHD, PBD, VS;
  - grupa z TN: TNR, RI, GCE, VOI;
  - korelacja pośrednia: MI, AUC, TPR, HD.
- Korelacja DICE z miarami odległościowymi maleje wraz ze spadkiem pokrycia (s. 17, Fig. 5).
- VS może osiągnąć maksimum (1) przy zerowym pokryciu (s. 7, 18).
- Odległości są liczone w wokselach, bez uwzględnienia rozmiaru woksela (s. 9).
- Table 5 (s. 25):
  - „Small segment”: DICE i JAC niezalecane, HD, AVD i MHD zalecane;
  - „Outliers exist”: HD niezalecana, AVD zalecana;
  - „Contour is important”: HD i AVD zalecane, VS niezalecana.
- Wydajność: na BRATS2012 HD liczona 2,4× szybciej niż w ITK (średnio 1,3 s), AVD 3,0× szybciej (2,5 s); wszystkie 20 miar razem średnio 43,2 s na wolumen VISCERAL (s. 14).

**Związek z systemem z pracy.** System łączy miarę pokrycia (Dice), miary odległościowe (HD95, ASSD) i miarę objętościową (stosunek pól). Zgadza się to z zaleceniem, by łączyć miary z różnych grup i unikać miar silnie skorelowanych (s. 3, 24). Ramiona znacznika Π (pasek 9 mm) są cienkie w jednym wymiarze, a dla takich obiektów samo Dice nie wystarcza, co uzasadnia dodanie miar odległościowych (s. 19). Przesunięcie środków odpowiada aspektowi położenia (alignment), który przy bardzo małych obiektach bywa ważniejszy od rozmiaru i konturu (s. 2). Autorzy uznają jednoczesne podawanie Dice i IoU za redundantne (s. 5) – warto to zaznaczyć w pracy.

**Uważaj.**
- Artykuł dotyczy wolumenów 3D MRI/CT, a nie zdjęć skóry 2D. Odległości podano w wokselach, nie w mm (s. 9).
- AVD to nie to samo co ASSD. AVD jest maksimum z dwóch skierowanych średnich (s. 10). Taha nie definiuje też „HD95” – podaje tylko ogólny q-ty kwantyl (s. 10) i przykład HD@0.9 (s. 13).
- Zdanie z s. 5, że JAC jest zawsze większy od DICE, przeczy wzorowi (8), z którego wynika JAC ≤ DICE – nie cytować go. Próg 5% to przykład („e.g.”), a nie ścisła granica (s. 19).

**Rysunki i tabele (kandydaci).**
- Table 1 (s. 4): „Overview of the metrics implemented in this tool” – 20 miar z kategoriami 1–6; przydatność: wysoka (można zawęzić do miar systemu).
- Table 5 (s. 25): „Summary of metric selection guidelines” – macierz: własności danych i wymagania × miary (✓/X); przydatność: wysoka.
- Fig. 6 (s. 20): „Metrics that fail to discover boundary errors” – gwiazda vs koło i vs obrócona gwiazda; przydatność: wysoka.
- Table 4 (s. 23): „Assignment of properties to metrics”; przydatność: średnia.
- Fig. 3 (s. 17): „The correlation between the rankings produced by 16 different metrics”; przydatność: średnia.
- Fig. 5 (s. 18), Fig. 7 (s. 20), Fig. 8 (s. 21), Fig. 1 (s. 13), Fig. 2 (s. 15): przydatność: niska.

---

### Maier-Hein, Reinke, Godau i in., 2024 – Metrics Reloaded: Recommendations for image analysis validation
`maierhein2024` · preprint arXiv:2206.01653v8 [cs.CV], 23.02.2024 (w tekście brak danych czasopisma) · DOI: brak w tekście · Podrozdział: 2.4

**Streszczenie.** Według autorów źle dobrane miary walidacyjne to niedoceniany problem w analizie obrazów biomedycznych. Wyróżniają trzy źródła błędów: zły wybór kategorii problemu, zły dobór miary i złe jej zastosowanie, np. przy agregacji (s. 5–6). Metrics Reloaded to ramy (framework) doboru miar. Opracowało je konsorcjum 73 ekspertów w wieloetapowym procesie delfickim (Delphi) w latach 2020–2022, a łącznie wkład wniosło 156 osób (s. 10–11). Podstawą jest „odcisk problemu” (problem fingerprint), czyli ustrukturyzowany opis cech problemu istotnych dla wyboru miar (s. 7, 12). Ramy obejmują cztery kategorie problemów, a miary wybiera się według drzew decyzyjnych S1–S9 (s. 7, 13). Wszystkie elementy osiągnęły próg konsensusu > 75%, a mediana zgodności wyniosła 93% (s. 14, 22). Dla segmentacji semantycznej zalecana jest miara pokrycia (DSC lub IoU) uzupełniona miarą brzegową (s. 15–16).

**Co zawrzeć w pracy.**
- 2.4 – idea odcisku problemu (s. 12; Fig. 3 s. 9). Rodziny cech:
  - FP1 – kategoria problemu;
  - FP2 – co jest ważne w danym zastosowaniu (brzeg, objętość, środek);
  - FP3 – struktura docelowa (rozmiar, zmienność rozmiaru, kształt);
  - FP4 – zbiór danych (niezrównoważenie klas, niepewność adnotacji, hierarchia danych);
  - FP5 – wyjście algorytmu.

  Fig. 3 zaznacza, że miary pokrycia nie mierzą zgodności kształtu, więc przy złożonym kształcie warto uznać brzeg za ważny (s. 9).
- 2.4 – cztery kategorie: klasyfikacja obrazu, detekcja obiektów, segmentacja semantyczna i segmentacja instancji. Wszystkie traktowane są jako klasyfikacja w różnych skalach: obrazu, obiektu i piksela (s. 7, 10–11, Fig. 4).
- 2.4 – ścieżka dla segmentacji semantycznej:
  1. Miara pokrycia – domyślnie DSC lub IoU. Wyjątek: struktury są stale małe względem siatki i referencja może być zaszumiona (s. 15; ED Fig. 6 s. 42).
  2. Miara brzegowa jako uzupełnienie – miary pokrycia nie widzą kształtu i słabo radzą sobie z małymi strukturami oraz dużą zmiennością rozmiarów (s. 16).
- 2.4 – wybór miary brzegowej, podproces S7 (s. 43, 83):
  - trzeba skompensować niedokładność adnotacji → NSD;
  - błąd karany za samo wystąpienie → NSD albo Boundary IoU;
  - błąd karany według odległości, z naciskiem na outliery → HD albo X-ty percentyl HD;
  - błąd karany według odległości, z naciskiem na cały kontur → ASSD albo MASD (domyślnie MASD).
- 2.4 – HD95: d95(A,B) = 95. percentyl z min_{b∈B} d(a,b) po a∈A; HD95(A,B) = max{d95(A,B), d95(B,A)} (s. 169). Stosuje się ją zamiast HD, gdy outliery przestrzenne mają być pomijane (s. 131).
- 2.4 – DSC to F1 na poziomie pikseli, a DSC = 2IoU/(1 + IoU). Obie miary zwykle dają ten sam ranking, więc łączenie ich nie ma wartości. DSC jest preferowane w medycynie, IoU w computer vision (s. 15, 128).
- 2.4 – zastosowanie miar:
  - miary liczy się osobno dla każdego obrazu i dopiero potem agreguje (s. 15);
  - agregacja musi respektować hierarchię danych (s. 46);
  - wartościom NaN przypisuje się najgorszą możliwą wartość; dla HD może to być np. przekątna obrazu (s. 84).

**Liczby i fakty do cytowania.**
- Proces Delphi: 5 międzynarodowych warsztatów i 9 ankiet (s. 10), łącznie ok. 2,5 roku (s. 21). Niezgoda od 0% do 7%; S1, S7 i S8 przyjęto jednogłośnie (s. 14, 22).
- Fig. 1a (s. 6), przykład poglądowy: przy małej strukturze różnica pojedynczych pikseli obniża DSC z 0,80 do 0,50.
- ED Fig. SN 2.23 (s. 132): jeden błędny piksel w referencji daje DSC 0,95, IoU 0,90, HD 11,31, HD95 6,79, ASSD 0,67, MASD 0,63, NSD 0,88. HD reaguje najsilniej.
- ED Fig. SN 2.5 (s. 84): pominięcie NaN daje średni DSC 0,90, a ustawienie NaN na 0 daje 0,60.
- Przykłady segmentacji dużych obiektów (zarodek, wątroba): zalecane DSC + NSD (Fig. 5, s. 20). Modalność nie ma znaczenia, liczy się pojedynczy, duży względem siatki obiekt (s. 19).
- Raportowanie: przy dużej zmienności między oceniającymi „więcej niż jedno miejsce po przecinku często nie jest użyteczne” (ED Tab. 1, s. 46).
- Ściągawki miar (cheat sheets):
  - HD95 nie stosować, gdy trzeba kompensować zmienność między oceniającymi (s. 169);
  - ASSD nie stosować, gdy rozmiary referencji i predykcji mocno się różnią (s. 164);
  - ASSD = [Σ_{a∈A} d(a,B) + Σ_{b∈B} d(b,A)] / (|A| + |B|), liczone po pikselach brzegu (s. 164).

**Związek z systemem z pracy.** Segmentacja znamienia i znacznika to segmentacja semantyczna jednego obiektu, więc zestaw Dice + HD95/ASSD odpowiada zaleceniu „miara pokrycia + miara brzegowa” (s. 15–16, S7 s. 43). Miary liczone osobno dla każdej pary, mediany i walidacja krzyżowa po znamionach (94 pary, 34 znamiona) są zgodne z zaleceniem respektowania hierarchii danych (s. 15, 46). Ramy nie obejmują rejestracji ani TRE – dotyczą problemów klasyfikacyjnych (s. 7, 24), więc do TRE potrzebne jest inne źródło.

**Uważaj.**
- Zalecenia to konsensus ekspertów, a nie wynik eksperymentu. Autorzy przyznają, że brakuje wzorca „najlepszej miary” (s. 22).
- Ramy domyślnie polecają MASD zamiast ASSD oraz NSD przy niepewnej adnotacji (s. 83). Wybór ASSD i HD95 w systemie warto więc uzasadnić, np. interpretacją w mm. Ściągawka DSC odradza DSC przy dużej zmienności rozmiarów struktur (s. 147).
- Numery stron odnoszą się do PDF arXiv v8 (210 s.: tekst główny s. 4–24, suplement od s. 47). Referencja rozmyta jest poza zakresem (s. 21).

**Rysunki i tabele (kandydaci).**
- Extended Data Fig. 7 (s. 43): „Subprocess S7 for selecting a boundary-based segmentation metric (if any)” – drzewo NSD / Boundary IoU / ASSD, MASD / HD, HD95; przydatność: wysoka.
- Extended Data Fig. SN 2.23 (s. 132): „Effect of annotation errors/noise” – siedem miar przy jednym błędnym pikselu; przydatność: wysoka.
- Fig. 3 (s. 9): „Relevant properties of a driving biomedical image analysis problem are captured by the problem fingerprint”; przydatność: średnia–wysoka.
- Fig. 1 (s. 6): „Contributions of the Metrics Reloaded framework” – trzy typy pułapek; przydatność: średnia.
- Extended Data Fig. 6 (s. 42): „Subprocess S6 for selecting overlap-based segmentation metrics (if any)”; Fig. 5 (s. 20): „Instantiation of the framework…”; Table 1 (s. 17–18): „Metrics Reloaded addresses common and rare pitfalls in metric selection”; przydatność: średnia.
- Fig. 2 (s. 8), Fig. 4 (s. 10), Extended Data Tab. 1 (s. 46): przydatność: niska.
