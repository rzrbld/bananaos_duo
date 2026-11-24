#!/usr/bin/env python3
"""Exercise real SquashFS metadata for valid and host-owned startup trees."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
checker = root/'overlay/tools/duolite/check-root-ownership.py'
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp); tree = tmp/'root'
    for name in ('bin/busybox', 'etc/init.d/rcS', 'usr/bin/banana-ui-session'):
        p = tree/name; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('#!/bin/sh\n'); p.chmod(0o755)
    (tree/'bin/busybox').chmod(0o4755)
    (tree/'sbin').mkdir(); (tree/'sbin/init').symlink_to('../bin/busybox')
    for uid in (0, 1000):
        image = tmp/f'{uid}.squashfs'
        subprocess.run(['mksquashfs', str(tree), str(image), '-noappend', '-no-progress', '-processors', '1', '-force-uid', str(uid), '-force-gid', str(uid)], check=True, stdout=subprocess.DEVNULL)
        result = subprocess.run([sys.executable, str(checker), str(image)], capture_output=True, text=True)
        assert (result.returncode == 0) == (uid == 0), result.stdout+result.stderr
        if uid == 1000: assert 'expected 0:0' in result.stderr
print('PASS: real SquashFS root ownership accepted; host-owned setuid startup rejected')
