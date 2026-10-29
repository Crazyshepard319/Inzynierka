# Zwroty do rozdziału 2 „Analiza stanu wiedzy” (pkt 2)

Stan: 26.10.2026.

Fakty w przykładowych zdaniach pochodzą z kart w `03_streszczenia_artykulow.md` – przed użyciem sprawdź stronę w karcie. Nawiasy kwadratowe [ … ] to miejsca do uzupełnienia. Przykłady są wzorami konstrukcji zdań, nie gotowym tekstem rozdziału (wzór rozdziału będzie w pkt 6).

---

## 1. Jak pisać ten rozdział – 6 zasad

1. **Synteza, nie wyliczanka.** Akapit zaczyna się od tezy (problemu, pojęcia, kategorii metod), a artykuły ją ilustrują. Zła struktura: „Autor A zrobił… Autor B zrobił… Autor C zrobił…”. Dobra: „Metody oparte na cechach zawodzą dla par RGB–IR, ponieważ… [A]. Rozwiązaniem jest… [B, C].”
2. **Schemat akapitu:** teza → źródło (co pokazali, na jakich danych, z jakim wynikiem) → porównanie / ograniczenie → wniosek dla Twojej pracy. Ostatnie zdanie podrozdziału łączy literaturę z systemem.
3. **Każda liczba z kontekstem:** czego dotyczy, na jakich danych, jaką miarą. „Dice 0,91” bez kontekstu jest bezwartościowe. Dobrze: „Dice 0,910 na zbiorze testowym ISIC 2018 (obrazy dermatoskopowe)”.
4. **Parafraza, nie tłumaczenie abstraktu.** Własnymi słowami, inną kolejnością, z własnym wnioskiem. Cytat dosłowny tylko wyjątkowo, w cudzysłowie.
5. **Cytuj tylko to, co jest w źródle.** Jeśli fakt znasz z przeglądu, cytuj przegląd, a nie pracę, której nie czytałeś (zob. „cytowanie pośrednie” niżej).
6. **Budżet ≤ 8 stron:** ok. 1 akapit na ważny artykuł, 1 zdanie na poboczny. Szczegóły metod, których nie używasz (np. architektura GAN), pomijaj.

---

## 2. Czasowniki do relacjonowania prac

| Funkcja | Czasowniki (forma „autorzy …”) | Kiedy używać |
|---|---|---|
| Neutralny opis | opisują, przedstawiają, omawiają, analizują, stosują, wykorzystują | przeglądy, opis metody |
| Wkład / nowość | zaproponowali, opracowali, wprowadzili, rozszerzyli, zmodyfikowali | nowa metoda, miara, zbiór |
| Wynik badania | wykazali, uzyskali, osiągnęli, zaobserwowali, odnotowali, stwierdzili | konkretny wynik eksperymentu |
| Wynik teoretyczny | wyprowadzili, pokazali analitycznie | wzory (np. Fitzpatrick – wyrażenie na TRE) |
| Interpretacja autorów | wskazują, zwracają uwagę, podkreślają, sugerują, postulują, zalecają | wnioski i rekomendacje (np. Metrics Reloaded) |
| Porównanie | porównali, zestawili, ocenili | prace porównujące metody (González-Pérez) |
| Dystans / krytyka | twierdzą, przyjmują, zakładają | gdy nie podzielasz wniosku lub jest on niesprawdzony |

**Czas:**
- konkretne badanie – czas przeszły („zaproponowali”, „uzyskali”);
- treść przeglądu lub stan obecny – czas teraźniejszy („przegląd wskazuje”, „metody te wymagają”).

**Unikaj:**
- „udowodnili” – poza dowodem matematycznym;
- „pokazali, że … jest najlepsza” – zwykle chodzi o „najlepsza w ich eksperymencie”;
- „jak wiadomo” – bez źródła.

---

## 3. Cytowanie – mechanika (LaTeX)

