#!/bin/sh
# Run with the BananaLinux checkout at /source and a writable build area at /work.
set -eu
export HOME=/tmp/banana-build-home
mkdir -p "$HOME" /work/native /work/native-dl /work/native-ccache
if [ ! -f /work/native/.config ]; then
    make -C /source/.buildroot O=/work/native BR2_EXTERNAL=/source/buildroot \
        BR2_DL_DIR=/work/native-dl banana_duolite_defconfig
fi
[ "$#" -gt 0 ] || set -- all
# Check the emulator's complete patch chain before compiling the rest of the
# firmware. The normal all target then reuses its download/extraction stamps.
for target do
    if [ "$target" = all ]; then
        make -C /work/native BR2_DL_DIR=/work/native-dl BR2_CCACHE_DIR=/work/native-ccache bananads-patch
        break
    fi
done
exec make -C /work/native BR2_DL_DIR=/work/native-dl BR2_CCACHE_DIR=/work/native-ccache "$@"
