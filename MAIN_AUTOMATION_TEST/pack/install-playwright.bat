@echo off
setlocal
cd /d "%~dp0\.."
set "PYTHONUTF8=1"
set "PLAYWRIGHT_BROWSERS_PATH=%CD%\pack\ms-playwright"

echo Installing Chromium to pack\ms-playwright ...
python -m playwright install chromium
echo Done. Run pack\build-backend.bat to bundle.
