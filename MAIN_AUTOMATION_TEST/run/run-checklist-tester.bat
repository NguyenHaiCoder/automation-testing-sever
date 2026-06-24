@echo off
setlocal
cd /d "%~dp0"
set "BACKEND=%~dp0pack\dist\checklist-backend"
if not exist "%BACKEND%\checklist-backend.exe" (
    echo Chua build backend. Chay pack\build-backend.bat truoc.
    pause
    exit /b 1
)
set "PYTHONUTF8=1"
set "PLAYWRIGHT_BROWSERS_PATH=%BACKEND%\ms-playwright"
cd /d "%BACKEND%"
start "Checklist API" checklist-backend.exe api
echo API started. Mo MAIN_AUTOMATION_TEST_FE bang Electron hoac trinh duyet.
pause
