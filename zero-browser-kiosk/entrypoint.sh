#!/bin/bash
set -e

# Allow running with read-only root
export XDG_CONFIG_HOME=/tmp/.chromium
export XDG_CACHE_HOME=/tmp/.chromium
export XDG_RUNTIME_DIR=/tmp/kiosk-runtime

# Ensure the directory exists and has correct restrictive permissions for Wayland
mkdir -p "$XDG_CONFIG_HOME"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"

URL="${KIOSK_URL:-https://sy-zero.com/}"

cleanup() {
    set +e
    echo "Received termination signal. Shutting down kiosk..."

    # Terminate Cage/Chromium and wayvnc gracefully first
    CAGE_PIDS=$(pgrep -x cage)
    VNC_PIDS=$(pgrep -x wayvnc)
    if [ -n "$CAGE_PIDS" ] || [ -n "$VNC_PIDS" ]; then
        echo "Stopping Cage and wayvnc..."
        kill -TERM $CAGE_PIDS $VNC_PIDS 2>/dev/null
        sleep 1
        kill -KILL $CAGE_PIDS $VNC_PIDS 2>/dev/null
    fi

    echo "Kiosk cleanup complete. Exiting cleanly."
    exit 0
}

# Trap SIGTERM (Kubernetes shutdown) and SIGINT
trap cleanup SIGTERM SIGINT

start_vnc() {
    # Wait until the Cage compositor creates the Wayland display socket
    echo "Waiting for Wayland socket..."
    while [ ! -S "$XDG_RUNTIME_DIR/wayland-0" ]; do
        sleep 0.5
    done

    # Give Cage a moment to bind protocols after creating socket
    sleep 1

    echo "Wayland socket detected. Starting VNC Server on port 5900..."
    export WAYLAND_DISPLAY=wayland-0

    if [ -n "${HEADLESS_RESOLUTION:-}" ]; then
        echo "Setting headless output to $HEADLESS_RESOLUTION..."
        wlr-randr --output HEADLESS-1 --custom-mode "$HEADLESS_RESOLUTION" \
            || echo "Warning: failed to set headless resolution; using default."
    fi

    wayvnc --disable-input 0.0.0.0 5900 > /tmp/wayvnc.log 2>&1
}

start_cage_chromium() {
    echo "Initializing Wayland Kiosk Server..."
    echo "Target URL: $URL"

    # Make sure it does not try to call home
    export GOOGLE_API_KEY="no"
    export GOOGLE_DEFAULT_CLIENT_ID="no"
    export GOOGLE_DEFAULT_CLIENT_SECRET="no"
    export DBUS_SESSION_BUS_ADDRESS="/dev/null"

    CHROME_FLAGS="--ozone-platform=wayland \
                --touch-events=enabled \
                --enable-touch-drag-drop \
                --kiosk \
                --no-sandbox \
                --no-first-run \
                --no-default-browser-check \
                --check-for-update-interval=31536000 \
                --disable-session-crashed-bubble \
                --noerrdialogs \
                --disable-infobars \
                --disable-dev-shm-usage \
                --autoplay-policy=no-user-gesture-required \
                --ignore-gpu-blocklist \
                --enable-zero-copy \
                --enable-gpu-rasterization \
                --use-gl=angle \
                --use-angle=gles \
                --disable-component-extensions-with-background-pages \
                --metrics-recording-only \
                --disable-default-apps \
                --disable-backgrounding-occluded-windows \
                --disable-renderer-backgrounding \
                --disable-background-timer-throttling \
                --disable-features=Dbus,GCM,Translate,TranslateUI,OptimizationHints \
                --disable-background-networking \
                --disable-sync \
                --force-dark-mode \
                --gcm-registration-url=http://127.0.0.1:1"

    # Filter stderr log clutter for GCM/Dbus
    cage -- chromium $CHROME_FLAGS "$URL" 2> >(grep -vE "google_apis/gcm|dbus/bus.cc|dbus/object_proxy.cc")
}

# Make sure udev events in the container are fired
/lib/systemd/systemd-udevd --daemon 2>/dev/null || true
udevadm trigger --action=add 2>/dev/null || true

# With a monitor attached, use cage's default DRM/KMS backend to drive the
# real screen (prod: zero). With none attached (singel/subzero), that backend
# can't find a CRTC and cage spins at ~100% CPU while wayvnc crashes on the
# zero-size output; fall back to wlroots' headless backend (a virtual output,
# still GPU-composited and served over VNC), sized to $HEADLESS_RESOLUTION.
#
# Detected from DRM connector state: -x avoids matching "disconnected", -s
# stays quiet on an empty glob. Uncertain -> headless (low-CPU + VNC, not a
# crash loop). Plug a monitor into a headless node and restart to drive it.
if grep -qxs connected /sys/class/drm/*/status; then
    echo "Physical display connected; using cage's default DRM backend."
else
    echo "No physical display connected; using wlroots headless backend (GPU / GLES2)."
    export WLR_BACKENDS=headless
    # GPU compositing on the DRM render node. Software (pixman + LIBGL_ALWAYS_
    # SOFTWARE) works but composites every frame on the CPU (~630m observed);
    # gles2 is what gets headless CPU near a node with a real display (~126m).
    # The wayvnc frame-capture segfault is a zero-size-output damage bug (it
    # also hits displays running gles2), so we address it by sizing the output
    # to $HEADLESS_RESOLUTION before wayvnc attaches, not by dropping the GPU.
    export WLR_RENDERER=gles2
    HEADLESS_RESOLUTION="1920x1080"
fi

start_vnc &
VNC_PID=$!
start_cage_chromium &
CAGE_PID=$!

wait $CAGE_PID $VNC_PID

cleanup
