@echo off
setlocal enabledelayedexpansion
set ROOT_DIR=%~dp0
if not exist "%ROOT_DIR%.venv\Scripts\python.exe" (
    echo Creating portable Python virtual environment...
    python -m venv "%ROOT_DIR%.venv"
    call "%ROOT_DIR%.venv\Scripts\python.exe" -m pip install --upgrade pip
    call "%ROOT_DIR%.venv\Scripts\python.exe" -m pip install -r "%ROOT_DIR%\requirements.txt"
)
call "%ROOT_DIR%.venv\Scripts\python.exe" "%ROOT_DIR%\main.py" --gui
