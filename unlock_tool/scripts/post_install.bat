@echo off
set ROOT_DIR=%~dp0..\
echo Running post-install checks for Unlock Tool...
if "%OS%"=="Windows_NT" (
    echo Please install Zadig and the Google USB driver if you are connecting Android devices.
    echo For libimobiledevice support install the latest Windows binaries and add them to PATH.
    echo For iOS and checkra1n support, use a macOS or Linux machine instead.
) else (
    echo Unsupported platform for this script.
)
