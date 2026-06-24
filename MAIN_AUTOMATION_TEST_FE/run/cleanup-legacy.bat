@echo off
cd /d "%~dp0\.."
if exist server (
  echo [CLEANUP] Removing legacy server\ ...
  rmdir /s /q server 2>nul
  if exist server (
    echo [WARN] Cannot remove server\ - close Cursor/terminal using this folder and run again.
    exit /b 1
  )
)
if exist data (
  echo [CLEANUP] Removing legacy data\ ...
  rmdir /s /q data 2>nul
)
echo [OK] Legacy folders removed.
exit /b 0
