# Rysunki, tabele i dane z artykułów do rozdziału 2 (pkt 4)

Stan: 26.10.2026.

**Sposób weryfikacji – każda pozycja poniżej:**
1. jest w artykule z grupy A albo w Twoim (★);
2. ma numer i podpis sprawdzone w tekście PDF;
3. została obejrzana na wyrenderowanej stronie PDF;
4. ma wycięty podgląd w folderze `praca/materialy/rysunki_z_artykulow/` (nazwa pliku w kolumnie „Plik”).

Nic tu nie jest wygenerowane: rysunki i tabele są wycięte z PDF-ów 1:1, a liczby w sekcji „Dane” pochodzą z kart w `03_streszczenia_artykulow.md` (ze stronami).

**Strony.** „PDF s.” = numer strony w pliku (do szukania), „druk.” = strona drukowana (do `\cite[s.~…]{…}`). PanDerm i Metrics Reloaded to wersje arXiv – w czasopiśmie numery rysunków dodatkowych i stron mogą być inne.

**Budżet.** Rozdział 2 ma ≤ 8 stron, więc realnie zmieszczą się **4–6 rysunków i 2–3 tabele**. Na końcu jest „pakiet minimalny”. Reszta to rezerwa do wyboru.

---

## 1. Rysunki

Priorytet: ★★★ – zalecany, ★★ – dobry, ★ – tylko gdy zostanie miejsce.

### 2.1 Obrazowanie zmian skórnych

| ID | Źródło | Oryginalny podpis (skrót) | Co pokazuje / po co | Priorytet | Plik |
|---|---|---|---|---|---|
| R01 | `visualization-detection-cancer`, Figure 1, PDF s. 2 (druk. 2 z 4) | „a) The infrared imaging system HRIS…, b) photograph… with a cluster of pigmented lesions and the template frame applied for imaging, c) reference infrared image…, d) the same area after cooling, e) magnified section of the melanoma lesion” | Stanowisko, **znacznik (ramka) naklejony na skórę**, obraz IR w spoczynku i po schłodzeniu. Jeden rysunek ilustruje termografię dynamiczną (2.1) i znacznik referencyjny (2.2.2). | ★★★ | `R01_herman2011_fig1.png` |
| R02 | `infared-thermal-imaging`, Figure 1, PDF s. 3 (druk. R34) | „(Left) Thermogram of lateral face recorded in 1995 with 320 × 240 pixels; (right) thermogram recorded in 2011 with a new 640 × 480 pixel infrared camera.” | Wpływ rozdzielczości kamery na termogram. Twoja kamera ma 320 × 240 px, więc rysunek uzasadnia ograniczenie rozdzielczości. | ★ | `R02_ring2012_fig1.png` |

### 2.2.1 Modele transformacji i miary podobieństwa

| ID | Źródło | Oryginalny podpis (skrót) | Co pokazuje / po co | Priorytet | Plik |
|---|---|---|---|---|---|
| R03 | `zitova2003`, Fig. 1, PDF s. 3 (druk. 979) | „Four steps of image registration: top row – feature detection…; middle row – feature matching by invariant descriptors…; bottom left – transform model estimation…; bottom right – image resampling and transformation…” | Cztery etapy rejestracji na jednym przykładzie. Dobra ilustracja definicji rejestracji. | ★★★ | `R03_zitova2003_fig1.png` |
| R04 | `zitova2003`, Fig. 5, PDF s. 14 (druk. 990) | „Examples of various mapping functions: similarity transform (top left), affine transform (top right), perspective projection (bottom left), and elastic transform (bottom right).” | Modele transformacji: podobieństwo, afiniczna, perspektywiczna (homografia) i elastyczna. Dwa z nich są w systemie (afiniczna, homografia). | ★★ | `R04_zitova2003_fig5.png` |
| R05 | `deep-learning-in-registration`, Figure 1, PDF s. 3 (druk. 2) | „A flowchart of medical image registration framework.” | Pętla: model transformacji → obraz przekształcony → miara podobieństwa → optymalizacja. Alternatywa dla R03 – prostsza; wybierz jedną z nich. | ★★ | `R05_chen2021_fig1.png` |
| R06 | `correlation-ratio`, Fig. 2, PDF s. 3 (druk. 1117) | „'Grey stripe' registration experiment. Left, plot of mutual information I(A, B_T) vs. horizontal translation. Right, the correlation ratio…” | Wiele maksimów informacji wzajemnej vs jedno maksimum stosunku korelacyjnego. Tylko jeśli szerzej opisujesz miary statystyczne (E4). Skan – jakość średnia. | ★ | `R06_roche1998_fig2.png` |

