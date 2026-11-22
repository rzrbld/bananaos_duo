#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cp "$HERE/banana.conf" "$BINARIES_DIR/banana.conf"
rm -rf "$BINARIES_DIR/openabl"
cp -a "$HERE/openabl" "$BINARIES_DIR/openabl"
rm -rf "$BUILD_DIR/genimage-duolite.tmp"
genimage --rootpath "$TARGET_DIR" --tmppath "$BUILD_DIR/genimage-duolite.tmp" \
    --inputpath "$BINARIES_DIR" --outputpath "$BINARIES_DIR" --config "$HERE/genimage.cfg"
gzip -kf6 "$BINARIES_DIR/banana-duolite.img"
( cd "$BINARIES_DIR" && sha256sum banana-duolite.img.gz > banana-duolite.img.gz.sha256 )