- **Dwóch autorów:** oba nazwiska. „Evangelidis i Psarakis~\cite{evangelidis2008} zaproponowali…”
- **Trzech i więcej:** „i in.” albo „i współautorzy”. „Oniga i in.~\cite{oniga2026}…”. Wybierz jedną formę i trzymaj się jej.
- **Cytat na końcu zdania**, przed kropką: „…jest otwartym problemem~\cite{deep-learning}.”
- **Kilka źródeł:** jeden `\cite{visualization-detection-cancer,magalhaes2019}`, nie `\cite{visualization-detection-cancer}\cite{magalhaes2019}`.
- **Tylda `~`** przed `\cite` – zapobiega złamaniu wiersza między słowem a numerem.
- **Nie zaczynaj zdania od numeru:** zdanie „[3] wykazał…” jest złe; dobrze: „Celebi i in.~\cite{dermoscopy} wskazują…”.
- **Konkretna strona** (np. przy liczbie, definicji): `\cite[s.~5]{taha2015}` – podaj stronę **drukowaną** (przelicznik w nagłówku `03_streszczenia_artykulow.md`).
- **Cytowanie pośrednie:** gdy fakt pochodzi z przeglądu, a oryginału nie masz: „…metody progowania adaptacyjnego (za:~\cite{mirikharaji2023})” albo „Według przeglądu~\cite{mirikharaji2023}, …”. Nie dodawaj do bibliografii pracy, której nie czytałeś.
- **Rysunek / tabela z artykułu:** w podpisie „Źródło: \cite{…}”; zmodyfikowany – „Opracowano na podstawie \cite{…}”. Zbudowany z danych kilku prac – „Opracowanie własne na podstawie \cite{…,…}”.

---

## 4. Zwroty według funkcji

### 4.1 Wprowadzenie podrozdziału
- „W niniejszym podrozdziale omówiono…”
- „Podrozdział przedstawia podstawowe pojęcia związane z…, a następnie…”
- „Zagadnienie … można rozpatrywać na dwóch poziomach: … oraz …”
- „Ze względu na zakres pracy ograniczono się do…”
- „Pominięto metody…, ponieważ nie mają zastosowania w rozważanym przypadku.”

### 4.2 Definiowanie pojęć
- „Przez … rozumie się…”
- „… definiuje się jako…”
- „W literaturze termin … odnosi się do…”
- „Zgodnie z definicją podaną w~\cite{…}, …”
- „Pojęcie to bywa używane niejednoznacznie: …”
- **Wzór:** „Rejestracja obrazów to proces geometrycznego dopasowania obrazu rejestrowanego do obrazu referencyjnego, przedstawiających tę samą scenę w różnym czasie, z różnych punktów widzenia lub z użyciem różnych sensorów~\cite{zitova2003}.”

### 4.3 Klasyfikacja i podział metod
- „Metody … dzieli się zazwyczaj na…”
- „W literaturze wyróżnia się dwie zasadnicze grupy metod: … oraz …”
- „Ze względu na … wyróżnia się…”
- „Pierwszą grupę stanowią…, drugą – …”
- „Podział ten nie jest rozłączny – …”
- **Wzór:** „Zitová i Flusser~\cite{zitova2003} dzielą metody rejestracji na obszarowe (ang. *area-based*) i oparte na cechach (ang. *feature-based*). Proces rejestracji opisują czterema etapami: detekcją cech, ich dopasowaniem, estymacją modelu transformacji oraz transformacją i przepróbkowaniem obrazu.”

### 4.4 Relacjonowanie jednej pracy (metoda → dane → wynik)
- „[Autor] i in.~\cite{…} zaproponowali metodę…, w której…”
- „Metodę zweryfikowano na zbiorze [liczba] [jakich] obrazów…”
- „Autorzy uzyskali [miara] równą [wartość] (…), przy czym…”
- „Kluczowym elementem rozwiązania jest…”
- „Rozwiązanie składa się z dwóch etapów: … Następnie …”
- **Wzór:** „Oniga i in.~\cite{oniga2026} rejestrują obrazy zmian skórnych w świetle widzialnym, bliskiej podczerwieni i termowizji. Na skórze wokół zmiany umieszczają kwadratowy znacznik referencyjny, lokalizowany detektorem YOLOv8n. Następnie sieć typu ResU-Net przewiduje mapy cieplne punktów kluczowych, z których wyznacza się homografię. Zbiór obejmował 155 trójek obrazów od 62 pacjentów.”

