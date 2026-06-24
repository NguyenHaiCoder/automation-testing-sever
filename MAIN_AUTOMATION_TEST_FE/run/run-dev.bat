@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0\.."
set "ROOT=%CD%"

echo.
echo ==========================================
echo  MAIN_AUTOMATION_TEST_FE - React Dashboard
echo  Frontend only (API chay rieng)
echo ==========================================
echo  Root: %ROOT%
echo  URL:  http://localhost:5173
echo  API:  http://127.0.0.1:8765  (MAIN_AUTOMATION_TEST)
echo.

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm not found.
    pause
    exit /b 1
)

if not exist "%ROOT%\node_modules" (
    echo [SETUP] npm install...
    call npm install
)

echo [RUN] npm run dev
echo       Can chay API: MAIN_AUTOMATION_TEST\run\run-api.bat
echo.

call npm run dev
pause
