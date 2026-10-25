@echo off
rem Ocena segmentacji znamienia (Dice z adnotacjami CVAT) na wszystkich parach z dane\pary - liczy na GPU, jesli wolne.
rem Porownuje metode z aplikacji (kandydaci na znamie) z dawna (kadr = cale wnetrze znacznika).
rem Tylko nowa metoda: ocen_segmentacje.bat --metody kandydaci     Wybrane pary: --pary 1 2 3
rem Wynik: Inzynierka\wyniki\wyniki_segmentacji\ocena_panderm_upernet_DATA\ocena.csv
cd /d "%~dp0.."
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" -u -m modele_segmentacja.ocen_segmentacje %*
pause
