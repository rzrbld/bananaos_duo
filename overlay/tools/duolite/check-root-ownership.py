#!/usr/bin/env python3
"""Reject root filesystems whose privileged startup files have host ownership."""
import argparse
from pathlib import Path
import subprocess

CRITICAL = {'', 'bin', 'bin/busybox', 'sbin', 'sbin/init',
            'etc/init.d/rcS', 'usr/bin/banana-ui-session'}

def check(listing):
    found = set()
    for line in listing.splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6 or '/' not in fields[1]:
            continue
        mode, owner = fields[:2]
        path = fields[5].split(' -> ', 1)[0]
        if path != 'squashfs-root' and not path.startswith('squashfs-root/'):
            continue
        uid, gid = map(int, owner.split('/'))
        rel = path.removeprefix('squashfs-root').lstrip('/')
        if rel in CRITICAL:
            assert (uid, gid) == (0, 0), f'Privileged startup path /{rel} is owned by {uid}:{gid}, expected 0:0; build using fakeroot'
            found.add(rel)
        if len(mode) > 3 and mode[3] in 'sS':
            assert uid == 0, f'Setuid file /{rel} would switch to UID {uid}, expected root'
    assert found == CRITICAL, 'Missing startup ownership metadata: '+str(sorted(CRITICAL-found))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--unsquashfs', default='unsquashfs')
    args = parser.parse_args()
    check(subprocess.check_output([args.unsquashfs, '-lln', str(args.image)], text=True))
    print('SquashFS privileged startup and setuid ownership passed')
