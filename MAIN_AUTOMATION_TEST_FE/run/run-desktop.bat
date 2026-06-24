@echo off
setlocal
cd /d "%~dp0\.."
echo.
echo ==========================================
echo  Checklist Tester — Desktop (Electron)
echo  Truong phong: double-click file nay
echo ==========================================
echo.

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Can cai Node.js
    pause
    exit /b 1
)

if not exist node_modules call npm install

call npm run desktop:dev
