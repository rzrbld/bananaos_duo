#!/usr/bin/env python3
"""Fail image assembly when essential Duo Lite network/debug files are missing."""
from pathlib import Path
import os
import sys

root = Path(sys.argv[1]).resolve()
required = [
    'usr/bin/qrtr-ns', 'usr/bin/tqftpserv', 'usr/bin/rmtfs',
    'usr/sbin/wpa_supplicant', 'usr/sbin/wpa_cli', 'usr/sbin/dropbear',
    'usr/bin/dropbearkey', 'usr/share/udhcpc/default.script',
    'usr/libexec/banana/wifi', 'usr/libexec/banana/ssh',
    'usr/libexec/banana/duolite-service', 'usr/libexec/banana/duolite-import-network',
    'usr/libexec/banana/duolite-log-watch', 'usr/libexec/banana/duolite-early-log', 'usr/libexec/banana/boot-log',
    'usr/bin/bluetoothctl', 'usr/bin/dbus-daemon', 'usr/bin/dbus-uuidgen',
    'usr/libexec/bluetooth/bluetoothd', 'usr/bin/bluealsa', 'usr/bin/bluealsa-cli',
    'lib/firmware/qca/cmbtfw13.tlv', 'lib/firmware/qca/retroid-duolite/cmnv13.bin',
    'lib/firmware/qcom/a630_sqe.fw',
    'lib/firmware/ath10k/WCN3990/hw1.0/retroid-duolite/board-2.bin',
    'lib/firmware/ath10k/WCN3990/hw1.0/retroid-duolite/firmware-5.bin',
    'lib/firmware/qcom/sm6125/modem.mbn',
    'lib/firmware/qcom/sm6125/adsp.mbn',
    'lib/firmware/qcom/sm6125/wlanmdsp.mbn',
]
errors = []
for rel in required:
    p = root / rel
    if not p.is_file() or p.stat().st_size == 0:
        errors.append('Missing or empty: ' + rel)
for rel, target in [('root/.ssh','/run/banana/ssh'),
                    ('etc/resolv.conf','../run/resolv.conf'),
                    ('var/lib/tqftpserv','/run/banana/tqftpserv'),
                    ('var/lib/bluetooth','/run/banana/bluetooth'),
                    ('var/lib/bluealsa','/run/banana/bluealsa')]:
    p = root / rel
    if not p.is_symlink() or os.readlink(p) != target:
        errors.append('Incorrect runtime symlink: ' + rel)
inittab = (root / 'etc/inittab').read_text()
for line in inittab.splitlines():
    if '::respawn:' in line and 'duolite-service' in line and line.split(':',1)[0]:
        errors.append('BusyBox service incorrectly names a terminal: ' + line)
for service in ['tqftpserv', 'rmtfs']:
    if 'duolite-service ' + service not in inittab:
        errors.append('Missing supervised service: ' + service)
for rel in ['etc/init.d/rcS', 'usr/libexec/banana/duolite-service',
            'usr/libexec/banana/duolite-log-watch', 'usr/libexec/banana/duolite-early-log', 'usr/libexec/banana/duolite-import-network']:
    if not os.access(root / rel, os.X_OK):
        errors.append('Not executable: ' + rel)
if errors:
    raise SystemExit('\n'.join(errors))
print('Duo Lite native network/debug root checks passed')
