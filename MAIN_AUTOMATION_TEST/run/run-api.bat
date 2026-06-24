@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0\.."
set "ROOT=%CD%"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

echo.
echo ==========================================
echo  MAIN_AUTOMATION_TEST - API Server
echo  Dashboard backend for React FE
echo ==========================================
echo  Root: %ROOT%
echo  URL:  http://127.0.0.1:8765
echo.

set "PY=python"
where python >nul 2>&1
if errorlevel 1 (
    set "PY=py"
    where py >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found.
        pause
        exit /b 1
    )
)

"%PY%" -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] pip install -r requirements.txt
    "%PY%" -m pip install -r "%ROOT%\requirements.txt"
)

echo [RUN] %PY% -m api
echo       Nhan Ctrl+C de dung.
echo.

"%PY%" -m api
pause
