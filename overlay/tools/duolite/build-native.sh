#!/bin/sh
# Run with the BananaLinux checkout at /source and a writable build area at /work.
set -eu
export HOME=/tmp/banana-build-home
mkdir -p "$HOME" /work/native /work/native-dl /work/native-ccache
if [ ! -f /work/native/.config ]; then
    make -C /source/.buildroot O=/work/native BR2_EXTERNAL=/source/buildroot \
        BR2_DL_DIR=/work/native-dl banana_duolite_defconfig
fi
exec make -C /work/native BR2_DL_DIR=/work/native-dl BR2_CCACHE_DIR=/work/native-ccache "${@:-all}"
