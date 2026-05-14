@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHON=%SCRIPT_DIR%portable_python\windows\python\python.exe"

if not exist "%PYTHON%" (
    echo Portable Python not found at %PYTHON%
    pause
    exit /b 1
)

rem Add platform-tools to PATH
set "PATH=%SCRIPT_DIR%platform-tools;%PATH%"

rem Run the tool
"%PYTHON%" main.py %*

endlocal