### 2.2.2 Rejestracja RGB–termowizja i znaczniki referencyjne

| ID | Źródło | Oryginalny podpis (skrót) | Co pokazuje / po co | Priorytet | Plik |
|---|---|---|---|---|---|
| R07 | `oniga2026`, Figure 3, PDF s. 4 | „Acquired image triplet: VIS image (left), NIR image (middle), and TH image (right).” | **Kwadratowy znacznik na skórze widoczny w VIS, NIR i termowizji.** Najbliższy odpowiednik Twojego znacznika Π (do porównania kształtu). | ★★★ | `R07_oniga2026_fig3.png` |
| R08 | `visible-and-infared`, Fig. 1, PDF s. 3 (druk. 44) | „Image statistics that imply problems for IR and ViS image registration. (a) Interest point detection for IR and ViS images. Two different methods: SURF and Harris corner detection are used. (b) … distributions of Intensity, Gradient Magnitudes and Gradient Orientations” | Panel (a): punkty SURF / Harris w IR i ViS się nie pokrywają. Argument przeciw dopasowaniu punktów charakterystycznych, a za znacznikiem. Wystarczy panel (a). | ★★★ | `R08_han2013_fig1.png` |
| R09 | `non-contact-breathing-monitoring`, Fig. 1, PDF s. 4 (druk. 1110) | „The overview of the proposed method.” | Rama kalibracyjna, rejestracja RGB–termowizja, ROI z RGB przenoszony na termogram. Ta sama zasada co w Twoim systemie: „wykrywaj w RGB, mierz w TH”. | ★★ | `R09_maurya2021_fig1.png` |
| R10 | `gonzalezperez2021`, Figure 1, PDF s. 4 (druk. 4 z 16) | „Custom built checkerboard keypoint detection and matching. (Left) Thermal image… (Right) RGB image… Notice the black aluminum plate behind the checkerboard in the RGB image and its corresponding cold contrast signature in the thermal image.” | Wzorzec z aluminium widoczny w obu widmach. Analogia do folii aluminiowej w znaczniku Π. | ★★ | `R10_gonzalezperez2021_fig1.png` |

### 2.2.3 Metody głębokie i 2.2.4 Fuzja

| ID | Źródło | Oryginalny podpis (skrót) | Co pokazuje / po co | Priorytet | Plik |
|---|---|---|---|---|---|
| R11 | `neural-networks`, Fig. 2, PDF s. 3 (druk. 3) | „The upper part illustrates the training strategy of the proposed weakly-supervised registration framework…, where the dashed lines indicate data flows only required in training. The lower part depicts the resulting inference…” | Etykiety potrzebne tylko w treningu, a we wnioskowaniu wystarczy para obrazów. Ilustracja metod głębokich – tylko gdy 2.2.3 ma więcej niż akapit. | ★ | `R11_hu2018_fig2.png` |
| R12 | `deep-learning`, Fig. 1, PDF s. 1 (druk. 10535) | „The benefit of visible and infrared image fusion. The first row shows visible images while the second row shows corresponding infrared images. The third row illustrates the fusion results using the MGFF method…” | Komplementarność obrazu widzialnego i podczerwonego. Sceny niemedyczne, więc tylko jako ilustracja pojęcia fuzji. | ★ | `R12_zhang2023_fig1.png` |

### 2.3 Segmentacja

