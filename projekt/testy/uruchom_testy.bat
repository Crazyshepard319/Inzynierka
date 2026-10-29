@echo off
rem Testy funkcjonalne systemu bez GUI (rozdzial 6.6): srodowisko aplikacji, wyniki w oknie i w testy\wynik_testow.txt
cd /d "%~dp0.."
"%~dp0..\..\inzynierka\Scripts\python.exe" -m unittest discover -s testy -v > testy\wynik_testow.txt 2>&1
type testy\wynik_testow.txt
pause
