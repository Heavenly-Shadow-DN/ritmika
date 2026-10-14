@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   Ritmika - zapusk magazina
echo ============================================
echo.

set PY=
where python >nul 2>nul
if not errorlevel 1 set PY=python
if defined PY goto checklib

where py >nul 2>nul
if errorlevel 1 goto nopython
set PY=py -3

:checklib
if exist lib goto run

echo Pervyy zapusk: ustanovka bibliotek v papku lib...
set PIP_USER=0
%PY% -m pip install --target lib -r requirements.txt
if errorlevel 1 goto pipfail

:run
echo Zapusk servera. Brauzer otkroetsya sam cherez paru sekund.
echo Ostanovka: zakroyte eto okno ili nazhmite Ctrl+C.
echo.
%PY% run.py
echo.
echo Server ostanovlen.
pause
exit /b 0

:pipfail
echo Ne udalos ustanovit biblioteki. Proverte internet i poprobuyte snova.
pause
exit /b 1

:nopython
echo Python ne nayden na etom kompyutere.
echo Ustanovite ego s sayta https://www.python.org/downloads/
echo pri ustanovke otmette galochkoy "Add Python to PATH",
echo zatem zapustite etot fayl snova.
pause
exit /b 1