| ID | Źródło | Oryginalny podpis (skrót) | Co pokazuje / po co | Priorytet | Plik |
|---|---|---|---|---|---|
| R13 | `ronneberger2015`, Fig. 1, PDF s. 2 (druk. 235) | „U-net architecture (example for 32x32 pixels in the lowest resolution). Each blue box corresponds to a multi-channel feature map…” | Klasyczny schemat U-Net: koder, dekoder, połączenia skrótowe. Podstawa modelu M3. Twój U-Net (16–256 kanałów, 4 poziomy) narysujesz w rozdz. 5 jako rysunek własny. | ★★★ | `R13_ronneberger2015_fig1.png` |
| R14 | `xiao2018upernet`, Fig. 4, PDF s. 7 (druk. 438) | „UPerNet framework for Unified Perceptual Parsing. Top-left: The Feature Pyramid Network (FPN) with a Pyramid Pooling Module (PPM) appended on the last layer of the back-bone network…” | Dekoder UperNet (FPN + PPM) używany z PanDerm. Zawiera głowy zadań, których nie używasz – rysunek do rozważenia. | ★★ | `R14_xiao2018upernet_fig4.png` |
| R15 | `yan2025panderm`, Figure 1, PDF s. 5 (arXiv; podpis na s. 6) | „Overview of this study.” | Panel a – skład danych pretreningu (4 modalności), panel e – architektura (koder ViT-L, nauczyciel CLIP). Cały rysunek jest za gęsty; w pracy użyj panelu a lub e. | ★★ | `R15_yan2025panderm_fig1.png` |
| R16 | `mirikharaji2023`, Fig. 10, PDF s. 30 | „Number of skin lesion images with ground-truth segmentation maps per year categorized based on modality… while the number of dermoscopic skin lesion images has been constantly on the rise, the number of clinical images has remained unchanged for the past several years.” | Mało zdjęć klinicznych z maskami (dominuje dermoskopia). Uzasadnia przesunięcie dziedziny i własny zbiór (2.3.3 / 2.5). | ★★ | `R16_mirikharaji2023_fig10.png` |
| R20 | `codella2019`, Fig. 1, PDF s. 3 (plik `codella2018.pdf`) | „Example training data and ground truth from Part 1: Lesion Segmentation, Part 2: Attribution Detection, and Part 3: Disease Classification.” | Obrazy dermatoskopowe ISIC 2018 z maskami zmian (Part 1). Kontrast ze zdjęciami z telefonu: zmiana duża i wyśrodkowana, bez znacznika. W pracy wystarczy wycinek „Part 1”. | ★ | `R20_codella2019_fig1.png` |

### 2.4 Miary oceny

| ID | Źródło | Oryginalny podpis (skrót) | Co pokazuje / po co | Priorytet | Plik |
|---|---|---|---|---|---|
| R17 | `fitzpatrick1998`, Fig. 1, PDF s. 6 (druk. 699) | „Geometrical relationship between εFi, FRE, and TRE.” | Zależność FLE, FRE i TRE na jednym schemacie. Podstawa badania E1. Prosty rysunek – można przerysować z adnotacją „Opracowano na podstawie”. | ★★★ | `R17_fitzpatrick1998_fig1.png` |
| R18 | `taha2015`, Fig. 6, PDF s. 20 | „Metrics that fail to discover boundary errors. In a, the star is compared with a circle and in b the same star is compared with another star of the same dimensions, rotated…” | Te same FP/FN, czyli ten sam Dice, a zupełnie inny kształt. Dlaczego obok Dice potrzebne są HD95 / ASSD. | ★★★ | `R18_taha2015_fig6.png` |
| R19 | `maierhein2024`, Extended Data Fig. SN 2.23, PDF s. 132 (arXiv) | „Effect of annotation errors/noise. A single erroneously annotated pixel may lead to a large decrease in performance, especially in the case of the Hausdorff Distance (HD)… HD95… was designed to deal with spatial outliers.” | Jeden błędny piksel: DSC 0,95, ale HD = 11,31 i HD95 = 6,79. Dlaczego w pracy HD95, a nie HD. Alternatywa dla R18 albo uzupełnienie. | ★★★ | `R19_maierhein2024_edfig_sn2_23.png` |
| R21 | `codella2019`, Fig. 2, PDF s. 4 | „Histograms of submissions for Part 1: Lesion Segmentation. Performance on the X-axis, and number of submissions on the Y-axis…” | Rozkłady odsetka porażek, Jaccarda progowanego i Jaccarda dla zgłoszeń ISIC 2018. Pokazuje, że wysoka średnia nie wyklucza porażek. | ★★ | `R21_codella2019_fig2_histogramy.png` |
| R22 | `codella2019`, Fig. 2 (drugi o tym numerze), PDF s. 5 | „Assessment of new Threshold Jaccard metric. A) Proportion of segmentation failures (X-axis) vs. various metric values (Y-axis). B) Participant ranking by Thresholded Jaccard (X-axis) vs. Jaccard (Y-axis).” | Jaccard progowany lepiej oddaje odsetek porażek i zmienia ranking. Tylko jeśli opisujesz miarę progowaną szerzej. W pracy podaj stronę, bo numer rysunku jest zdublowany. | ★ | `R22_codella2019_fig2_tj.png` |

