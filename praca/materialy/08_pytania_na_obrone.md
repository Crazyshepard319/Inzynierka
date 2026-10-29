# Pytania na obronę – z krótkimi odpowiedziami

Stan: 29.10.2026. Odpowiedzi oparte na wynikach z 28.10 (n = 92 pary, U-Net n = 94). Odpowiedź ustna: 1–2 minuty, zaczynaj od jednego zdania-tezy, potem liczba lub przykład. Jeśli nie znasz odpowiedzi – powiedz, co wiesz na pewno, i jak byś to sprawdził.

---

## A. Problem i cel

**1. Po co rejestrować zdjęcie z termowizją, skoro znamienia nie widać na termogramie?**
Właśnie dlatego: obszar znamienia można wyznaczyć tylko na zdjęciu, a żeby odczytać wartości z obrazu termowizyjnego w tym samym miejscu skóry, trzeba znać przekształcenie między obrazami. System przenosi znamię ze zdjęcia na obraz termowizyjny i zapisuje dla każdego piksela jego współrzędne i surową intensywność.

**2. Co jest wynikiem działania systemu?**
Raport HTML (obrazy, miary, objaśnienia), `metryki.json`, plik CSV z pikselami znamienia na obrazie termowizyjnym (x, y, ułamek pokrycia, intensywność z .SEQ) oraz wpis w bazie SQLite (analiza, miary, piksele).

**3. Czy system stawia diagnozę?**
Nie. To narzędzie do przestrzennego zestawienia danych z dwóch modalności i oceny wiarygodności tego zestawienia. Interpretacja termiczna i diagnostyka są poza zakresem.

## B. Znacznik i rejestracja

**4. Dlaczego znacznik ma kształt litery Π?**
Nie ma symetrii obrotowej, więc kąt jest jednoznaczny w 360°. Otwór 17 × 17 mm wyznacza obszar, w którym leży znamię. Osiem narożników daje homografię piksele → mm (skala) i punkty do oceny błędu TRE.

**5. Dlaczego folia aluminiowa?**
Na zdjęciu jest szara, metaliczna, z teksturą załamań – odróżnia się barwą od skóry. Na obrazie termowizyjnym ma niską emisyjność i odbija otoczenie, więc wygląda inaczej niż skóra (emisyjność skóry 0,96–0,98).

**6. Dlaczego ECC na maskach, a nie informacja wzajemna na obrazach?**
Intensywności obrazu widzialnego i termowizyjnego nie są ze sobą bezpośrednio powiązane, a informacja wzajemna może mieć wiele maksimów. Na maskach znacznika problem staje się jednomodalny. Wynik E4: mediana TRE 0,61 mm (ECC na maskach) wobec 3,36 mm (MI w otoczeniu znacznika) i 4,51 mm (MI na całym obrazie); ECC lepsze w 87 z 92 par (Wilcoxon, p < 0,001). MI nie poprawiło nawet dopasowania wstępnego (3,13 mm).

**7. Co to jest kryterium ECC?**
Rozszerzony współczynnik korelacji (Evangelidis i Psarakis, 2008): korelacja znormalizowanych (po odjęciu średniej) wektorów intensywności, niezmiennicza względem jasności i kontrastu. Maksymalizowany iteracyjnie; potrzebuje dobrego punktu startowego – dlatego najpierw dopasowanie przez podobieństwo i rozmycie masek od σ = 6 do 1,5 piksela.

**8. Kiedy homografia, a kiedy przekształcenie afiniczne?**
Homografia opisuje płaską scenę widzianą pod kątem (8 parametrów), afiniczne – bez perspektywy (6). Homografię wybiera się, gdy zmniejsza błąd krawędzi o > 5% i jest stabilna (skala w rogach kadru różni się od skali w środku znacznika najwyżej 2×). W 92 parach: homografia 65, afiniczne 27.

**9. Co to jest TRE i dlaczego nie wystarczy Dice masek znacznika?**
TRE (target registration error) to odległość odpowiadających sobie punktów po rejestracji – tu 8 narożników oznaczonych ręcznie w CVAT, w mm na płaszczyźnie znacznika. Dice masek, na których liczono transformację, jest wysoki z konstrukcji (optymalizacja go maksymalizuje), więc nie jest niezależną oceną (Fitzpatrick i in. pokazali to samo dla FRE).

