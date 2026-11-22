#!/usr/bin/env python3
"""Import the pinned Duo Lite kernel support into the native board directory."""
from pathlib import Path
import shutil
import subprocess
import sys

PIN = '21d9dc6759cc3016c2e2e7244574c0e6a5a6bcd8'
banana = Path(__file__).resolve().parents[2]
rocknix = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else banana.parent / 'distribution'
if subprocess.check_output(['git', '-C', str(rocknix), 'rev-parse', 'HEAD'], text=True).strip() != PIN:
    raise SystemExit('ROCKNIX checkout does not match the pinned revision')
board = banana / 'buildroot/board/duolite'
patches = board / 'linux-patches'
patches.mkdir(parents=True, exist_ok=True)
device = Path('projects/ROCKNIX/devices/SM6115')
# Generic/version fixes precede the device patches (scripts/unpack applies
# the device's patch directory last). Device QSEED tuning depends on rotation fixes.
groups = ['projects/ROCKNIX/packages/linux/patches/mainline',
          'packages/linux/patches/default', 'projects/ROCKNIX/packages/linux/patches/7.3',
          str(device / 'patches/linux')]
for old in patches.glob('*.patch'):
    old.unlink()
count = 0
for index, group in enumerate(groups, 1):
    for source in sorted((rocknix / group).glob('*.patch')):
        shutil.copyfile(source, patches / f'{index}-{source.name}')
        count += 1
shutil.copyfile(rocknix / device / 'linux/linux.aarch64.conf', board / 'linux-rocknix.config')
(board / 'dts').mkdir(exist_ok=True)
shutil.copyfile(rocknix / device / 'linux/dts/qcom/sm6125-retroid-pocket-duo-lite.dts',
                board / 'dts/sm6125-retroid-pocket-duo-lite.dts')
(board / 'SOURCES').write_text(f'repository=https://github.com/ROCKNIX/distribution\ncommit={PIN}\nlinux=7.3.5\npatches={count}\n')
print(f'Imported {count} kernel patches, the Duo Lite device tree and kernel config')