### 4.5 Podawanie wyników liczbowych
- „…osiągając [miara] na poziomie [wartość] na zbiorze…”
- „Mediana błędu wyniosła…, a…”
- „Wynik ten uzyskano w warunkach…, dlatego nie można go bezpośrednio porównać z…”
- „Różnica … była (nie)istotna statystycznie (p = …).”
- „Wartości te dotyczą…, a nie…”
- **Wzór:** „W pracy~\cite{non-contact-breathing-monitoring} średni błąd rejestracji (TRE) wyniósł 1,8 piksela dla 50 par obrazów RGB–termowizja.”
- **Wzór z zastrzeżeniem:** „Wartości Dice powyżej 0,95 uzyskane w~\cite{gonzalezperez2021} dotyczą masek całych stóp, czyli obiektów dużych w porównaniu ze znamieniem. Nie są więc porównywalne z wynikami dla małych struktur.”

### 4.6 Porównywanie prac
- „Podobne podejście zastosowali…”
- „W odróżnieniu od…, w pracy~\cite{…}…”
- „Oba rozwiązania łączy…, różnią się natomiast…”
- „W przeciwieństwie do metod opartych na…, …”
- „Zestawienie omówionych prac przedstawiono w tabeli 2.x.”
- „Wspólną cechą przytoczonych rozwiązań jest…”
- **Wzór:** „Herman i Pirtini Cetingul~\cite{visualization-detection-cancer} oraz Oniga i in.~\cite{oniga2026} stosują kwadratowy znacznik naklejany na skórę. W pierwszej pracy narożniki znacznika służą do wyrównania sekwencji obrazów IR, w drugiej znacznik wyznacza obszar zainteresowania, w którym sieć neuronowa szuka punktów kluczowych.”

### 4.7 Ograniczenia i krytyka
- „Istotnym ograniczeniem tej metody jest…”
- „Metoda wymaga…, co w rozważanym przypadku jest trudne do spełnienia, ponieważ…”
- „Wyniki uzyskano na niewielkim zbiorze…, co ogranicza możliwość uogólnienia.”
- „Autorzy nie podają…” / „W pracy nie oceniono…”
- „Podejście to sprawdza się, gdy…, natomiast zawodzi, gdy…”
- **Wzór:** „Han i in.~\cite{visible-and-infared} wykazali, że punkty charakterystyczne SURF i Harrisa nie są powtarzalne między obrazami widzialnymi a podczerwonymi. Ich metoda wymaga jednak prostoliniowych struktur, typowych dla otoczenia zbudowanego przez człowieka, i nie przenosi się na obrazy skóry.”

### 4.8 Ostrożne formułowanie (hedging)
- „może wskazywać na…”, „sugeruje, że…”
- „w rozważanych warunkach”, „w badanym zbiorze”
- „z dużym prawdopodobieństwem”, „w przybliżeniu”
- „według autorów”, „jak twierdzą autorzy”
- „wyniki te należy traktować ostrożnie, ponieważ…”
- „brak jednoznacznych dowodów na…”

### 4.9 Przejścia między akapitami i podrozdziałami
- „Odmienne podejście prezentują…”
- „Problem ten rozwiązują częściowo metody…”
- „Kolejną grupę stanowią…”
- „Niezależnie od…, wszystkie omówione metody…”
- „Z powyższego wynika, że…”
- „Wobec tego naturalnym rozwiązaniem jest…”
- „Zagadnienie to omówiono szerzej w podrozdziale 2.x.”

