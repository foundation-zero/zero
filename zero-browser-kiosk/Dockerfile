FROM debian:trixie-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    cage \
    chromium \
    libgl1-mesa-dri \
    mesa-vulkan-drivers \
    udev \
    procps\
    wayvnc \
    inotify-tools \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
