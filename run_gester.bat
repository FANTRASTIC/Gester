@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Gester has not been set up yet.
  echo Run setup_windows.bat first.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
python main.py

if errorlevel 1 (
  echo.
  echo Gester exited with an error. Copy the error above if you need help debugging it.
  pause
)
