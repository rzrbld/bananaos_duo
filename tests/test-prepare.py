#!/usr/bin/env python3
"""Preparation stays stable after Python tests create disposable bytecode."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('prepare', Path(__file__).resolve().parents[1]/'scripts/prepare.py')
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)

class Preparation(unittest.TestCase):
    def test_generated_bytecode_cannot_change_or_enter_source(self):
        original = prepare.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'scripts').mkdir()
            (root/'scripts/prepare.py').write_text('source')
            (root/'sources.json').write_text('{}')
            (root/'patches').mkdir()
            overlay = root/'overlay'
            overlay.mkdir()
            helper = overlay/'helper.py'
            helper.write_text('print("original")\n')
            try:
                prepare.ROOT = root
                baseline = prepare.fingerprint()
                cache = overlay/'__pycache__'
                cache.mkdir()
                (cache/'helper.cpython-314.pyc').write_bytes(b'generated')
                (overlay/'helper.pyo').write_bytes(b'generated')
                self.assertEqual(prepare.fingerprint(), baseline)
                destination = root/'prepared'
                prepare.copy_overlay(overlay, destination)
                self.assertEqual((destination/'helper.py').read_bytes(), helper.read_bytes())
                self.assertFalse((destination/'__pycache__').exists())
                self.assertFalse((destination/'helper.pyo').exists())
                helper.write_text('print("changed")\n')
                self.assertNotEqual(prepare.fingerprint(), baseline)
                changed = prepare.fingerprint()
                helper.chmod(0o755)
                self.assertNotEqual(prepare.fingerprint(), changed)
            finally:
                prepare.ROOT = original

if __name__ == '__main__': unittest.main()
