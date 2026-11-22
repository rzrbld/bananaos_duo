#!/usr/bin/env python3
"""Package a checked image, original-format A/B update and matching sources."""
import argparse
import gzip
import hashlib
import io
import json
import re
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def text_member(tar, name, data):
    b = data.encode(); info = tarfile.TarInfo(name); info.size = len(b); info.mode = 0o644
    tar.addfile(info, io.BytesIO(b))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('images', 'source', 'legal', 'output'): p.add_argument('--'+name, type=Path, required=True)
    args = p.parse_args(); out = args.output; out.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', '-C', str(ROOT), 'diff', '--exit-code', '--quiet'], check=True)
    subprocess.run(['git', '-C', str(ROOT), 'diff', '--cached', '--exit-code', '--quiet'], check=True)
    port_commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    pins = json.loads((ROOT/'sources.json').read_text())
    # External toolchain legal-info contains the SDK binary. Collect matching
    # GCC runtime/glibc sources too, from Bootlin's pinned source archive.
    runtime = ROOT/'build/toolchain-runtime'
    for file in pins['ToolchainRuntime']['sources']:
        dest = runtime/file['path']; dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.is_file() or sha(dest) != file['sha256']:
            with urllib.request.urlopen(file['url'], timeout=120) as response, dest.with_suffix(dest.suffix+'.new').open('wb') as f:
                shutil.copyfileobj(response, f)
            dest.with_suffix(dest.suffix+'.new').replace(dest)
        assert sha(dest) == file['sha256'], 'Toolchain source hash mismatch: '+file['path']
    version = (ROOT/'VERSION').read_text().strip()
    assert re.fullmatch(r'\d+\.\d+\.\d+(?:-alpha\.\d+)?', version), version
    assert (args.source/'buildroot/board/duolite/RELEASE').read_text().strip() == version
    images = args.images
    # Streaming comparison prevents a truncated .gz being published beside a good raw image.
    h = hashlib.sha256()
    with gzip.open(images/'banana-duolite.img.gz', 'rb') as f:
        for b in iter(lambda: f.read(8<<20), b''): h.update(b)
    assert h.hexdigest() == sha(images/'banana-duolite.img')
    required = ('Image', 'sm6125-retroid-pocket-duo-lite.dtb', 'rootfs.squashfs')
    hashes = {name: sha(images/name) for name in required}
    name = 'banana-duolite-'+version
    shutil.copyfile(images/'banana-duolite.img.gz', out/(name+'.img.gz'))
    prefix = name+'.update'
    with tarfile.open(out/(prefix+'.tar'), 'w') as tar:
        for file in required: tar.add(images/file, arcname=prefix+'/'+file, recursive=False)
        text_member(tar, prefix+'/VERSION', version+'\n')
        text_member(tar, prefix+'/board', 'duolite\n')
        metadata = {'VERSION': version+'\n', 'board': 'duolite\n'}
        sums = {**hashes, **{n: hashlib.sha256(b.encode()).hexdigest() for n,b in metadata.items()}}
        text_member(tar, prefix+'/sha256sums', ''.join(h+'  '+n+'\n' for n,h in sums.items()))
    # GPL corresponding sources: the complete prepared OS tree, this port and
    # Buildroot's source archives + license manifests. No build cache or /data.
    assert (args.legal/'manifest.csv').is_file(), 'Run make legal-info before packaging'
    archive = out/(name+'-sources.tar.gz')
    excluded = {'.git', '.buildroot', '.duolite-prepared', '__pycache__', 'rc-obj', 'stock-menu-obj'}
    def source_filter(info):
        parts = Path(info.name).parts
        if any(part in excluded for part in parts): return None
        return info
    with tarfile.open(archive, 'w:gz', compresslevel=1) as tar:
        names = subprocess.check_output(['git', '-C', str(args.source), 'ls-files', '--cached', '--others', '--exclude-standard', '-z']).decode().split('\0')
        for name in names:
            if not name or name == '.duolite-prepared': continue
            path = args.source/name
            if path.exists() or path.is_symlink(): tar.add(path, arcname='source/BananaLinux/'+name, recursive=False)
        tar.add(args.legal, arcname='source/legal-info')
        tar.add(runtime, arcname='source/toolchain-runtime')
        toolchain = args.legal.parent/'host/opt/ext-toolchain'
        for file in ('buildroot.config', 'summary.csv', 'README.txt'):
            tar.add(toolchain/file, arcname='source/toolchain-runtime/'+file)
        tar.add(ROOT/'upstream/buildroot', arcname='source/buildroot', filter=source_filter)
        for folder in ('patches', 'overlay', 'scripts', 'docs', 'tests', '.github'):
            tar.add(ROOT/folder, arcname='source/port/'+folder, filter=source_filter)
        for file in ('README.md', 'LICENSE', 'THIRD_PARTY.md', 'VERSION', 'sources.json', 'Makefile', '.gitmodules'):
            tar.add(ROOT/file, arcname='source/port/'+file)
    # GitHub assets are limited to 2 GiB. Split only if necessary; instructions
    # for joining parts remain in the manifest and docs/BUILD.md.
    if archive.stat().st_size >= 1900<<20:
        with archive.open('rb') as f:
            i = 0
            while f.tell() < archive.stat().st_size:
                with (out/(archive.name+f'.part{i:03d}')).open('wb') as part:
                    left = 1900<<20
                    while left and (block := f.read(min(left, 8<<20))): part.write(block); left -= len(block)
                i += 1
        archive.unlink()
    manifest = {'device': 'Retroid Pocket Duo Lite', 'board': 'duolite', 'version': version,
                'repository': 'rzrbld/bananaos_duo', 'port_commit': port_commit, 'components': hashes,
                'upstream': pins, 'includes_user_data': False,
                'openabl': json.loads((args.source/'buildroot/board/duolite/openabl-source.json').read_text())}
    (out/'release-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    files = sorted(p for p in out.iterdir() if p.is_file() and p.name != 'SHA256SUMS-duolite.txt')
    (out/'SHA256SUMS-duolite.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in files))
    print('Packaged image, A/B update, corresponding sources and SHA256SUMS-duolite.txt')

if __name__ == '__main__': main()
