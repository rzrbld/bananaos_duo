#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
python3 scripts/prepare.py
mkdir -p build/work
docker build -t banana-duolite-builder:bookworm -f build/source/tools/duolite/Dockerfile build/source
docker build -t banana-duolite-native-builder:bookworm -f build/source/tools/duolite/Dockerfile.native build/source
# Parallelism is configurable on smaller build machines.
JOBS=${JOBS:-4}
docker run --rm --user "$(id -u):$(id -g)" \
    -e CCACHE_MAXSIZE=2G \
    -v "$ROOT/build/source:/source:ro" -v "$ROOT/build/work:/work" \
    banana-duolite-native-builder:bookworm \
    /source/tools/duolite/build-native.sh "BR2_JLEVEL=$JOBS" "${@:-all}"
