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
if defined PY goto found

where py >nul 2>nul
if errorlevel 1 goto nopython
set PY=py -3

:found
echo [1/2] Ustanovka zavisimostey, pervyy zapusok mozhet zanyat minutu...
%PY% -m pip install -q -r requirements.txt
if errorlevel 1 goto pipfail

echo [2/2] Zapusk servera. Brauzer otkroetsya sam cherez paru sekund.
echo Ostanovka: zakroyte eto okno ili nazhmite Ctrl+C.
echo.
%PY% run.py
echo.
echo Server ostanovlen.
pause
exit /b 0

:pipfail
echo Ne udalos ustanovit zavisimosti. Proverte internet i poprobuyte snova.
pause
exit /b 1

:nopython
echo Python ne nayden na etom kompyutere.
echo Ustanovite ego s sayta https://www.python.org/downloads/
echo pri ustanovke otmette galochkoy "Add Python to PATH",
echo zatem zapustite etot fayl snova.
pause
exit /b 1
