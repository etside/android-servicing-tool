@echo off
:: build_windows.bat  –  Build AndroidServicingTool for Windows x64
:: Run from:  <eTool folder>
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

set VENV=.build_venv_win
set DIST=dist\AndroidServicingTool
set ARCHIVE=AndroidServicingTool-windows-x64.zip

echo === Android Servicing Tool - Windows build ===

:: ── Python check ──────────────────────────────────────────────────────────────
python --version >nul 2>&1 || (
    echo ERROR: python not found. Install Python 3.9+ and add to PATH.
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo Python: %PYVER%

:: ── venv ──────────────────────────────────────────────────────────────────────
if exist "%VENV%" rmdir /s /q "%VENV%"
python -m venv "%VENV%"
call "%VENV%\Scripts\activate.bat"
python -m pip install --quiet --upgrade pip wheel

:: ── deps ──────────────────────────────────────────────────────────────────────
pip install --quiet ^
  PyQt6==6.7.1 ^
  pyinstaller==6.10.0 ^
  pyusb==1.3.1 ^
  pyserial==3.5 ^
  cryptography==43.0.3 ^
  pycryptodome==3.21.0 ^
  requests==2.32.3 ^
  psutil==6.1.0 ^
  packaging==24.2

:: ── build ─────────────────────────────────────────────────────────────────────
echo Building...
pyinstaller newui.spec --clean --noconfirm ^
  --workpath build\windows --distpath dist

:: ── verify ────────────────────────────────────────────────────────────────────
if not exist "%DIST%\AndroidServicingTool.exe" (
    echo ERROR: executable not found
    exit /b 1
)

:: ── zip ───────────────────────────────────────────────────────────────────────
powershell -Command "Compress-Archive -Path 'dist\AndroidServicingTool' -DestinationPath '%ARCHIVE%' -Force"

echo.
echo [OK] Build complete
echo     Executable : %DIST%\AndroidServicingTool.exe
echo     Archive    : %ARCHIVE%