**Sprawdzone, ale bez wycinka (nieprzydatne lub nieczytelne):**
- `magalhaes2019` Figure 1 (PDF s. 2, „Stages involved in the acquisition protocol”) – bardzo mały, nieczytelny;
- `maierhein2024` Extended Data Fig. 7 (PDF s. 43, drzewo wyboru miary brzegowej) – za drobny tekst; lepiej opisać słowami.

---

## 2. Tabele (do wstawienia jako obraz albo przepisania)

| ID | Źródło | Oryginalny tytuł | Jak użyć | Priorytet | Plik |
|---|---|---|---|---|---|
| T01 | `evangelidis2008`, TABLE 1, PDF s. 4 (druk. 1861) | „Outline of the Proposed Forward Additive ECC (FA-ECC) Refinement Algorithm” | Kroki S1–S4 algorytmu ECC. Lepiej pasuje do rozdz. 5 (implementacja rejestracji) jako pseudokod z cytatem. | ★★ | `T01_evangelidis2008_tab1.png` |
| T02 | `mirikharaji2023`, Table 1, PDF s. 5 | „Public skin lesion datasets with lesion segmentation annotations.” | Publiczne zbiory z maskami (DermQuest, DermoFit, PH², ISIC 2016/2017/2018, HAM10000). Lepiej przepisać skrócone 3–4 wiersze (zob. D3). **Uwaga:** wiersz HAM10000 ma odwrócone klasy („1113 non-melanomas, 8902 melanomas”); według `tschandl2018` (T03) to 1113 czerniaków. | ★★★ | `T02_mirikharaji2023_tab1.png` |
| T03 | `tschandl2018`, Table 1, PDF s. 5 | „Summary of publicly available dermatoscopic image datasets in comparison to HAM10000.” | Liczności, licencje, odsetek weryfikacji histopatologicznej i klasy. Rezerwa – w pracy wystarczą 2–3 liczby w tekście. | ★ | `T03_tschandl2018_tab1.png` |
| T04 | `yan2025panderm`, Extended Data Table 18, PDF s. 56 (arXiv) | „Lesion segmentation performance of different models on ISIC2018 dataset.” | DSC i JAC (z 95% CI) dla SL-ImageNet, autoSMIM, BATFormer i PanDerm. Punkt odniesienia dla Twojego Dice 0,899. Przepisz razem z T05 (zob. D2). | ★★★ | `T04_yan2025panderm_edtab18.png` |
| T05 | `yan2025panderm`, Extended Data Table 19, PDF s. 56 (arXiv) | „Lesion segmentation performance of different models on HAM10000 dataset.” | Jak T04, zbiór HAM10000. | ★★ | `T05_yan2025panderm_edtab19.png` |
| T06 | `taha2015`, Table 1, PDF s. 4 | „Overview of the metrics implemented in this tool” | 20 miar z kategoriami 1–6. W pracy wystarczy wyciąg miar systemu (zob. D4). | ★★ | `T06_taha2015_tab1.png` |
| T07 | `taha2015`, Table 5, PDF s. 25 (strona obrócona) | „Summary of metric selection guidelines” | Zalecenia doboru miar. Dla „Small segment” Dice/JAC niezalecane, a HD/AVD zalecane; dla „Outliers exist” HD niezalecana. Uzasadnienie zestawu Dice + HD95 + ASSD. Do przepisania jako wycinek 3–4 wierszy. | ★★★ | `T07_taha2015_tab5.png` |
| T08 | `codella2019`, Table 1, PDF s. 10 | „Top 5 submissions to Part 1: Lesion Segmentation…” | Odsetek porażek (F) 0,079–0,093, Jaccard progowany 0,796–0,802, Jaccard 0,834–0,838; osobno dla czerniaków, rogowacenia łojotokowego (F do 0,310) i znamion. Lepiej podać 2–3 liczby w tekście 2.3.3/2.4 niż wstawiać tabelę. | ★★ | `T08_codella2019_tab1.png` |