**10. Skąd próg 1 mm?**
1 mm to ok. 3–4 piksele obrazu termowizyjnego (piksel na skórze 0,21–0,44 mm, mediana 0,28 mm) i mniej niż połowa średnicy typowego znamienia (mediana 2,1 mm). Mediana TRE 0,61 mm, ≤ 1 mm w 78 z 92 par.

**11. Co się stało w parze 78?**
Rejestracja nie powiodła się (TRE 24,7 mm). System to sygnalizował: zgodność znacznika na zdjęciu z wzorcem 0,52 (< 0,65 – ostrzeżenie) i najniższy Dice folii w E2 (0,72). Wszystkie cztery pary ze zgodnością na zdjęciu < 0,65 (8, 59, 78, 79) miały TRE > 1,3 mm.

**12. Dlaczego pary 75 i 76 nie zostały przeanalizowane?**
Maska znacznika na zdjęciu nie miała poprawnego otworu (2% i 8% otoczki zamiast 15–60%), a ponowna detekcja dała kształt niezgodny z Π (0,54 i 0,58). Bez otworu nie ma obszaru segmentacji znamienia – system kończy analizę komunikatem (WN6) zamiast podać błędny wynik.

## C. Segmentacja

**13. Dlaczego na termowizji segmentuje się znacznik, a nie znamię?**
Znamię bez schłodzenia skóry nie jest widoczne na obrazie termowizyjnym (Herman 2011). Model dedykowany termowizji (M3) segmentuje więc folię znacznika, a porównanie jej maski z maską przeniesioną ze zdjęcia (E2) weryfikuje zgodność obszaru zainteresowania.

**14. Dlaczego U-Net, i to mały?**
94 obrazy 320 × 240 – mało danych. U-Net był projektowany dla małych zbiorów biomedycznych (Ronneberger 2015). Wersja zmniejszona: 1,94 mln parametrów, kanały 16–256, silna augmentacja. Wynik: Dice 0,969 ± 0,008, HD95 mediana 0,62 mm; lepszy od detektora klasycznego (0,954, p < 0,001).

**15. Jak uniknięto przecieku danych przy walidacji?**
Podział na 5 foldów według znamion, nie zdjęć – 2–3 zdjęcia tego samego znamienia są w jednym foldzie. Liczbę epok (60) ustalono z góry, bez wybierania epoki na zbiorze testowym. Dla każdej pary system używa modelu foldu, w którym była testowa.

**16. Czym jest PanDerm i dlaczego go użyto?**
Model bazowy dla dermatologii (Yan i in., Nature Medicine 2025): koder ViT-L uczony samonadzorowanie na ok. 2,1 mln obrazów z 11 źródeł. Dodano dekoder UperNet i douczono na ISIC 2018 Task 1 (2594 obrazy): test Dice 0,899. Własnych zdjęć z maskami było za mało na trening od zera.

**17. Dlaczego PanDerm działa na zdjęciach z telefonu, skoro uczono go na dermoskopii?**
Przesunięcie dziedziny: w ISIC znamię zajmuje ok. połowy kadru, u nas 1–4 mm w otworze 17 mm. Rozwiązanie: szukanie tylko w otworze znacznika, do 3 kandydatów (ciemne plamy względem lokalnego tła skóry), kadr wokół kandydata jak w ISIC, wybór maski o największym kontraście brzegu. Wynik: Dice 0,870 (mediana 0,896); bez kandydatów mediana Dice wynosiła 0,06.

**18. Jakie są słabości segmentacji znamienia?**
Zawyżanie pola (mediana stosunku pól 1,10) – szerszy brzeg niż w adnotacji; porażki przy znamionach przy folii lub w jej cieniu (pary 57, 81: Dice 0,32 i 0,37) i przy bardzo bladym znamieniu (59: 0,55). Dalsza praca: douczenie na własnych zdjęciach.

## D. Miary i weryfikacja

**19. Dice a IoU – czym się różnią?**
Dice = 2|A∩B|/(|A|+|B|), IoU = |A∩B|/|A∪B|; IoU = Dice/(2 − Dice) – monotoniczne, ten sam ranking. Dla małych obiektów oba są wrażliwe na pojedyncze piksele, dlatego uzupełniono je miarami odległości w mm (HD95, ASSD) i stosunkiem pól.

