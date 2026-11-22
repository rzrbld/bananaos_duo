ARG BUILDER_BASE=debian:bookworm
FROM ${BUILDER_BASE}
RUN dpkg --add-architecture arm64 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        make gcc-aarch64-linux-gnu g++-aarch64-linux-gnu pkg-config \
        libfreetype6-dev:arm64 libdrm-dev:arm64 libasound2-dev:arm64 zlib1g-dev:arm64 \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update \
    && apt-get install -y --no-install-recommends git cmake ca-certificates \
    && rm -rf /var/lib/apt/lists/*
