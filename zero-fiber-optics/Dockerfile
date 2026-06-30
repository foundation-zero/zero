FROM rust:1.88-bookworm AS builder

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
COPY src ./src

RUN cargo build --release --locked

FROM debian:bookworm-slim AS runtime

RUN apt-get update && \
  apt-get install -y --no-install-recommends ca-certificates && \
  rm -rf /var/lib/apt/lists/* && \
  groupadd -g 1001 app && \
  useradd -r -u 1001 -g app app

WORKDIR /app

COPY --from=builder /app/target/release/zero-fiber-optics /usr/local/bin/zero-fiber-optics
COPY --chown=1001:1001 example/config.xml /app/example/config.xml

USER 1001

ENTRYPOINT ["zero-fiber-optics"]
CMD ["/app/config.xml"]