### 4.10 Odniesienie do własnej pracy (koniec akapitu / podrozdziału)
- „W niniejszej pracy…”
- „Z tego względu w systemie zastosowano…”
- „Rozwiązanie przyjęte w pracy nawiązuje do…, z tą różnicą, że…”
- „Obserwacja ta uzasadnia wybór…”
- „Analogicznie, w niniejszej pracy…”
- **Wzór:** „Z tego względu w niniejszej pracy miarę podobieństwa oblicza się nie na surowych obrazach, lecz na maskach znacznika wyodrębnionych w obu modalnościach, co sprowadza problem wielomodalny do jednomodalnego.”

### 4.11 Luka badawcza i podsumowanie (2.5)
- „Przeprowadzony przegląd wskazuje, że…”
- „W analizowanej literaturze nie znaleziono rozwiązania, które…” (ostrożniej niż „nie istnieje”)
- „Dotychczasowe prace koncentrują się na…, natomiast…”
- „Żadna z omówionych prac nie łączy… z…”
- „Lukę tę wypełnia niniejsza praca, w której…”
- „Na podstawie przeglądu sformułowano następujące wnioski dla projektu systemu: …”

---

## 5. Szkielety dla podrozdziałów rozdziału 2

### 2.1 Obrazowanie zmian skórnych
- Termografia – zasada: „Termografia rejestruje promieniowanie podczerwone emitowane przez skórę, której emisyjność wynosi 0,96–0,98~\cite{infared-thermal-imaging}.”
- Standaryzacja: „Wiarygodność pomiaru termograficznego zależy od standaryzacji badania, w tym od powtarzalnego wyznaczania obszaru zainteresowania~\cite{infared-thermal-imaging}.”
- Termografia dynamiczna: „W termografii dynamicznej obraz rejestruje się po wymuszeniu termicznym, najczęściej kontrolowanym schłodzeniu skóry~\cite{visualization-detection-cancer,magalhaes2019}.”
- Wynik kliniczny: „Magalhaes i in.~\cite{magalhaes2019} uzyskali dla 46 zmian (16 czerniaków, 30 znamion) dokładność klasyfikacji 84,2% przy czułości 91,3% [sprawdź w karcie, której cechy i klasyfikatora to dotyczy].”
- Przejście do rejestracji: „Ponieważ bez schłodzenia zmiana jest na termogramie niewidoczna~\cite{visualization-detection-cancer}, jej położenie trzeba przenieść z obrazu w świetle widzialnym…”
- Dermatoskopia / zdjęcie: „Komputerowa analiza obrazów dermatoskopowych obejmuje segmentację, ekstrakcję cech i klasyfikację, przy czym segmentacja stanowi pierwszy i trudny etap~\cite{dermoscopy}.”

### 2.2 Rejestracja obrazów wielomodalnych
- 2.2.1: „Wybór modelu transformacji określa, jakie zniekształcenia mogą zostać skompensowane…” · „Miara podobieństwa … jest niezmiennicza względem…” · „Evangelidis i Psarakis~\cite{evangelidis2008} zaproponowali kryterium ECC, niezmiennicze względem zmian jasności i kontrastu…”
- 2.2.1 (miary statystyczne, opcjonalnie): „Roche i in.~\cite{correlation-ratio} pokazali na przykładzie syntetycznym, że informacja wzajemna może mieć wiele równoważnych maksimów…”
- 2.2.2: „Rejestrację obrazów widzialnych i termowizyjnych utrudnia brak bezpośredniej zależności między intensywnościami pikseli~\cite{visible-and-infared}.” · „W zastosowaniach medycznych korespondencję zapewnia się zwykle przez obiekty widoczne w obu modalnościach – szachownice kalibracyjne~\cite{gonzalezperez2021}, ramy kalibracyjne~\cite{non-contact-breathing-monitoring} lub znaczniki naklejane na skórę~\cite{visualization-detection-cancer,oniga2026}.”
- 2.2.3: „Przegląd~\cite{deep-learning-in-registration} obejmujący 77 prac dzieli metody głębokiej rejestracji na…” · „Hu i in.~\cite{neural-networks} wykorzystują etykiety anatomiczne wyłącznie na etapie uczenia, a podczas wnioskowania sieć potrzebuje jedynie pary obrazów.” · „Metody te wymagają dużych zbiorów uczących, którymi dla pary telefon–kamera termowizyjna nie dysponowano.”
- 2.2.4: „Zhang i Demiris~\cite{deep-learning} wyróżniają fuzję na poziomie pikseli, cech i decyzji…” · „Fuzja pikselowa wymaga dokładnej rejestracji…” · „W niniejszej pracy nałożenie obrazów pełni funkcję wizualizacji wyniku rejestracji.”

