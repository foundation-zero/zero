FROM debian:trixie-slim@sha256:62bd423aeee912639ca8ee681c2b762cb3e25137e0a92b20be455898a9f034ad

RUN apt-get update && apt-get install -y --no-install-recommends \
    cage \
    chromium \
    libgl1-mesa-dri \
    mesa-vulkan-drivers \
    udev \
    procps\
    wayvnc \
    wlr-randr \
    evtest \
    libinput-tools \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
