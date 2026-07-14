#!/bin/bash
set -e

# Allow running with read only root
# Define a local runtime directory inside the container
export XDG_CONFIG_HOME=/tmp/.chromium
export XDG_CACHE_HOME=/tmp/.chromium
export XDG_RUNTIME_DIR=/tmp/kiosk-runtime

# Ensure the directory exists and has the correct restrictive permissions required by Wayland
mkdir -p "$XDG_CONFIG_HOME"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
# -------------------------------------

URL="${KIOSK_URL:-https://sy-zero.com/}"


CAGE_PID=""
VNC_PID=""

cleanup() {
    echo "Received termination signal. Shutting down kiosk..."

    # Terminate VNC Server
    if [ -n "$VNC_PID" ]; then
        echo "Stopping VNC Server (PID $VNC_PID)..."
        kill -TERM "$VNC_PID" 2>/dev/null
    fi

    # Terminate Cage/Chromium
    if [ -n "$CAGE_PID" ]; then
        echo "Stopping Cage/Chromium (PID $CAGE_PID)..."
        kill -TERM "$CAGE_PID" 2>/dev/null
    fi

    # Wait briefly for them to die
    wait "$CAGE_PID" 2>/dev/null
    wait "$VNC_PID" 2>/dev/null
    echo "Kiosk cleanup complete. Exiting cleanly."
    exit 0
}

trap cleanup SIGTERM SIGINT

start_vnc() {
    # Wait until the Cage compositor creates the Wayland display socket
    echo "Waiting for Wayland socket..."
    while [ ! -S "$XDG_RUNTIME_DIR/wayland-0" ]; do
        sleep 0.5
    done

    echo "Wayland socket detected. Starting VNC Server on port 5900..."
    # Bind wayvnc to all interfaces (0.0.0.0) so it's accessible externally
    export WAYLAND_DISPLAY=wayland-0
    exec wayvnc 0.0.0.0 5900 > /tmp/wayvnc.log 2>&1 &
    VNC_PID=$!
}

# Run the VNC monitor loop in the background so we can start cage
start_vnc &

echo "Initializing Wayland Kiosk Server..."
echo "Target URL: $URL"

# Make sure it does not try to call home
export GOOGLE_API_KEY="no"
export GOOGLE_DEFAULT_CLIENT_ID="no"
export GOOGLE_DEFAULT_CLIENT_SECRET="no"
export DBUS_SESSION_BUS_ADDRESS="/dev/null"


CHROME_FLAGS="--ozone-platform=wayland \
              --kiosk \
              --no-sandbox \
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
              --disable-features=Dbus,GCM,Translate,OptimizationHints \
              --disable-background-networking \
              --disable-sync \
              --gcm-registration-url=http://127.0.0.1:1"

exec cage -- chromium $CHROME_FLAGS "$URL" &
CAGE_PID=$!

# Wait on the Cage process (this keeps the script running)
wait "$CAGE_PID"
cleanup