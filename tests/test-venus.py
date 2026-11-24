#!/usr/bin/env python3
"""Exercise firmware rejection and read-only Android access / cleanup failures."""
import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'overlay/buildroot/board/duolite/rootfs/usr/libexec/banana/duolite-venus-firmware'
loader = importlib.machinery.SourceFileLoader('venus', str(HELPER))
spec = importlib.util.spec_from_loader(loader.name, loader)
venus = importlib.util.module_from_spec(spec)
loader.exec_module(venus)


class Firmware(unittest.TestCase):
    def image(self, path):
        path.mkdir()
        for name in venus.FILES:
            (path / name).write_bytes(b'\x7fELF\x01' + bytes(60))
        (path / 'venus.b02').write_bytes(b'QC_IMAGE_VERSION_STRING=VIDEO.VE.5.4-test\0')

    def test_valid_image_is_published_together(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); source = root / 'image'; self.image(source)
            target = root / 'runtime/qcom/sm6125'
            venus.stage(source, target)
            self.assertEqual(sorted(p.name for p in target.iterdir()), sorted(venus.FILES))
            for name in venus.FILES:
                self.assertEqual((source / name).read_bytes(), (target / name).read_bytes())

    def test_missing_segment_and_wrong_generation_publish_nothing(self):
        for failure in ('missing', 'wrong', 'symlink'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as d:
                root = Path(d); source = root / 'image'; self.image(source)
                if failure == 'missing': (source / 'venus.b04').unlink()
                elif failure == 'wrong': (source / 'venus.b02').write_bytes(b'VIDEO.VE.6.0')
                else:
                    (source / 'venus.b04').unlink(); (source / 'venus.b04').symlink_to(source / 'venus.b00')
                with self.assertRaises(RuntimeError): venus.stage(source, root / 'target')
                self.assertFalse((root / 'target').exists())

    def test_extraction_never_maps_or_mounts_writable_and_cleans_up(self):
        for failure in (None, 'mount', 'stage'):
            calls = []
            def run(args, **kwargs):
                calls.append(args)
                if failure == 'mount' and args[0] == 'mount':
                    raise subprocess.CalledProcessError(1, args)
                return subprocess.CompletedProcess(args, 0, stdout='/dev/loop7\n')
            with self.subTest(failure=failure), patch.object(venus, 'stage') as stage:
                if failure == 'stage': stage.side_effect = RuntimeError('bad image')
                if failure:
                    with self.assertRaises((RuntimeError, subprocess.CalledProcessError)):
                        venus.extract(Path('/dev/internal'), Path('/run/result'), Path('/run/mount'), run)
                else: venus.extract(Path('/dev/internal'), Path('/run/result'), Path('/run/mount'), run)
                self.assertIn(['losetup', '-r', '/dev/loop7', '/dev/internal'], calls)
                self.assertIn(['mount', '-t', 'vfat', '-o', 'ro,noatime', '/dev/loop7', '/run/mount'], calls)
                self.assertEqual(calls[-1], ['losetup', '-d', '/dev/loop7'])
                if failure != 'mount': self.assertEqual(calls[-2], ['umount', '/run/mount'])


if __name__ == '__main__': unittest.main()
