#!/usr/bin/env python3
"""Assemble pinned upstream sources, fetched menu files and the Duo Lite port."""
import hashlib
import json
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'build/source'
PINS = json.loads((ROOT / 'sources.json').read_text())

def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

def fingerprint():
    h = hashlib.sha256()
    files = [ROOT/'sources.json', ROOT/'scripts/prepare.py']
    for folder in ('patches', 'overlay'):
        files += sorted(p for p in (ROOT/folder).rglob('*') if p.is_file() or p.is_symlink())
    for p in files:
        h.update(str(p.relative_to(ROOT)).encode())
        h.update(str(p.lstat().st_mode & 0o777).encode())
        h.update(str(p.readlink()).encode() if p.is_symlink() else p.read_bytes())
    return h.hexdigest()

def prepare():
    for name, pin in [('BananaLinux', PINS['BananaLinux']), ('buildroot', PINS['Buildroot'])]:
        path = ROOT/'upstream'/name
        actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != pin['commit']:
            raise SystemExit(f'{name} does not match sources.json; run git submodule update --init')
        if subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain']):
            raise SystemExit(f'{name} is modified; keep upstream submodules clean')
    stamp = fingerprint()
    if DEST.exists():
        if (DEST/'.duolite-prepared').read_text().strip() == stamp:
            print('Prepared source is current'); return
        raise SystemExit('Port changed: run make clean-source, then make prepare (build/source is generated)')
    temp = ROOT/'build/source.new'
    if temp.exists(): shutil.rmtree(temp)
    temp.parent.mkdir(parents=True, exist_ok=True)
    run('git', 'clone', '--quiet', '--no-hardlinks', str(ROOT/'upstream/BananaLinux'), str(temp))
    run('git', '-C', str(temp), 'checkout', '--quiet', '--detach', PINS['BananaLinux']['commit'])
    br = temp/'.buildroot'; br.mkdir()
    archive = subprocess.Popen(['git', '-C', str(ROOT/'upstream/buildroot'), 'archive', PINS['Buildroot']['commit']], stdout=subprocess.PIPE)
    # This is a verified git tree, not an uploaded tarball. Buildroot's rootfs
    # skeleton deliberately contains absolute symlinks such as /etc/init.d/rcS.
    with tarfile.open(fileobj=archive.stdout, mode='r|') as t: t.extractall(br, filter='fully_trusted')
    assert archive.wait() == 0
    menu = temp/'ui/third_party/banana_menu'; menu.mkdir(parents=True)
    pin = PINS['BananaFront']
    for name, sha in pin['sha256'].items():
        url = pin['repository'].replace('https://github.com/', 'https://raw.githubusercontent.com/') + '/' + pin['commit'] + '/src/' + name
        with urllib.request.urlopen(url, timeout=60) as response: data = response.read()
        if hashlib.sha256(data).hexdigest() != sha: raise SystemExit('Menu source hash mismatch: '+name)
        dest = menu/name; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
    url = pin['repository'].replace('https://github.com/', 'https://raw.githubusercontent.com/') + '/' + pin['commit'] + '/LICENSE'
    with urllib.request.urlopen(url, timeout=60) as response: data = response.read()
    if hashlib.sha256(data).hexdigest() != pin['license_sha256']: raise SystemExit('Menu license hash mismatch')
    (menu/'COPYING').write_bytes(data)
    shutil.copytree(ROOT/'overlay', temp, dirs_exist_ok=True, symlinks=True)
    for patch in sorted((ROOT/'patches').glob('*.patch')):
        run('git', '-C', str(temp), 'apply', '--check', str(patch))
        run('git', '-C', str(temp), 'apply', str(patch))
    assert (temp/'buildroot/board/duolite/RELEASE').read_text() == (ROOT/'VERSION').read_text()
    (temp/'.duolite-prepared').write_text(stamp+'\n')
    temp.rename(DEST)
    print('Prepared pinned BananaLinux + Duo Lite port in build/source')

if __name__ == '__main__': prepare()
