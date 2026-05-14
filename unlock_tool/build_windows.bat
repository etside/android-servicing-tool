@echo off
REM Windows Build Script for Unlock Tool (Batch Version)
REM Run this on Windows to create the portable executable

echo Building Unlock Tool for Windows...
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo Error: main.py not found. Please run this script from the unlock_tool directory.
    pause
    exit /b 1
)

REM Check if portable Python exists
set PYTHON_PATH=.\portable_python\windows\python\python.exe
if not exist "%PYTHON_PATH%" (
    echo Error: Portable Python not found at %PYTHON_PATH%
    pause
    exit /b 1
)

REM Install PyInstaller if not present
echo Installing PyInstaller...
"%PYTHON_PATH%" -m pip install pyinstaller --quiet

REM Build the frontend first
echo Building frontend...
if exist "package.json" (
    if exist "node_modules" (
        call npm run build
    ) else (
        echo Warning: Node modules not found, skipping frontend build
    )
)

REM Check if build_windows.spec exists
if not exist "build_windows.spec" (
    echo Creating build_windows.spec...

    echo # -*- mode: python ; coding: utf-8 -*- > build_windows.spec
    echo import os >> build_windows.spec
    echo import sys >> build_windows.spec
    echo from pathlib import Path >> build_windows.spec
    echo. >> build_windows.spec
    echo ROOT_DIR = Path(os.getcwd()).resolve() >> build_windows.spec
    echo. >> build_windows.spec
    echo binaries = [] >> build_windows.spec
    echo datas = [ >> build_windows.spec
    echo     (str(ROOT_DIR / 'devices.json'), '.'), >> build_windows.spec
    echo     (str(ROOT_DIR / 'drivers'), 'drivers'), >> build_windows.spec
    echo     (str(ROOT_DIR / 'assets'), 'assets'), >> build_windows.spec
    echo     (str(ROOT_DIR / 'README.md'), '.'), >> build_windows.spec
    echo     (str(ROOT_DIR / 'EULA.txt'), '.'), >> build_windows.spec
    echo ] >> build_windows.spec
    echo. >> build_windows.spec
    echo # Windows-specific binaries >> build_windows.spec
    echo if sys.platform == 'win32': >> build_windows.spec
    echo     adb = ROOT_DIR / 'platform-tools' / 'adb.exe' >> build_windows.spec
    echo     fastboot = ROOT_DIR / 'platform-tools' / 'fastboot.exe' >> build_windows.spec
    echo     if adb.exists(): >> build_windows.spec
    echo     binaries.append((str(adb), '.')) >> build_windows.spec
    echo     if fastboot.exists(): >> build_windows.spec
    echo     binaries.append((str(fastboot), '.')) >> build_windows.spec
    echo. >> build_windows.spec
    echo hidden_imports = [ >> build_windows.spec
    echo     'PyQt6.QtCore', >> build_windows.spec
    echo     'PyQt6.QtGui', >> build_windows.spec
    echo     'PyQt6.QtWidgets', >> build_windows.spec
    echo     'usb.core', >> build_windows.spec
    echo     'usb.util', >> build_windows.spec
    echo     'serial', >> build_windows.spec
    echo     'serial.tools.list_ports', >> build_windows.spec
    echo ] >> build_windows.spec
    echo. >> build_windows.spec
    echo block_cipher = None >> build_windows.spec
    echo. >> build_windows.spec
    echo a = Analysis( >> build_windows.spec
    echo     ['main.py'], >> build_windows.spec
    echo     pathex=[str(ROOT_DIR)], >> build_windows.spec
    echo     binaries=binaries, >> build_windows.spec
    echo     datas=datas, >> build_windows.spec
    echo     hiddenimports=hidden_imports, >> build_windows.spec
    echo     hookspath=[], >> build_windows.spec
    echo     hooksconfig={}, >> build_windows.spec
    echo     runtime_hooks=[], >> build_windows.spec
    echo     excludes=[], >> build_windows.spec
    echo     win_no_prefer_redirects=False, >> build_windows.spec
    echo     win_private_assemblies=False, >> build_windows.spec
    echo     cipher=block_cipher, >> build_windows.spec
    echo     noarchive=False, >> build_windows.spec
    echo ) >> build_windows.spec
    echo. >> build_windows.spec
    echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher) >> build_windows.spec
    echo. >> build_windows.spec
    echo exe = EXE( >> build_windows.spec
    echo     pyz, >> build_windows.spec
    echo     a.scripts, >> build_windows.spec
    echo     a.binaries, >> build_windows.spec
    echo     a.zipfiles, >> build_windows.spec
    echo     a.datas, >> build_windows.spec
    echo     [], >> build_windows.spec
    echo     name='unlock_tool', >> build_windows.spec
    echo     debug=False, >> build_windows.spec
    echo     bootloader_ignore_signals=False, >> build_windows.spec
    echo     strip=False, >> build_windows.spec
    echo     upx=True, >> build_windows.spec
    echo     upx_exclude=[], >> build_windows.spec
    echo     runtime_tmpdir=None, >> build_windows.spec
    echo     console=False, >> build_windows.spec
    echo     disable_windowed_traceback=False, >> build_windows.spec
    echo     argv_emulation=False, >> build_windows.spec
    echo     target_arch=None, >> build_windows.spec
    echo     codesign_identity=None, >> build_windows.spec
    echo     entitlements_file=None, >> build_windows.spec
    echo     icon=None, >> build_windows.spec
    echo ) >> build_windows.spec
)

REM Run PyInstaller
echo Running PyInstaller...
"%PYTHON_PATH%" -m pyinstaller build_windows.spec --clean --noconfirm

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!

    REM Create portable zip
    echo Creating portable zip...

    REM Get current date for filename
    for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set datetime=%%i
    set DATESTAMP=%datetime:~0,8%

    set ZIP_NAME=unlock_tool_windows_portable_%DATESTAMP%.zip

    if exist "dist\unlock_tool" (
        powershell "Compress-Archive -Path 'dist\unlock_tool\*' -DestinationPath '%ZIP_NAME%' -Force"

        REM Get file size
        for %%A in ("%ZIP_NAME%") do set SIZE=%%~zA
        set /a SIZE_MB=%SIZE%/1048576

        echo Portable zip created: %ZIP_NAME%
        echo Size: %SIZE_MB% MB
        echo.
        echo SUCCESS: Windows portable build completed!
    ) else (
        echo Error: dist\unlock_tool directory not found
    )
) else (
    echo.
    echo Build failed!
)

echo.
pause