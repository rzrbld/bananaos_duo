#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
T=$1
# UCM creates merged mixer controls here; the immutable root must point into RAM.
mkdir -p "$T/var/lib"
rm -rf "$T/var/lib/alsa"
ln -s /run/banana/alsa "$T/var/lib/alsa"
# Remove the obsolete app-mutating helper from incremental builds too.
rm -f "$T/usr/libexec/banana/portmaster-duolite-ui"
mkdir -p "$T/etc/banana" "$T/data" "$T/boot" "$T/run" "$T/usr/share/banana/duolite"
cp "$HERE/../../../VERSION" "$T/etc/banana/version"
echo duolite > "$T/etc/banana/board"
echo Alpha > "$T/etc/banana/stage"
echo "Duo Lite $(cat "$HERE/BUILD")" > "$T/etc/banana/build"
cp "$HERE/RELEASE" "$T/etc/banana/release"
# Retire the old Store; preserve all user apps and PortMaster on /data.
rm -rf "$T/usr/share/banana/apps/store"
rm -f "$T/usr/bin/rocknixds-store-ui" "$T/usr/libexec/banana/run-store"
mkdir -p "$T/usr/share/libretro/autoconfig/sdl2"
cp "$HERE/retroid-sdl2.cfg" "$T/usr/share/libretro/autoconfig/sdl2/retroid-duolite.cfg"
if [ -f "$T/usr/bin/retroarch" ]; then
    python3 - "$T" <<'PY'
from pathlib import Path
import sys
t = Path(sys.argv[1])
binary = t / 'usr/bin/retroarch'
real = t / 'usr/libexec/banana/retroarch.real'
if binary.read_bytes()[:4] == b'\x7fELF':
    binary.replace(real)
assert real.read_bytes()[:4] == b'\x7fELF'
PY
    cp "$T/usr/libexec/banana/retroarch-duolite" "$T/usr/bin/retroarch"
fi
printf 'NAME="BananaOS"\nID=bananaos\nID_LIKE=buildroot\nVERSION="%s"\nHW_DEVICE="Retroid Pocket Duo Lite"\nPRETTY_NAME="BananaOS Duo Lite bring-up"\n' \
    "$(cat "$HERE/../../../VERSION")" > "$T/usr/lib/os-release"
ln -sfn ../usr/lib/os-release "$T/etc/os-release"
ln -sfn data/roms "$T/roms"

# Device defaults; user overrides remain in /data/banana/bananad.conf.
cat >> "$T/etc/banana/bananad.conf" <<'EOF'

# Duo Lite: illuminate only while plugged in (charging / off / battery).
led_mode = charging
fan_profile = auto
rumble = yes
# Save the game and shut down after 30 minutes asleep on battery.
poweroff_after_sleep_minutes = 30
EOF

# tqftpserv needs a writable scratch directory on the read-only root image.
mkdir -p "$T/var/lib"
rm -rf "$T/var/lib/tqftpserv"
ln -s /run/banana/tqftpserv "$T/var/lib/tqftpserv"
# Pairings are packed to the data card by the Bluetooth helper; BlueZ and
# bluez-alsa operate on writable RAM directories while the root stays read-only.
for name in bluetooth bluealsa; do
    rm -rf "$T/var/lib/$name"
    ln -s "/run/banana/$name" "$T/var/lib/$name"
done
# DHCP writes here through the standard /etc/resolv.conf symlink.
ln -sfn ../run/resolv.conf "$T/etc/resolv.conf"

# Initial native image uses the emulator display path already tested on Duo Lite.
sed -i 's/^ssh *=.*/ssh = on/' "$T/etc/banana/settings.conf"
sed -i 's/^nds_emulator *=.*/nds_emulator = bananads/' "$T/etc/banana/settings.conf"
python3 "$HERE/../../../tools/duolite/check-native-root.py" "$T"

# Preserve attribution for the original BananaOS in-game menu renderer.
mkdir -p "$T/usr/share/banana/licenses/original-menu"
cp "$HERE/../../../ui/third_party/banana_menu/COPYING" "$HERE/../../../ui/third_party/banana_menu/UPSTREAM.json" "$T/usr/share/banana/licenses/original-menu/"
