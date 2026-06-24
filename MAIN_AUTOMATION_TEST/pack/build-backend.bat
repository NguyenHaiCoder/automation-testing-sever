@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0\.."
set "ROOT=%CD%"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

echo.
echo ==========================================
echo  Build checklist-backend (PyInstaller)
echo ==========================================
echo.

set "PY=python"
where python >nul 2>&1
if errorlevel 1 set "PY=py"

"%PY%" -m pip install -q pyinstaller
"%PY%" -m pip install -q -r "%ROOT%\requirements.txt"

echo [1/3] PyInstaller...
"%PY%" -m PyInstaller "%ROOT%\pack\checklist-backend.spec" --noconfirm --distpath "%ROOT%\pack\dist" --workpath "%ROOT%\pack\build"
if errorlevel 1 (
    echo [ERROR] PyInstaller failed.
    pause
    exit /b 1
)

set "OUT=%ROOT%\pack\dist\checklist-backend"
if exist "%ROOT%\..\run_checklist_e2e.py" (
    echo [2/3] Copy run_checklist_e2e.py...
    copy /Y "%ROOT%\..\run_checklist_e2e.py" "%OUT%\"
)

if exist "%ROOT%\pack\ms-playwright" (
    echo [3/3] Copy Playwright Chromium...
    xcopy /E /I /Y "%ROOT%\pack\ms-playwright" "%OUT%\ms-playwright\" >nul
) else (
    echo [3/3] SKIP ms-playwright — chay pack\install-playwright.bat truoc khi dong goi
)

echo.
echo [OK] Backend: %OUT%\checklist-backend.exe
echo      Chay thu: %OUT%\checklist-backend.exe api
echo.
if "%~1"=="nopause" goto :eof
pause
