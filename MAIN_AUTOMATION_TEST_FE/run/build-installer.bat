@echo off
setlocal
cd /d "%~dp0\.."

echo [1] Build backend...
call "%~dp0..\..\MAIN_AUTOMATION_TEST\pack\build-backend.bat" nopause
if errorlevel 1 exit /b 1

echo.
echo [2] Build Electron app...
cd /d "%~dp0.."
call npm install
call npm run desktop:build

echo.
echo [OK] Installer: release\ChecklistTester-Setup-*.exe
pause
