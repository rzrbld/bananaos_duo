#!/usr/bin/env python3
"""Read-only comparison of the active SD firmware against release image components."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FILES = ('Image', 'sm6125-retroid-pocket-duo-lite.dtb', 'rootfs.squashfs')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images', type=Path, required=True)
    p.add_argument('--host', required=True, help='SSH destination, for example root@DUO_IP')
    p.add_argument('--control-path', help='Existing SSH control socket, if available')
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    expected = {}
    for name in FILES:
        path = args.images / name
        with path.open('rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        expected[name] = {'size': path.stat().st_size, 'sha256': digest}
    with (args.images / 'rootfs.squashfs').open('rb') as f:
        header = f.read(96)
    assert header[:4] == b'hsqs', 'Not a SquashFS release payload'
    used = struct.unpack_from('<Q', header, 40)[0]
    assert 96 <= used <= expected['rootfs.squashfs']['size']
    version = (ROOT / 'VERSION').read_text().strip()
    remote = '''
from pathlib import Path
import hashlib,json,re,struct
expected=EXPECTED
rows=[line.split() for line in Path('/proc/self/mountinfo').read_text().splitlines()]
root=next(row for row in rows if row[4]=='/')
assert root[root.index('-')+1]=='squashfs', 'Active root is not immutable SquashFS'
device=Path('/sys/dev/block/'+root[2]).resolve().name
# Only read the removable SD layout used by this port, never Android's eMMC.
assert device in ('mmcblk0p2','mmcblk0p3'), 'Unexpected active root device: '+device
slot='a' if device.endswith('p2') else 'b'
assert 'root=PARTLABEL=banana-root-'+slot in Path('/proc/cmdline').read_text().split()
components={}
for name,info in expected.items():
    path=Path('/dev')/device if name=='rootfs.squashfs' else Path('/boot')/slot/name
    if name!='rootfs.squashfs':
        assert path.stat().st_size==info['size'], 'Boot component size mismatch: '+name
    h=hashlib.sha256();left=info['size']
    with path.open('rb') as f:
        if name=='rootfs.squashfs':
            header=f.read(96)
            assert header[:4]==b'hsqs'
            assert struct.unpack_from('<Q',header,40)[0]==USED
            f.seek(0)
        while left:
            block=f.read(min(left,1024*1024))
            assert block, 'Truncated installed component: '+name
            h.update(block);left-=len(block)
    components[name]={'size':info['size'],'sha256':h.hexdigest()}
# A matching image can still have a failed driver probe. Treat missing basic
# controls as a failed installed-firmware verification, including optional-FF boots.
inputs=Path('/proc/bus/input/devices').read_text()
pad=next((block for block in inputs.split('\\n\\n') if 'Retroid Pocket Duo Lite Gamepad' in block), '')
assert pad and 'event' in pad, 'Built-in gamepad did not register'
print(json.dumps({'gamepad_registered':True,'version':Path('/etc/banana/release').read_text().strip(),
                  'running_slot':slot,'components':components}))
'''.replace('EXPECTED', repr(expected)).replace('USED', str(used))
    command = ['ssh', '-F', '/dev/null', '-o', 'ConnectTimeout=10']
    if args.control_path:
        command += ['-S', args.control_path]
    command += [args.host, 'python3', '-']
    run = subprocess.run(command, input=remote, text=True, capture_output=True, check=True, timeout=180)
    installed = json.loads(run.stdout)
    assert installed['version'] == version, 'Installed version differs from release version'
    assert installed['components'] == expected, 'Installed firmware hashes differ from release components'
    installed.update({'verified': True, 'rootfs_bytes_used': used,
                      'verified_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                      'scope': 'Active kernel, device tree and complete SquashFS payload including image padding; user data excluded'})
    result = json.dumps(installed, indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    print(result, end='')


if __name__ == '__main__':
    main()
