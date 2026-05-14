@echo off
setlocal enabledelayedexpansion
set ROOT_DIR=%~dp0..\
set KEYSTORE=%ROOT_DIR%\android_admin_apk\release.keystore
set ALIAS=unlock_tool_release
set APK_PATH=%ROOT_DIR%\android_admin_apk\app\build\outputs\apk\release\app-release-unsigned.apk
set SIGNED_APK=%ROOT_DIR%\android_admin_apk\app\build\outputs\apk\release\app-release-signed.apk
set ALIGNED_APK=%ROOT_DIR%\android_admin_apk\app\build\outputs\apk\release\app-release-aligned.apk

REM Find Android SDK path
if "%ANDROID_SDK_ROOT%"=="" (
    if exist "%USERPROFILE%\Android\Sdk" (
        set ANDROID_SDK_ROOT=%USERPROFILE%\Android\Sdk
    ) else (
        echo ERROR: ANDROID_SDK_ROOT not set and no Android SDK found at default location
        exit /b 1
    )
)

REM Find apksigner in build-tools
for /d %%D in ("%ANDROID_SDK_ROOT%\build-tools\*") do (
    if exist "%%D\apksigner.bat" (
        set APKSIGNER=%%D\apksigner.bat
    ) else if exist "%%D\apksigner.exe" (
        set APKSIGNER=%%D\apksigner.exe
    )
)

REM Find zipalign in build-tools
for /d %%D in ("%ANDROID_SDK_ROOT%\build-tools\*") do (
    if exist "%%D\zipalign.exe" (
        set ZIPALIGN=%%D\zipalign.exe
    )
)

if "!APKSIGNER!"=="" (
    echo ERROR: apksigner not found in %ANDROID_SDK_ROOT%\build-tools
    exit /b 1
)

if "!ZIPALIGN!"=="" (
    echo ERROR: zipalign not found in %ANDROID_SDK_ROOT%\build-tools
    exit /b 1
)

if not exist "%KEYSTORE%" (
    echo Creating new keystore at %KEYSTORE%
    keytool -genkeypair -v -keystore "%KEYSTORE%" -alias "%ALIAS%" -keyalg RSA -keysize 2048 -validity 3650 ^
        -dname "CN=Unlock Tool, OU=Dev, O=YourCompany, L=Local, S=State, C=US" -storepass changeit -keypass changeit
)

echo Building release APK...
pushd "%ROOT_DIR%\android_admin_apk"
call gradlew assembleRelease
popd

if not exist "%APK_PATH%" (
    echo Release APK not found at %APK_PATH%
    exit /b 1
)

echo Aligning unsigned APK with zipalign...
del /f /q "%ALIGNED_APK%" 2>nul || rem
call "!ZIPALIGN!" -v -p 4 "%APK_PATH%" "%ALIGNED_APK%"
if errorlevel 1 (
    echo ERROR: zipalign failed
    exit /b 1
)

echo Signing aligned APK with apksigner...
del /f /q "%SIGNED_APK%" 2>nul || rem
call "!APKSIGNER!" sign --ks "%KEYSTORE%" --ks-key-alias "%ALIAS%" --ks-pass pass:changeit --key-pass pass:changeit --out "%SIGNED_APK%" "%ALIGNED_APK%"

echo Verifying signed APK...
call "!APKSIGNER!" verify "%SIGNED_APK%"

echo Release APK signed and aligned: %SIGNED_APK%
dir "%SIGNED_APK%"
