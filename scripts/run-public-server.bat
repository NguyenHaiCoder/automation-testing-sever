@echo off
REM Build React (public) + start Python API serving FE + API on one port
setlocal
cd /d "%~dp0"

echo [1/3] npm install (FE)...
cd MAIN_AUTOMATION_TEST_FE
call npm ci
if errorlevel 1 exit /b 1

echo [2/3] npm run build:web (RESTRICT_ADMIN sidebar)...
call npm run build:web
if errorlevel 1 exit /b 1
cd ..

echo [3/3] Start server RESTRICT_ADMIN=1 on http://0.0.0.0:8765 ...
cd MAIN_AUTOMATION_TEST
set RESTRICT_ADMIN=1
set API_HOST=0.0.0.0
set API_PORT=8765
python -m api
