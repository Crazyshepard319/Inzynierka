@echo off
rem Potok analizy par w srodowisku modeli (PyTorch dla PanDerm), np.: potok_pary.bat 1 3 10-20
"%USERPROFILE%\modele_dane\srodowisko\Scripts\python.exe" "%~dp0potok_pary.py" %*
if errorlevel 1 pause