**20. Co pokazuje badanie E2 i dlaczego jest ważne?**
Porównuje maskę folii ze zdjęcia przeniesioną przez T z maską z U-Netu – bez adnotacji, dla każdej nowej pary. Dice folii 0,957 ± 0,032; silnie skorelowany z TRE (ρ = −0,72). Najniższe E2 = najgorsze rejestracje (78, 8, 79). To kontrola jakości możliwa w praktyce, gdy nie ma ręcznych adnotacji.

**21. Po co liczyć w siatce 4× gęstszej?**
Znamię zajmuje na termowizji 10–290 pikseli (mediana 44). Schodki pikseli zaniżałyby miary i pole. Przeniesienie wektorowe (kontur przez T) i siatka 4× dają ułamek pokrycia każdego piksela z błędem pola ok. 1%; zgodność pola termowizja/zdjęcie 1,015 ± 0,034.

## E. Piksele i termografia

**22. Co to jest „surowa intensywność” i dlaczego nie temperatura?**
Wartość z detektora (16 bit) zapisana w nagraniu .SEQ, przed przeliczeniem na temperaturę (Planck + emisyjność + parametry otoczenia). Promotor zalecił intensywność; przeliczenie na °C zależy od założonej emisyjności i kalibracji. Orientacyjnie 1 °C ≈ 213 jednostek w zakresie 30–37 °C.

**23. Czy na podstawie pikseli można coś powiedzieć o znamieniu?**
W obrazach statycznych – niewiele: odchylenie intensywności w znamieniu mediana 14 jednostek (≈ 0,07 °C). Zgodne z literaturą: bez schłodzenia znamię się nie wyróżnia. System dostarcza jednak dane w formacie gotowym do termografii dynamicznej (sekwencja po schłodzeniu).

**24. Jak dokładność rejestracji wpływa na piksele?**
Przy medianie TRE 0,61 mm (≈ 2 piksele) piksele brzegowe mogą być skórą obok. Dlatego zapisany jest ułamek pokrycia, a „w masce” są tylko piksele pokryte ≥ 50%; można też analizować tylko wnętrze (erozja o 1–2 piksele).

## F. Inżynieria systemu

**25. Dlaczego SQLite?**
Jeden plik, bez serwera, jeden użytkownik, SQL do analiz. Obrazy w plikach, w bazie ścieżki i wyniki. Tabela `miara` w układzie długim – nowe miary bez zmiany schematu; tabela `piksel` z kluczem (analiza, x, y). Schemat ma wersję i migrację.

**26. Dlaczego dwa środowiska Pythona?**
PyTorch z CUDA to kilka GB – aplikacja go nie potrzebuje. U-Net wyeksportowany do ONNX działa przez OpenCV (ok. 67 ms/obraz na CPU), a PanDerm uruchamiany jest jako osobny proces w środowisku modeli.

**27. Jak przetestowano system?**
18 testów automatycznych (`unittest`) przypisanych do wymagań WF/WN: wczytanie, błędne dane, kolejność etapów, rejestracja (czas 6,4 s, TRE 0,69 mm dla pary 14), brak znacznika, piksele i CSV, raport, baza i migracja, miary na maskach o znanym wyniku. Do tego scenariusze ręczne GUI.

**28. Co byś zrobił inaczej / co dalej?**
Termografia dynamiczna; douczenie M1 na zdjęciach z telefonu; zatrzymywanie analizy przy niepewnym znaczniku na termowizji i ostrzeżenie przy E2 < 0,93; więcej serii, osób i oznaczających; kalibracja temperatury; ocena użyteczności z lekarzami.

---

## Pytania „z kierunku”, które łatwo powiązać z pracą

- **Emisyjność i prawo Stefana–Boltzmanna** – dlaczego skóra jest prawie ciałem doskonale czarnym (0,96–0,98), a folia odbija otoczenie.
- **Przeuczenie (overfitting)** i jak mu zapobiegano (augmentacja, mały model, stała liczba epok, walidacja krzyżowa po znamionach).
- **Homografia** – ile punktów potrzeba (4), kiedy opisuje scenę (płaszczyzna lub czysty obrót kamery).
- **Splot, pooling, połączenia skrótowe w U-Net** – po co dekoder dostaje mapy kodera (lokalizacja).
- **Transfer learning / model bazowy** – różnica między douczaniem a uczeniem od zera.
