@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================
echo   Ritmika — запуск магазина
echo ============================================
echo.

set PY=
where python >nul 2>nul && set PY=python
if not defined PY ( where py >nul 2>nul && set PY=py -3 )
if not defined PY (
  echo Python не найден на этом компьютере.
  echo Установите его с сайта https://www.python.org/downloads/
  echo при установке отметьте галочкой "Add Python to PATH",
  echo затем запустите этот файл снова.
  echo.
  pause
  exit /b 1
)

echo [1/2] Установка зависимостей (первый запуск может занять минуту)...
%PY% -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo Не удалось установить зависимости. Проверьте интернет и попробуйте снова.
  pause
  exit /b 1
)

echo [2/2] Запуск сервера...
echo.
echo    Сайт откроется:  http://127.0.0.1:5000
echo    Остановка: закройте это окно (или Ctrl+C)
echo.

start "" cmd /c "timeout /t 2 >nul & start "" http://127.0.0.1:5000"
%PY% run.py

echo.
echo Сервер остановлен.
pause
