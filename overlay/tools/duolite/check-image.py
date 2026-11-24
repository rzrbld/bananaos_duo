#!/usr/bin/env python3
"""Verify a built SD image's GPT, FAT boot files, EFI kernel and native init."""
import argparse
import binascii
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import uuid

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--images', type=Path, required=True)
parser.add_argument('--tools', type=Path, required=True)
args = parser.parse_args()
base = args.images
source = Path(__file__).resolve().parents[2]
image = base / 'banana-duolite.img'
with image.open('rb') as f:
    size = image.stat().st_size
    f.seek(510); assert f.read(2) == b'\x55\xaa'
    f.seek(512); h = f.read(512)
    assert h[:8] == b'EFI PART'
    hdrsize, expected = struct.unpack_from('<II', h, 12)
    raw = bytearray(h[:hdrsize]); raw[16:20] = b'\0'*4
    assert binascii.crc32(raw) & 0xffffffff == expected
    current, backup, first, last = struct.unpack_from('<QQQQ', h, 24)
    assert current == 1 and backup == size//512 - 1
    offset, count, entrysize, expected = struct.unpack_from('<QIII', h, 72)
    f.seek(offset*512); entries = f.read(count*entrysize)
    assert binascii.crc32(entries) & 0xffffffff == expected
    parts = []
    for index in range(count):
        e = entries[index*entrysize:(index+1)*entrysize]
        if e[:16] == b'\0'*16:
            continue
        start, end, attrs = struct.unpack_from('<QQQ', e, 32)
        name = e[56:128].decode('utf-16-le').split('\0', 1)[0]
        assert first <= start <= end <= last
        parts.append((name, start, end, str(uuid.UUID(bytes_le=e[:16]))))
    assert [p[0] for p in parts] == ['boot', 'banana-root-a', 'banana-root-b']
    assert parts[0][3] == 'ebd0a0a2-b9e5-4433-87c0-68b6b72699c7'
    assert all(a[2] < b[1] for a,b in zip(parts, parts[1:]))
    f.seek(backup*512); h = f.read(512)
    assert h[:8] == b'EFI PART'
    expected = struct.unpack_from('<I', h, 16)[0]
    raw = bytearray(h[:hdrsize]); raw[16:20] = b'\0'*4
    assert binascii.crc32(raw) & 0xffffffff == expected
    for (_,start,end,_), name in zip(parts[:2], ['boot.vfat', 'rootfs.squashfs']):
        length = (base/name).stat().st_size
        with (base/name).open('rb') as reference:
            expected = hashlib.file_digest(reference, 'sha256').digest()
        f.seek(start*512); digest = hashlib.sha256()
        while length:
            data = f.read(min(length, 1024*1024)); assert data
            digest.update(data); length -= len(data)
        assert digest.digest() == expected
print('GPT headers, partition layout and embedded filesystems passed')

def command(name, *argv):
    return subprocess.check_output([str(args.tools/name), *map(str,argv)], stderr=subprocess.STDOUT)

boot = base/'boot.vfat'
entry = command('mtype', '-i', boot, '::/loader/entries/banana.conf')
assert entry == (base/'banana.conf').read_bytes()
assert b'devicetree /dtbs/qcom/sm6125-retroid-pocket-duo-lite.dtb' in entry
assert b'root=PARTLABEL=banana-root-a' in entry
with tempfile.TemporaryDirectory() as tmp:
    for remote, local in [('Image','Image'), ('dtbs/qcom/sm6125-retroid-pocket-duo-lite.dtb','sm6125-retroid-pocket-duo-lite.dtb')]:
        p = Path(tmp)/local
        command('mcopy', '-i', boot, '::/'+remote, p)
        assert p.read_bytes() == (base/local).read_bytes()
