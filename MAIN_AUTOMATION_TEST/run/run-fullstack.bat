@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0\.."
set "ROOT=%CD%"
set "FE=%ROOT%\..\MAIN_AUTOMATION_TEST_FE"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

echo.
echo ==========================================
echo  Full Stack Dev - API + React FE
echo ==========================================
echo  API:  MAIN_AUTOMATION_TEST  :8765
echo  FE:   MAIN_AUTOMATION_TEST_FE :5173
echo.

set "PY=python"
where python >nul 2>&1
if errorlevel 1 set "PY=py"

start "Checklist API" cmd /k "cd /d %ROOT% && %PY% -m api"

timeout /t 2 /nobreak >nul

start "Checklist FE" cmd /k "cd /d %FE% && npm run dev"

echo [OK] Da mo 2 cua so: API va FE
pause