---

## 3. Dane do własnych tabel (zestawienia liczb z artykułów)

To nie są tabele z artykułów, tylko **zestawienia liczb z artykułów**. W podpisie: „Opracowanie własne na podstawie \cite{…}”. Każda liczba ma stronę w karcie artykułu w `03_streszczenia_artykulow.md`.

### D1 (2.5) – Prace rejestrujące obraz widzialny z termowizyjnym

| Praca | Zastosowanie | Kamery (IR / widzialna) | Źródło korespondencji | Model transformacji | Ocena rejestracji |
|---|---|---|---|---|---|
| Herman i Pirtini Cetingul 2011 | termografia dynamiczna zmian barwnikowych | Merlin MWIR 3–5 µm / Canon PowerShot G11 | narożniki kwadratowego znacznika na skórze | kwadratowy model ruchu (sekwencja IR) | brak miar ilościowych |
| Han i in. 2013 | sceny zurbanizowane | LWIR 384 × 288 / 656 × 490 | linie z krawędzi + punkty Harrisa | perspektywiczny + lokalne afiniczne | błąd w px, np. „Home” 1,78 → 0,76 px |
| Maurya i in. 2021 | pomiar częstości oddechu | FLIR E-60 320 × 240 / Logitech C922 960 × 720 | rama kalibracyjna + cechy zgodności fazy | „linear mapping” (typ niepodany) | TRE 1,817 px (50 par) |
| González-Pérez i in. 2021 | stopa cukrzycowa | Thermal Expert TE-Q1 Plus 384 × 288 / RealSense D415 1280 × 720 (sztywno złączone) | szachownica z aluminium / maski stóp | translacja, homografia, ICP, afiniczna | Dice / Jaccard masek, np. Jaccard 0,938–0,965 przy 800 mm |
| Oniga i in. 2026 | zmiany skórne (VIS, NIR, TH) | Optris PI450i 382 × 288 i PI640i 640 × 480 / VIS 1920 × 1080 | kwadratowy znacznik (YOLOv8n) + punkty z sieci ResU-Net | homografia (RANSAC) | SSIM / MI / NMI, np. TH SSIM 0,395 ± 0,180 |
| **Niniejsza praca** | zmiany skórne | 320 × 240 / zdjęcie z telefonu | kształt znacznika Π (maski w obu modalnościach) | afiniczna / homografia (ECC) | TRE w mm (E1: mediana 0,61 mm), Dice masek między modalnościami (E2) |

Uwagi:
- Miary są różne (px, Dice, SSIM, mm) – w tekście zaznacz, że wartości nie są bezpośrednio porównywalne.
- Dla Hermana „brak miar ilościowych” wynika z karty `visualization-detection-cancer` (w „Uważaj”: artykuł nie podaje liczb o dokładności rejestracji ani diagnozy).

### D2 (2.3.3) – Segmentacja zmian skórnych: PanDerm i modele porównawcze

Źródło: `yan2025panderm`, Extended Data Tables 18–19 (PDF s. 56).

| Model | ISIC 2018 DSC | ISIC 2018 JAC | HAM10000 DSC | HAM10000 JAC |
|---|---|---|---|---|
| SL-ImageNet | 0,876 | 0,807 | 0,927 | 0,875 |
| autoSMIM | 0,848 | 0,769 | 0,920 | 0,865 |
| BATFormer | 0,884 | 0,815 | 0,937 | 0,891 |
| PanDerm | **0,910** | **0,846** | **0,949** | **0,910** |

Dopisek w tekście: model douczony w pracy osiągnął na zbiorze testowym ISIC 2018 Dice 0,899 (wynik własny, nie z artykułu – oznacz to).

### D3 (2.3.3) – Publiczne zbiory z maskami segmentacji (wyciąg)

Źródło: `mirikharaji2023`, Table 1 (PDF s. 5) + `tschandl2018` (PDF s. 5); podział ISIC 2018 potwierdza `codella2019` (s. 2).

