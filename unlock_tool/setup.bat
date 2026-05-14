@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHON=%SCRIPT_DIR%portable_python\windows\python\python.exe"

if not exist "%PYTHON%" (
    echo Portable Python not found at %PYTHON%
    pause
    exit /b 1
)

echo Upgrading pip and installing requirements...
"%PYTHON%" -m pip install --upgrade pip setuptools wheel
"%PYTHON%" -m pip install -r requirements.txt

echo Setup complete. You can now run run.bat --gui

endlocal