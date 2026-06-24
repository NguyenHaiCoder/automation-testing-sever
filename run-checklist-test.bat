@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
set PYTHONIOENCODING=utf-8

REM ============================================================
REM  Run Playwright E2E — Checklist Nhân sự
REM  Log: log-playwright\run_YYYYMMDD_HHMMSS\
REM ============================================================

cd /d "%~dp0"
set "LOG_DIR=%~dp0log-playwright"
set "SETUP_LOG=%LOG_DIR%\setup.log"

echo.
echo ========================================
echo  Checklist Playwright E2E Test Runner
echo ========================================
echo  Working dir: %~dp0
echo  Log folder:  %LOG_DIR%
echo.

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM --- check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)

REM --- install dependencies if missing ---
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing playwright + requests...
    echo [SETUP] Installing playwright + requests... >> "%SETUP_LOG%"
    pip install playwright requests >> "%SETUP_LOG%" 2>&1
    python -m playwright install chromium >> "%SETUP_LOG%" 2>&1
    echo [SETUP] Done. See %SETUP_LOG%
)

REM --- run tests (headless mac dinh) ---
echo  HEADLESS mode — dung run-checklist-test-visible.bat de mo Chromium
echo.

REM --- run tests ---
echo [RUN] Starting tests...
echo.
python "%~dp0run_checklist_e2e.py"
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% equ 0 (
    echo [OK] Tests finished successfully.
) else (
    echo [FAIL] Tests finished with errors. Exit code: %EXIT_CODE%
)

REM --- show latest summary if exists ---
if exist "%LOG_DIR%\latest\summary.txt" (
    echo.
    echo --- Latest Summary ---
    type "%LOG_DIR%\latest\summary.txt"
)

echo.
echo Full logs: %LOG_DIR%
if exist "%LOG_DIR%\last_run.txt" (
    set /p LAST_RUN=<"%LOG_DIR%\last_run.txt"
    echo This run:  !LAST_RUN!
)
echo.
pause
exit /b %EXIT_CODE%
