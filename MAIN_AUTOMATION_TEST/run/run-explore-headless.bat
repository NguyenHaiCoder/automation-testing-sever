@echo off
setlocal

cd /d "%~dp0\.."
set "PYTHONIOENCODING=utf-8"

set "PY=python"
where python >nul 2>&1 || set "PY=py"

echo [RUN] explore headless...
"%PY%" "%CD%\explore_checklist.py" --headless
pause
