FROM --platform=$BUILDPLATFORM rust:1.99-trixie@sha256:8a4e90c7946b74626488b1446f712c0fe0ed1a596cbd3d871684bc9c5433ae07 AS builder

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

COPY zero-fiber-optics/Cargo.toml zero-fiber-optics/Cargo.lock ./
COPY zero-fiber-optics/src ./src

# Cargo.toml points at ../packages/rust/zero-readiness, which is /packages from /app.
RUN --mount=type=bind,source=packages/rust,target=/packages/rust \
  if [ "$TARGETARCH" = "arm64" ]; then \
  cargo build --release --target aarch64-unknown-linux-gnu && \
  cp target/aarch64-unknown-linux-gnu/release/zero-fiber-optics /app/zero-fiber-optics; \
  else \
  cargo build --release --target x86_64-unknown-linux-gnu && \
  cp target/x86_64-unknown-linux-gnu/release/zero-fiber-optics /app/zero-fiber-optics; \
  fi

FROM debian:trixie-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2 AS runtime

RUN apt-get update && \
  apt-get install -y --no-install-recommends ca-certificates && \
  rm -rf /var/lib/apt/lists/* && \
  groupadd -g 1001 app && \
  useradd -r -u 1001 -g app app

WORKDIR /app

COPY --from=builder /app/zero-fiber-optics /usr/local/bin/zero-fiber-optics
COPY --chown=1001:1001 zero-fiber-optics/example/config.xml /app/example/config.xml
COPY --chown=1001:1001 zero-fiber-optics/config.xml /app/config.xml

USER 1001

ENTRYPOINT ["zero-fiber-optics"]
CMD ["/app/config.xml"]