### 2.3 Segmentacja obrazów medycznych
- 2.3.1: „Przed upowszechnieniem uczenia głębokiego segmentację zmian skórnych realizowano m.in. progowaniem adaptacyjnym, konturami aktywnymi i rozrostem obszaru (za:~\cite{mirikharaji2023}).” · „Metody te opierają się na cechach projektowanych ręcznie, co ogranicza ich odporność na…”
- 2.3.2: „Architektura U-Net~\cite{ronneberger2015} składa się ze ścieżki kurczącej, gromadzącej kontekst, i symetrycznej ścieżki rozszerzającej, zapewniającej dokładną lokalizację; połączenia skrótowe przekazują cechy wysokiej rozdzielczości z kodera do dekodera.” · „Sieć uczono na 30 obrazach (wyzwanie ISBI 2012), co pokazuje przydatność architektury przy małych zbiorach danych.”
- 2.3.2 (UperNet): „Dekoder UperNet~\cite{xiao2018upernet} łączy piramidę cech (FPN) z modułem PPM…”
- 2.3.3: „Przegląd~\cite{mirikharaji2023} obejmuje 177 prac z lat 2014–2022; zbiory ISIC wykorzystano w 168 z nich.” · „Model bazowy PanDerm~\cite{yan2025panderm} pretrenowano samonadzorowanie na 2 149 706 obrazach z 11 źródeł i 4 modalności…” · „Zbiór HAM10000~\cite{tschandl2018} …” · „W wyzwaniu ISIC 2018 wprowadzono progowany indeks Jaccarda: wynik poniżej 0,65 zastępuje się zerem, a segmentację traktuje jako porażkę~\cite{codella2019}.” · „Próg wyznaczono na podstawie zgodności trzech ekspertów (średni indeks Jaccarda 0,786)~\cite{codella2019}.” · „Mimo średnich wartości indeksu Jaccarda powyżej 0,8 większość metod zawodziła na ponad 10\% obrazów, najczęściej przy rogowaceniu łojotokowym~\cite{codella2019}.”
- 2.3.3 (przesunięcie dziedziny): „Modele uczone na obrazach dermatoskopowych pracują na zdjęciach z telefonu w warunkach przesunięcia dziedziny (ang. *domain shift*)…”
- 2.3.4: „Ponieważ znamię nie jest widoczne na termogramie statycznym~\cite{visualization-detection-cancer}, w termowizji segmentuje się obiekt referencyjny – znacznik…”

### 2.4 Miary oceny rejestracji i segmentacji
- „Fitzpatrick i in.~\cite{fitzpatrick1998} rozróżniają błąd lokalizacji znacznika (FLE), błąd rejestracji znaczników (FRE) i błąd w punkcie docelowym (TRE). Wskazują, że FRE jest zawodnym wskaźnikiem dokładności rejestracji.”
- „Taha i Hanbury~\cite{taha2015} zestawili 20 miar oceny segmentacji w sześciu kategoriach…” · „Współczynnik Dice'a i indeks Jaccarda są ze sobą powiązane monotonicznie, dlatego dają ten sam ranking segmentacji~\cite{taha2015}.”
- „Zgodnie z zaleceniami Metrics Reloaded~\cite{maierhein2024} miarę pokrycia uzupełnia się miarą brzegową…” · „Autorzy wyróżniają trzy źródła błędów walidacji: …”
- „W pracy~\cite{gonzalezperez2021} jakość rejestracji oceniano przez zgodność masek (Dice, Jaccard) po przeniesieniu…”