| Zbiór | Rok | Modalność | Liczba obrazów | Podział (trening / walidacja / test) |
|---|---|---|---|---|
| PH² | 2013 | dermoskopia | 200 | – |
| ISIC 2016 | 2016 | dermoskopia | 1279 | 900 / – / 379 |
| ISIC 2017 | 2017 | dermoskopia | 2750 | 2000 / 150 / 600 |
| ISIC 2018 | 2018 | dermoskopia | 3694 | 2594 / 100 / 1000 |
| HAM10000 | 2020 (maski) | dermoskopia | 10 015 | – (obrazy 600 × 450 px) |

- DermoFit (2013, kliniczne, 1300) – tylko jako przykład zbioru klinicznego z maskami.
- Nie przepisuj kolumny „Class distribution” dla HAM10000 z Mirikharaji (błąd – zob. T02).

### D4 (2.4) – Miary użyte w systemie a literatura

| Miara w systemie | Kategoria wg `taha2015` (Table 1, s. 4) | Zalecenia | Uwagi |
|---|---|---|---|
| Dice (DSC) | 1 – pokrycie (overlap) | `taha2015` Table 5: niezalecany dla „Small segment”; `maierhein2024`: łączyć z miarą brzegową | znamiona 1–4 mm to małe obiekty |
| IoU (Jaccard) | 1 – pokrycie | monotonicznie zależny od Dice – ten sam ranking (`taha2015`, s. 5) | wystarczy raportować jedną z dwóch, drugą pomocniczo |
| HD95 | 6 – odległość przestrzenna (Taha: ogólny kwantyl HD, bez nazwy „HD95”) | `maierhein2024` SN 2.23: HD wrażliwa na pojedynczy błędny piksel, HD95 to ogranicza | – |
| ASSD | 6 – odległość (Taha ma AVD – **to nie to samo** co ASSD) | `maierhein2024` ED Fig. 7: ASSD wśród miar brzegowych | definicję ASSD podaj własnymi słowami (bez cytatu Taha) |
| stosunek pól | 2 – objętościowa (VS: „Volume is important”) | `taha2015` Table 5 | – |
| TRE [mm] | – | `fitzpatrick1998`: TRE, a nie FRE, jako miara dokładności | E1 |

---

## 4. Pakiet minimalny (propozycja na ≤ 8 stron)

1. **Rys. 2.1** – R01 (Herman: znacznik na skórze + termogram) **albo** R07 (Oniga: znacznik w VIS/NIR/TH). Jeden z dwóch; R07 lepiej pokazuje znacznik w trzech modalnościach.
2. **Rys. 2.2** – R03 (Zitová: etapy rejestracji) albo R05 (Chen: pętla rejestracji).
3. **Rys. 2.3** – R08 panel (a) (Han: punkty SURF / Harris nie pokrywają się w IR i ViS).
4. **Rys. 2.4** – R13 (U-Net).
5. **Rys. 2.5** – R18 (Taha: gwiazdy) albo R19 (Maier-Hein: jeden piksel a HD/HD95).
6. **Tabela 2.1** – D1 (zestawienie prac RGB–IR) w 2.5.
7. **Tabela 2.2** – D2 (PanDerm vs modele porównawcze) albo D3 (zbiory) w 2.3.3.

Na rysunki z innych prac w pracy dyplomowej zwykle wystarcza podpis ze źródłem („Źródło: \cite{…}”). Nie zmieniaj treści rysunku; przerysowany schemat oznacz „Opracowano na podstawie \cite{…}”. W razie wątpliwości co do wymagań wydziału zapytaj promotorkę.

**Przykładowe podpisy (LaTeX):**
```latex
\caption{Znacznik referencyjny na skórze w obrazach VIS, NIR i termowizyjnym. Źródło:~\cite{oniga2026}}
\caption{Punkty charakterystyczne SURF i Harrisa wykryte w obrazie podczerwonym i widzialnym. Źródło:~\cite{visible-and-infared}}
\caption{Architektura sieci U-Net. Źródło:~\cite{ronneberger2015}}
\caption{Zestawienie prac rejestrujących obraz widzialny z termowizyjnym. Opracowanie własne na podstawie~\cite{visualization-detection-cancer,visible-and-infared,non-contact-breathing-monitoring,gonzalezperez2021,oniga2026}}
```
