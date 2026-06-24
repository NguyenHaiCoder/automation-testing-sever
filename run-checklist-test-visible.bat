@echo off
chcp 65001 >nul
REM ============================================================
REM  Chromium HIỂN THỊ — xem bot tự login / click / test
REM ============================================================

cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set WAIT_ENTER=1
set SLOW_MO=600
set ROLE_PAUSE_MS=5000

echo.
echo ========================================
echo  Checklist E2E — CHROMIUM VISIBLE
echo ========================================
echo  Chromium se MO LEN man hinh
echo  Sau khi test xong: nhan ENTER de dong browser
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    pause
    exit /b 1
)

python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing playwright...
    pip install playwright requests -q
    python -m playwright install chromium
)

echo [RUN] python run_checklist_e2e.py --visible
echo.
python "%~dp0run_checklist_e2e.py" --visible
set EXIT_CODE=%ERRORLEVEL%

echo.
if exist "%~dp0log-playwright\latest\summary.txt" (
    echo --- Summary ---
    type "%~dp0log-playwright\latest\summary.txt"
)
echo.
pause
exit /b %EXIT_CODE%
