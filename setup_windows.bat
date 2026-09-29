@echo off
setlocal
cd /d "%~dp0"

echo [Gester] Creating virtual environment...
py -m venv .venv
if errorlevel 1 goto :error

call .venv\Scripts\activate.bat

echo [Gester] Updating pip...
python -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [Gester] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 goto :error

echo [Gester] Downloading hand-tracking model...
python setup_model.py
if errorlevel 1 goto :error

echo.
echo Setup complete.
echo Run run_gester.bat to start the prototype.
pause
exit /b 0

:error
echo.
echo Setup failed. Read the error above and send it to ChatGPT if you want help debugging it.
pause
exit /b 1
