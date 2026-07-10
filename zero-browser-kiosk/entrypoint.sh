#!/bin/bash
set -e

# --- FIX FOR XDG_RUNTIME_DIR ERROR ---
# Define a local runtime directory inside the container
export XDG_RUNTIME_DIR=/tmp/kiosk-runtime
# Ensure the directory exists and has the correct restrictive permissions required by Wayland
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
# -------------------------------------

URL="${KIOSK_URL:-https://sy-zero.com/}"

echo "Initializing Wayland Kiosk Server..."
echo "Target URL: $URL"

CHROME_FLAGS="--ozone-platform=wayland \
              --kiosk \
              --no-first-run \
              --noerrdialogs \
              --disable-infobars \
              --disable-dev-shm-usage \
              --autoplay-policy=no-user-gesture-required \
              --ignore-gpu-blocklist \
              --enable-zero-copy \
              --enable-gpu-rasterization \
              --use-gl=angle \
              --use-angle=gles \
              --disable-features=Dbus"

exec cage -- chromium $CHROME_FLAGS "$URL"
