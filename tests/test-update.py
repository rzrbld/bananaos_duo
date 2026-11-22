#!/usr/bin/env python3
"""Exercise the real updater against file-backed SD slots and a local feed."""
import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'build/source'
UPDATER = SOURCE/'system/rootfs/usr/libexec/banana/update'
HELPER = SOURCE/'system/rootfs/usr/libexec/banana/update-duolite-boot'
DTB = 'sm6125-retroid-pocket-duo-lite.dtb'

class Update(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='duolite-update-'); self.root = Path(self.tmp.name)
        self.boot = self.root/'boot'; self.run = self.root/'run'; self.data = self.root/'data'
        for d in ('boot/loader/entries', 'boot/a', 'boot/b', 'run', 'data/updates', 'dev', 'bin',
                  'sys/class/block/mmcblk0p2', 'sys/class/block/mmcblk0p3'): (self.root/d).mkdir(parents=True, exist_ok=True)
        for s in 'ab':
            (self.boot/s/'Image').write_text('kernel-old-'+s)
            (self.boot/s/DTB).write_text('dtb-old-'+s)
        self.entry = self.boot/'loader/entries/banana.conf'
        self.entry.write_text('title BananaOS\nlinux /a/Image\ndevicetree /a/'+DTB+'\noptions root=PARTLABEL=banana-root-a rootfstype=squashfs ro console=tty0\n')
        (self.run/'slot').write_text('a\n'); (self.run/'disk').write_text(str(self.root/'dev/mmcblk0')+'\n')
        for part in ('2', '3'):
            with (self.root/('dev/mmcblk0p'+part)).open('wb') as f: f.truncate(64<<20)
            (self.root/('sys/class/block/mmcblk0p'+part+'/size')).write_text(str(64*2048))
        self.executable('mount', '#!/bin/sh\nexit 0\n')
        dd = shutil.which('dd')
        self.executable('dd', '#!/usr/bin/env python3\nimport os,sys,subprocess\na=sys.argv[1:]\n'
            'if os.getenv("DD_FAIL") and "seek=1" in a: sys.exit(1)\n'
            f'r=subprocess.run([{dd!r},*a]);\n'
            'if not r.returncode and os.getenv("DD_CORRUPT") and "seek=1" in a:\n'
            ' p=next(x[3:] for x in a if x.startswith("of="))\n'
            ' with open(p,"r+b") as f:f.write(b"!")\n'
            'sys.exit(r.returncode)\n')
        helper = HELPER.read_text().replace('/boot', str(self.boot))
        (self.root/'helper').write_text(helper)
        script = UPDATER.read_text().replace('/boot', str(self.boot)).replace('/sys/class/block/', str(self.root/'sys/class/block')+'/')
        script = script.replace('/proc/sys/vm/drop_caches', '/dev/null').replace('[ -b "$PART" ]', '[ -f "$PART" ]')
        # Physical-device identity cannot exist on a host fixture. Only that
        # guard is stubbed; all real package, hash, write and BLS code runs.
        script = script.replace('case $1 in\nlist)', 'duolite_guard() { :; }\ncase $1 in\nlist)')
        (self.root/'update').write_text(script)
        self.env = {**os.environ, 'PATH':str(self.root/'bin')+':'+os.environ['PATH'],
            'BANANA_RUN':str(self.run), 'BANANA_DATA':str(self.data), 'BANANA_BOARD':'duolite',
            'BANANA_VERSION':'0.1.0-alpha.25', 'BANANA_UPDATE_BOOT_HELPER':str(self.root/'helper')}

    def tearDown(self): self.tmp.cleanup()
    def executable(self, name, text):
        p=self.root/'bin'/name; p.write_text(text); p.chmod(0o755)
    def invoke(self, *args, ok=True, **env):
        r=subprocess.run(['sh',str(self.root/'update'),*map(str,args)],env={**self.env,**env},capture_output=True,text=True)
        self.assertEqual(r.returncode==0,ok,r.stdout+r.stderr); return r.stdout
    def default(self):
        return 'a' if 'root=PARTLABEL=banana-root-a ' in self.entry.read_text() else 'b'
    def package(self, version='0.1.0-alpha.26', board='duolite', missing=None):
        files={'Image':('kernel-'+version).encode(), DTB:('dtb-'+version).encode(),
            'rootfs.squashfs':b'x'*(40<<20),'VERSION':(version+'\n').encode(),'board':(board+'\n').encode()}
        files['sha256sums']=''.join(hashlib.sha256(b).hexdigest()+'  '+n+'\n' for n,b in files.items() if n!=missing).encode()
        p=self.data/'updates'/('banana-duolite-'+version+'.update.tar')
        with tarfile.open(p,'w') as t:
            for n,b in files.items():
                i=tarfile.TarInfo('payload/'+n);i.size=len(b);t.addfile(i,io.BytesIO(b))
        return p

    def test_good_apply_and_previous(self):
        p=self.package(); self.invoke('apply',p);self.assertEqual(self.default(),'b')
        self.assertEqual((self.boot/'b/Image').read_text(),'kernel-0.1.0-alpha.26')
        recovery=(self.boot/'loader/entries/banana-recovery.conf').read_text();self.assertIn('root=PARTLABEL=banana-root-a ',recovery)
        (self.run/'slot').write_text('b\n');self.invoke('switch','a');self.assertEqual(self.default(),'a')
    def test_interrupted_write(self):
        p=self.package();self.invoke('apply',p,ok=False,DD_FAIL='1');self.assertEqual(self.default(),'a')
        self.assertFalse((self.boot/'b/Image').exists());self.invoke('switch','b',ok=False)
        self.invoke('apply',p);self.assertEqual(self.default(),'b')
    def test_second_apply_before_reboot(self):
        self.invoke('apply',self.package());self.assertEqual(self.default(),'b')
        self.invoke('apply',self.package('0.1.0-alpha.27'),ok=False,DD_FAIL='1')
        self.assertEqual(self.default(),'a');self.invoke('switch','b',ok=False)
    def test_readback_corruption(self):
        self.invoke('apply',self.package(),ok=False,DD_CORRUPT='1');self.assertEqual(self.default(),'a')
        self.assertIn('reads back wrong',(self.run/'update-status').read_text())
    def test_wrong_board_and_missing_checksum(self):
        before=self.entry.read_bytes()
        self.invoke('apply',self.package(board='universal'),ok=False)
        self.invoke('apply',self.package(missing='Image'),ok=False)
        self.assertEqual(self.entry.read_bytes(),before)
        self.assertEqual((self.boot/'b/Image').read_text(),'kernel-old-b')
    def test_fresh_image_kernel_paths(self):
        shutil.copyfile(self.boot/'a/Image',self.boot/'Image')
        (self.boot/'dtbs/qcom').mkdir(parents=True)
        shutil.copyfile(self.boot/'a'/DTB,self.boot/'dtbs/qcom'/DTB)
        shutil.rmtree(self.boot/'a')
        self.entry.write_text(self.entry.read_text().replace('/a/Image','/Image').replace('/a/'+DTB,'/dtbs/qcom/'+DTB))
        self.invoke('apply',self.package());self.assertEqual(self.default(),'b')
        self.assertEqual((self.boot/'a/Image').read_text(),'kernel-old-a')
        self.invoke('switch','a');self.assertEqual(self.default(),'a')
    def test_port_release_feed_and_version_order(self):
        releases=[]
        for version,board,draft in [('0.1.0-alpha.100','duolite',True),('0.1.0-alpha.99','rgds',False),
                                    ('0.1.0-alpha.27','duolite',False),('0.1.0-alpha.26','duolite',False)]:
            url='https://github.com/rzrbld/bananaos_duo/releases/download/v'+version+'/'
            releases.append({'tag_name':'v'+version,'draft':draft,'prerelease':True,'assets':[
                {'size':100,'browser_download_url':url+'banana-'+board+'-'+version+'.update.tar'},
                {'size':100,'browser_download_url':url+'SHA256SUMS-'+board+'.txt'}]})
        feed=self.root/'feed.json';feed.write_text(json.dumps(releases))
        answer=self.invoke('check',BANANA_UPDATE_FEED=feed.as_uri())
        self.assertIn('state=newer',answer);self.assertIn('latest=0.1.0-alpha.27',answer)
        self.assertIn('rzrbld/bananaos_duo/releases/download/',answer)
        self.package();self.assertIn('\t0.1.0-alpha.26\tduolite',self.invoke('list'))

if __name__=='__main__': unittest.main(verbosity=2)
