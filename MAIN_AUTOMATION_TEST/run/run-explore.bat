@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0\.."
set "ROOT=%CD%"
set "LOG_DIR=%ROOT%\log"
set "SETUP_LOG=%LOG_DIR%\setup.log"
set "PYTHONIOENCODING=utf-8"

echo.
echo ==========================================
echo  MAIN_AUTOMATION_TEST - Explore Checklist
echo  3 Chromium (ADMIN / OFFICER / EMPLOYEE)
echo ==========================================
echo  Root: %ROOT%
echo  Log:  %LOG_DIR%
echo.

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set "PY=python"
where python >nul 2>&1
if errorlevel 1 (
    set "PY=py"
    where py >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found. Install Python 3.10+ or add to PATH.
        pause
        exit /b 1
    )
)

"%PY%" --version
if errorlevel 1 (
    echo [ERROR] Python cannot run.
    pause
    exit /b 1
)

"%PY%" -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing playwright...
    "%PY%" -m pip install -r "%ROOT%\requirements.txt" >> "%SETUP_LOG%" 2>&1
    "%PY%" -m playwright install chromium >> "%SETUP_LOG%" 2>&1
)

echo.
echo [RUN] %PY% explore_checklist.py --visible
echo       Chromium se mo len man hinh
echo.
"%PY%" "%ROOT%\explore_checklist.py" --visible
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if exist "%LOG_DIR%\last_run.txt" (
    set /p "LAST=" < "%LOG_DIR%\last_run.txt"
    echo Last run: !LAST!
    if exist "!LAST!\docs\summary.md" (
        echo.
        echo --- docs\summary.md ---
        type "!LAST!\docs\summary.md"
    )
)
echo.
pause
exit /b %EXIT_CODE%
