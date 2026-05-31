FROM rust:1.86 AS builder
WORKDIR /app
COPY backend/Cargo.toml ./
COPY backend/src ./src
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/target/release/poap_badge_api /usr/local/bin/poap_badge_api
EXPOSE 4000
ENV PORT=4000
CMD ["poap_badge_api"]
