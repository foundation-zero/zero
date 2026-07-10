FROM debian:trixie-slim

# Install system dependencies for Wayland rendering and hardware communication
RUN apt-get update && apt-get install -y --no-install-recommends \
    cage \
    chromium \
    libgl1-mesa-dri \
    mesa-vulkan-drivers \
    udev \
    && rm -rf /var/lib/apt/lists/*

# Copy and set execution permissions for the startup script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
