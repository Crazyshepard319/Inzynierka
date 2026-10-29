"""
Analiza wielomodalna pary RGB - termowizja: etapy systemu wspolne dla aplikacji (aplikacja.py)
i potoku wsadowego (potok_pary.py).

    system.py    etapy systemu: wejscie, rejestracja, segmentacja (narozniki znacznika, znamie PanDerm),
                 przeniesienie ROI na termowizje, pomiary i zgodnosc, raport (klasa Analiza)
    dane.py      dane par z dane/pary/N/: informacje z plikow mapowania, adnotacje z CVAT, surowa
                 intensywnosc termowizji z nagrania .SEQ
    geometria.py przenoszenie punktow i masek przez macierz T, homografia px -> mm, skala mm/px
    miary.py     miary zgodnosci: Dice, IoU, HD95, ASSD, przesuniecie srodkow, stosunek pol, TRE
    pomiary.py   parametry znamienia: geometria i kolor (RGB); piksele znamienia na termowizji (x, y, surowa
                 intensywnosc z nagrania .SEQ) i ich CSV; temperatura (nieuzywana w raporcie)
    obrazy.py    obrazy do raportu: zdjecie, termowizja, nalozenie i jego zblizenie wokol znamienia
    raport.py    raport HTML pary (obrazy osadzone w pliku) z objasnieniem wszystkich wielkosci
"""