### 2.5 Podsumowanie i luka
- „Zestawienie prac rejestrujących obraz widzialny z termowizyjnym przedstawiono w tabeli 2.x.”
- Kolumny tabeli: praca · zastosowanie · źródło korespondencji · model transformacji · miara oceny · niezależna weryfikacja ROI.
- „Z przeglądu wynikają trzy wnioski dla projektu systemu: (1) …, (2) …, (3) …”

---

## 6. Typowe błędy – przykłady

| Źle | Dobrze |
|---|---|
| „W artykule [5] autorzy zrobili rejestrację i wyszło im dobrze.” | „Maurya i in.~\cite{non-contact-breathing-monitoring} uzyskali średni błąd rejestracji 1,8 piksela dla 50 par obrazów RGB–termowizja.” |
| „U-Net jest najlepszą siecią do segmentacji.” | „Architektura U-Net jest powszechnie stosowana w segmentacji obrazów biomedycznych, zwłaszcza przy małych zbiorach uczących~\cite{ronneberger2015,mirikharaji2023}.” |
| „PanDerm ma Dice 0,91.” | „Na zbiorze testowym ISIC 2018 PanDerm z dekoderem UperNet osiągnął Dice 0,910~\cite{yan2025panderm}.” |
| Akapit = streszczenie jednego artykułu bez związku z pracą | Ostatnie zdanie akapitu: „…dlatego w niniejszej pracy…” |
| „Jak wiadomo, MI jest standardem.” | „Informacja wzajemna jest powszechnie stosowaną miarą w rejestracji wielomodalnej~\cite{zitova2003,correlation-ratio}.” |
| Cytowanie Mattesa, Rothera (GrabCut), ViT, Blanda–Altmana bez PDF (pozycje B/C, usunięte) | MI – przez `zitova2003`/`correlation-ratio`, Mattes tylko jako nazwa metryki SimpleITK; ViT – jako koder PanDerm~\cite{yan2025panderm}; GrabCut – bez nazwy („krawędź folii doprecyzowano segmentacją interaktywną z OpenCV”); Bland–Altman – nie opisywać, zgodność pól podać prostymi statystykami (średnia różnica, SD, stosunek pól) |

---

## 7. Słowniczek PL–EN (do spójności terminów)

| Polski termin (używaj w pracy) | Angielski (w nawiasie przy 1. użyciu) |
|---|---|
| rejestracja obrazów | image registration |
| obraz referencyjny / obraz rejestrowany (ruchomy) | reference (fixed) / sensed (moving) image |
| model transformacji, przekształcenie afiniczne, homografia | transformation model, affine transform, homography |
| miara podobieństwa | similarity measure |
| informacja wzajemna | mutual information (MI) |
| rozszerzony współczynnik korelacji | enhanced correlation coefficient (ECC) |
| punkt charakterystyczny, deskryptor | keypoint, descriptor |
| znacznik referencyjny | fiducial marker |
| błąd lokalizacji znacznika / rejestracji znaczników / w punkcie docelowym | FLE / FRE / TRE |
| fuzja obrazów | image fusion |
| obszar zainteresowania | region of interest (ROI) |
| segmentacja, maska binarna | segmentation, binary mask |
| architektura koder–dekoder, połączenia skrótowe | encoder–decoder, skip connections |
| model bazowy | foundation model |
| uczenie samonadzorowane | self-supervised learning |
| douczanie | fine-tuning |
| przesunięcie dziedziny | domain shift |
| walidacja krzyżowa | cross-validation |
| współczynnik Dice'a, indeks Jaccarda | Dice similarity coefficient (DSC), Jaccard index (IoU) |
| 95. percentyl odległości Hausdorffa | 95th percentile Hausdorff distance (HD95) |
| średnia symetryczna odległość powierzchni | average symmetric surface distance (ASSD) |
| termografia statyczna / dynamiczna | static / dynamic (active) thermography |
| emisyjność | emissivity |
