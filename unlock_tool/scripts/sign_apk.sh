#!/usr/bin/env bash
set -e
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
KEYSTORE="$ROOT_DIR/android_admin_apk/release.keystore"
ALIAS="unlock_tool_release"
APK_PATH="$ROOT_DIR/android_admin_apk/app/build/outputs/apk/release/app-release-unsigned.apk"
ALIGNED_APK="$ROOT_DIR/android_admin_apk/app/build/outputs/apk/release/app-release-aligned.apk"
SIGNED_APK="$ROOT_DIR/android_admin_apk/app/build/outputs/apk/release/app-release-signed.apk"

# Find apksigner and zipalign in Android SDK
ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}"
APKSIGNER=$(find "$ANDROID_SDK_ROOT/build-tools" -name "apksigner" -type f 2>/dev/null | sort -V | tail -1)
ZIPALIGN=$(find "$ANDROID_SDK_ROOT/build-tools" -name "zipalign" -type f 2>/dev/null | sort -V | tail -1)

if [ ! -f "$APKSIGNER" ]; then
  echo "ERROR: apksigner not found in Android SDK at $ANDROID_SDK_ROOT"
  echo "Please set ANDROID_SDK_ROOT environment variable or install Android SDK build-tools"
  exit 1
fi

if [ ! -f "$ZIPALIGN" ]; then
  echo "ERROR: zipalign not found in Android SDK at $ANDROID_SDK_ROOT"
  exit 1
fi

if [ ! -f "$KEYSTORE" ]; then
  echo "Creating new keystore at $KEYSTORE"
  keytool -genkeypair -v -keystore "$KEYSTORE" -alias "$ALIAS" -keyalg RSA -keysize 2048 -validity 3650 \
    -dname "CN=Unlock Tool, OU=Dev, O=YourCompany, L=Local, S=State, C=US" -storepass changeit -keypass changeit
fi

echo "Building release APK..."
cd "$ROOT_DIR/android_admin_apk"
./gradlew assembleRelease

if [ ! -f "$APK_PATH" ]; then
  echo "Release APK not found at $APK_PATH"
  exit 1
fi

echo "Aligning unsigned APK with zipalign..."
rm -f "$ALIGNED_APK"
if ! "$ZIPALIGN" -v -p 4 "$APK_PATH" "$ALIGNED_APK"; then
  echo "zipalign failed"
  exit 1
fi

echo "Signing aligned APK with apksigner..."
rm -f "$SIGNED_APK"
"$APKSIGNER" sign --ks "$KEYSTORE" --ks-key-alias "$ALIAS" --ks-pass pass:changeit --key-pass pass:changeit \
  --out "$SIGNED_APK" "$ALIGNED_APK"

echo "Verifying signed APK..."
"$APKSIGNER" verify "$SIGNED_APK"

echo "Release APK signed and aligned: $SIGNED_APK"

echo "Release APK signed and aligned: $ALIGNED_APK"
ls -lh "$ALIGNED_APK"
