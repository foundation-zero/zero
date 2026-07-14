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


start_vnc() {
    # Wait until the Cage compositor creates the Wayland display socket
    echo "Waiting for Wayland socket..."
    while [ ! -S "$XDG_RUNTIME_DIR/wayland-0" ]; do
        sleep 0.5
    done

    echo "Wayland socket detected. Starting VNC Server on port 5900..."
    # Bind wayvnc to all interfaces (0.0.0.0) so it's accessible externally
    export WAYLAND_DISPLAY=wayland-0
    exec wayvnc 0.0.0.0 5900 > /tmp/wayvnc.log 2>&1
}

# Run the VNC monitor loop in the background so we can start cage
start_vnc &

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
