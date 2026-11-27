FROM --platform=$BUILDPLATFORM rust:1.100.0-trixie@sha256:e84068000361bf3d4a5ba2b7647f62893528b1eb9f847d7a23b493f5ce8ea254 AS builder

WORKDIR /app

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

COPY zero-battery-cells/Cargo.toml zero-battery-cells/Cargo.lock ./
COPY zero-battery-cells/src ./src

# Cargo.toml points at ../packages/rust/zero-readiness, which is /packages from /app.
RUN --mount=type=bind,source=packages/rust,target=/packages/rust \
  if [ "$TARGETARCH" = "arm64" ]; then \
  cargo build --release --target aarch64-unknown-linux-gnu && \
  cp target/aarch64-unknown-linux-gnu/release/zero-battery-cells /app/zero-battery-cells; \
  else \
  cargo build --release --target x86_64-unknown-linux-gnu && \
  cp target/x86_64-unknown-linux-gnu/release/zero-battery-cells /app/zero-battery-cells; \
  fi

FROM debian:trixie-slim@sha256:8aa5a7bf5a1955bddbe7d74fcdd0b91ab30e74362a8b73af672b0481b35b44a0 AS runtime

RUN apt-get update && \
  apt-get install -y --no-install-recommends ca-certificates && \
  rm -rf /var/lib/apt/lists/* && \
  groupadd -g 1001 app && \
  useradd -r -u 1001 -g app app

WORKDIR /app

COPY --from=builder /app/zero-battery-cells /usr/local/bin/zero-battery-cells
COPY --chown=1001:1001 zero-battery-cells/spec/KEB6_FOX_05_41_1_NVL_Declaration.txt /app/spec/KEB6_FOX_05_41_1_NVL_Declaration.txt

USER 1001

ENTRYPOINT ["zero-battery-cells"]
