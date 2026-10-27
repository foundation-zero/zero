FROM --platform=$BUILDPLATFORM rust:1.99.1-trixie@sha256:931c2c0531a8b143e044f0f3914dfe802f15bb3d1955f0b657e9359327ac2ffc AS builder

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
COPY src ./src

ARG TARGETARCH

RUN apt-get update && \
  if [ "$TARGETARCH" = "arm64" ]; then \
  apt-get install -y gcc-aarch64-linux-gnu && \
  rustup target add aarch64-unknown-linux-gnu; \
  elif [ "$TARGETARCH" = "amd64" ]; then \
  apt-get install -y gcc-x86-64-linux-gnu && \
  rustup target add x86_64-unknown-linux-gnu; \
  fi

ENV CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_LINKER=x86_64-linux-gnu-gcc
ENV CC_x86_64_unknown_linux_gnu=x86_64-linux-gnu-gcc
ENV CXX_x86_64_unknown_linux_gnu=x86_64-linux-gnu-g++

ENV CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-linux-gnu-gcc
ENV CC_aarch64_unknown_linux_gnu=aarch64-linux-gnu-gcc
ENV CXX_aarch64_unknown_linux_gnu=aarch64-linux-gnu-g++

RUN if [ "$TARGETARCH" = "arm64" ]; then \
  cargo build --release --target aarch64-unknown-linux-gnu && \
  cp target/aarch64-unknown-linux-gnu/release/zero-battery-cells /app/zero-battery-cells; \
  else \
  cargo build --release --target x86_64-unknown-linux-gnu && \
  cp target/x86_64-unknown-linux-gnu/release/zero-battery-cells /app/zero-battery-cells; \
  fi

FROM debian:trixie-slim@sha256:62bd423aeee912639ca8ee681c2b762cb3e25137e0a92b20be455898a9f034ad AS runtime

RUN apt-get update && \
  apt-get install -y --no-install-recommends ca-certificates && \
  rm -rf /var/lib/apt/lists/* && \
  groupadd -g 1001 app && \
  useradd -r -u 1001 -g app app

WORKDIR /app

COPY --from=builder /app/zero-battery-cells /usr/local/bin/zero-battery-cells
COPY --chown=1001:1001 spec/KEB6_FOX_05_41_1_NVL_Declaration.txt /app/spec/KEB6_FOX_05_41_1_NVL_Declaration.txt

USER 1001

ENTRYPOINT ["zero-battery-cells"]
