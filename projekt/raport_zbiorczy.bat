@echo off
rem Raport zbiorczy wszystkich par z wynikow potoku (najpierw potok_pary.bat 1-94)
rem Wynik: Inzynierka\wyniki\raport_zbiorczy\ (raport_zbiorczy.html, pary.csv, statystyki.csv, tabele.tex)
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" "%~dp0raport_zbiorczy.py" %*
pause
