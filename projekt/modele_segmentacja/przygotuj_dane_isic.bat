@echo off
rem Pobranie (ok. 14 GB) i przygotowanie zbioru ISIC 2018 Task 1
cd /d "%~dp0.."
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" -u -m modele_segmentacja.modele.panderm_upernet.dane pobierz
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" -u -m modele_segmentacja.modele.panderm_upernet.dane przygotuj
pause