kernel = (base/'Image').read_bytes()
off = struct.unpack_from('<I',kernel,0x3c)[0]
assert kernel[:2] == b'MZ' and kernel[off:off+4] == b'PE\0\0'
assert struct.unpack_from('<H',kernel,off+4)[0] == 0xaa64
dtb = (base/'sm6125-retroid-pocket-duo-lite.dtb').read_bytes()
assert b'banana,quiet-max-pwm' in dtb
assert b'banana,emergency-cooling-state' in dtb
assert b'VA DMIC2' in dtb and b'VA_MCLK' in dtb and b'MIC BIAS1' in dtb
assert b'aux-devs' in dtb
assert b'banana,haptics' in dtb
assert b'TX SWR_INPUT2' in dtb and b'qcom,tx-channel-mapping' in dtb
openabl = source/'buildroot/board/duolite/openabl'
origin = json.loads((openabl.parent/'openabl-source.json').read_text())
assert origin['modified'] is False
with tempfile.TemporaryDirectory() as tmp:
    command('mcopy', '-s', '-i', boot, '::/openabl', tmp)
    copied = Path(tmp)/'openabl'
    assert {p.name for p in copied.iterdir()} == set(origin['files'])
    for name, sha in origin['files'].items():
        data = (copied/name).read_bytes()
        assert data == (openabl/name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == sha
print('Unmodified ROCKNIX OpenABL folder present on the FAT boot partition')
print('OpenABL boot entry, FAT kernel/DTB copies and ARM64 EFI header passed')

squash = base/'rootfs.squashfs'
import sys
subprocess.run([sys.executable, str(source/'tools/duolite/check-root-ownership.py'), str(squash), '--unsquashfs', str(args.tools/'unsquashfs')], check=True)
assert b'portmaster-duolite-ui' not in command('unsquashfs', '-l', squash)
def cat(name):
    return command('unsquashfs','-cat',squash,name)
assert cat('etc/banana/board').strip() == b'duolite'
assert cat('etc/banana/build') == b'Duo Lite ' + (source/'buildroot/board/duolite/BUILD').read_bytes().strip() + b'\n'
wifi = cat('usr/libexec/banana/wifi')
assert b'bgscan="simple:15:-70:1800"' in wifi
assert b'/data/banana/wifi-roaming' in wifi and b'bgscan=""' in wifi
import io, zipfile
with zipfile.ZipFile(io.BytesIO(cat('usr/share/slopetanium/seed.zip'))) as seed:
    assert seed.read('slopetanium/slopetanium-ui.aarch64')[:4] == b'\x7fELF'
    assert b'SLOP_TOP_ROTATION' in seed.read('slopetanium/slopetanium-ui.aarch64')
    assert b'SLOP_SELF_APPS_DIR' in seed.read('slopetanium/app/core.py')
    assert json.loads(seed.read('slopetanium/app/native-app.json'))['schema'] == 1
assert b'[slopetanium]' in cat('etc/banana/systems.conf')
assert b'[rocknixdsstore]' not in cat('etc/banana/systems.conf')
assert b'SLOP_SELF_APPS_DIR' in cat('usr/libexec/banana/run-slopetanium')
assert b'usr/bin/slopetanium-ui' not in command('unsquashfs', '-l', squash)
assert b'rocknixds-store-ui' not in command('unsquashfs', '-l', squash)
assert cat('etc/banana/release') == (source/'buildroot/board/duolite/RELEASE').read_bytes()
assert b'Microphone test' in cat('usr/bin/banana-ui')
assert b'Game vibration for emulators and compatible ports.' in cat('usr/bin/banana-ui')
for rel in ['usr/libexec/banana/duolite-audio', 'usr/libexec/banana/volume-duolite']:
    assert cat(rel) == (source/'system/rootfs'/rel).read_bytes(), rel
for name in ['RetroidPocketDuoLite.conf', 'HiFi-RetroidPocketDuoLite.conf']:
    assert cat('usr/share/alsa/ucm2/Qualcomm/sm6125/'+name) == (source/'buildroot/board/duolite/ucm2/Qualcomm/sm6125'/name).read_bytes(), name
for name in ['aplay', 'arecord']:
    assert cat('usr/bin/'+name).startswith(b'\x7fELF'), name
release = cat('usr/lib/os-release')
assert b'NAME="BananaOS"\n' in release
assert b'HW_DEVICE="Retroid Pocket Duo Lite"\n' in release
assert b'BANANA_SERIAL_MODESET=1' in cat('etc/banana/hardware.env')
assert b'banana-ui --panels-on' not in cat('etc/init.d/rcS')
assert b'BANANA_SERIAL_MODESET' in cat('usr/bin/banana-ui')
for rel in ['etc/init.d/rcS','etc/inittab', 'usr/libexec/banana/duolite-service',
            'usr/libexec/banana/duolite-import-network','usr/libexec/banana/duolite-log-watch',
            'usr/libexec/banana/duolite-early-log', 'usr/libexec/banana/duolite-clock']:
    assert cat(rel) == (source/'buildroot/board/duolite/rootfs'/rel).read_bytes(), rel
for rel in ['usr/libexec/banana/wifi','usr/libexec/banana/ssh','usr/libexec/banana/run-bananads',
            'usr/libexec/banana/run-nds','usr/libexec/banana/bluetooth','usr/libexec/banana/run-slopetanium',
            'usr/libexec/banana/slopetanium-portmaster-bootstrap','usr/libexec/banana/slopetanium-seed',
            'usr/libexec/banana/run-dodakvarter','usr/libexec/banana/run-activity','usr/libexec/banana/run-port','usr/libexec/banana/one-panel',
            'usr/libexec/banana/retroarch-duolite','usr/libexec/banana/run-retroarch',
            'usr/libexec/banana/update','usr/libexec/banana/update-duolite-boot',
            'usr/libexec/banana/run-retroarch-duolite','usr/libexec/banana/run-ps1',
            'usr/libexec/banana/port-keyboard',
            'usr/share/banana/portmaster/mod_BananaOS.txt','usr/share/banana/portmaster/gamecontrollerdb-duolite.txt',
            'usr/share/banana/portmaster/bin/python3',
            'usr/bin/banana-perf','etc/init.d/rcK']:
    assert cat(rel) == (source/'system/rootfs'/rel).read_bytes(),rel
assert cat('etc/banana/sleep.d/10-wifi') == (source/'system/rootfs/etc/banana/sleep.d/10-wifi').read_bytes()
for rel in ['usr/bin/banana-ui','usr/bin/bananads','usr/sbin/bananad','usr/bin/dodakvarter',
            'usr/bin/qrtr-ns','usr/bin/tqftpserv','usr/bin/rmtfs','usr/sbin/wpa_supplicant','usr/sbin/iw','usr/sbin/dropbear',
            'usr/bin/bluetoothctl','usr/bin/bluealsa','usr/bin/bluealsa-cli',
            'usr/bin/dbus-daemon','usr/libexec/bluetooth/bluetoothd',
            'usr/lib/alsa-lib/libasound_module_pcm_bluealsa.so']:
    assert cat(rel)[:4] == b'\x7fELF',rel
assert cat('etc/banana/stage').strip() == b'Alpha'
assert b'Duo Lite' in cat('etc/banana/build')
assert cat('usr/share/banana/rnds/icons/slopetanium.png').startswith(b'\x89PNG\r\n\x1a\n')
assert b'--top-width' in cat('usr/bin/banana-ui')
assert b'--top-rotation' in cat('usr/bin/banana-activity')
assert b'SDL_BANANA_TOP_ROTATION' in cat('usr/lib/libSDL2-2.0.so.0')
assert b'ID_INPUT_JOYSTICK' in cat('etc/udev/rules.d/99-duolite-gamepad.rules')
assert cat('usr/bin/retroarch') == cat('usr/libexec/banana/retroarch-duolite')
assert cat('usr/libexec/banana/retroarch.real')[:4] == b'\x7fELF'
assert cat('usr/share/banana/duolite/retroarch.cfg') == (source/'buildroot/board/duolite/retroarch.cfg').read_bytes()
for lib in ['libSDL2_image-2.0.so.0','libSDL2_ttf-2.0.so.0','libSDL2_mixer-2.0.so.0']:
    assert cat('usr/lib/' + lib)[:4] == b'\x7fELF', lib
assert cat('usr/lib/libpng16.so.16')[:4] == b'\x7fELF'
# SDL_image may use its embedded PNG decoder rather than libpng symbols.
assert b'Not a PNG' in cat('usr/lib/libSDL2_image-2.0.so.0')
for lib in ['libopenal.so.1', 'libvorbisfile.so.3', 'libtheoradec.so.1', 'libmpg123.so.0']:
    assert cat('usr/lib/' + lib)[:4] == b'\x7fELF', lib
assert cat('usr/lib/libsqlite3.so.0')[:4] == b'\x7fELF'
assert cat('usr/libexec/ksmbd.tools')[:4] == b'\x7fELF'
assert b'ksmbd.mountd -> /usr/libexec/ksmbd.tools' in command('unsquashfs', '-ll', squash, 'usr/sbin/ksmbd.mountd')
assert b'/lib-dynload/_sqlite3.' in command('unsquashfs', '-ll', squash)
assert b'Slopetanium.app' in command('unsquashfs', '-l', squash, 'usr/share/banana/apps/slopetanium')

def config(name):
    result = {}
    for line in cat(name).decode().splitlines():
        if line.startswith('#') or '=' not in line: continue
        key,value = line.split('=',1); result[key.strip()] = value.strip()
    return result
power = config('etc/banana/bananad.conf')
assert power['led_mode'] == 'charging' and power['fan_profile'] == 'auto'
assert power['poweroff_after_sleep_minutes'] == '30'
assert config('etc/banana/settings.conf')['nds_emulator'] == 'bananads'
assert config('etc/banana/settings.conf')['ssh'] == 'on'
assert config('etc/banana/settings.conf')['bluetooth'] == 'off'
assert b'blacklist hci_uart' in cat('etc/modprobe.d/duolite-bluetooth.conf')
assert cat('lib/firmware/qca/cmbtfw13.tlv')
assert cat('lib/firmware/qca/retroid-duolite/cmnv13.bin')
import crypt
root_hash = next(line.split(':')[1] for line in cat('etc/shadow').decode().splitlines() if line.startswith('root:'))
assert crypt.crypt('rocknix',root_hash) == root_hash
hashes = (source/'buildroot/package/qcom-adreno-firmware/qcom-adreno-firmware.hash').read_text().splitlines()
expected_fw = next(line.split()[1] for line in hashes if line.split()[-1:] == ['a630_sqe.fw'])
assert hashlib.sha256(cat('lib/firmware/qcom/a630_sqe.fw')).hexdigest() == expected_fw
assert cat('etc/banana/release').strip() == (source/'buildroot/board/duolite/RELEASE').read_bytes().strip()
assert b'api.github.com/repos/rzrbld/bananaos_duo/releases' in cat('usr/libexec/banana/update')
print('Packaged native init, networking, logs, executables and power defaults passed')

# Every native system's default emulator must actually be shipped.
for core in ['gpsp','mgba','gambatte','fceumm','banananes','snes9x','picodrive','vice_x64sc','fuse','pcsx_rearmed','mupen64plus_next','fake08',
             'citra','ppsspp','flycast','genesis_plus_gx','mame2003_plus','cap32','dolphin']:
    blob = cat('usr/lib/libretro/' + core + '_libretro.so')
    assert blob[:4] == b'\x7fELF' and int.from_bytes(blob[18:20], 'little') == 183, core
print('Native ARM64 emulator cores present')

import configparser
systems = configparser.ConfigParser(interpolation=None)
systems.read_string(cat('etc/banana/systems.conf').decode())
for system, core in [('3ds','citra'), ('psp','ppsspp'), ('dreamcast','flycast'),
                     ('mastersystem','genesis_plus_gx'), ('mame','mame2003_plus'),
                     ('amstradcpc','cap32'), ('wii','dolphin')]:
    assert systems[system]['always'].strip() == 'yes', system
    assert systems[system]['run'].strip() == '/usr/libexec/banana/run-retroarch ' + core + ' %ROM%', system
for core in ['ppsspp','dolphin']:
    rel = 'usr/share/banana/duolite/cores/' + core + '_libretro.so.cfg'
    assert cat(rel) == (source/'buildroot/board/duolite/rootfs'/rel).read_bytes(), rel
for asset in ['PPSSPP/compat.ini', 'PPSSPP/flash0/font/ltn0.pgf',
              'dolphin-emu/Sys/GC/font_western.bin']:
    assert cat('usr/share/banana/duolite/system/' + asset), asset
listing = command('unsquashfs', '-l', squash)
for test_rom in [b'2048-port-3ds.3dsx', b'EBOOT.PBP', b'gravity-wave.cdi',
                 b'2048sanqui.sms', b'gridlee.zip', b'tv2024.dsk', b'tetwiis.dol']:
    assert test_rom not in listing, test_rom
print('Seven new systems visible without ROMs; official emulator assets present; test ROMs excluded')

assert cat('usr/share/libretro/autoconfig/sdl2/retroid-duolite.cfg') == (source/'buildroot/board/duolite/retroid-sdl2.cfg').read_bytes()
assert b'BANANA_NATIVE_MENU_ROTATION' in cat('usr/libexec/banana/retroarch.real')
assert b'[menu] open' in cat('usr/bin/banana-ui')
assert b'BANANA_MENU' in cat('usr/libexec/banana/retroarch.real')
assert cat('usr/share/banana/licenses/original-menu/UPSTREAM.json') == (source/'ui/third_party/banana_menu/UPSTREAM.json').read_bytes()
print('Original BananaOS menu, emulator bridge and rotated fallback packaged')
