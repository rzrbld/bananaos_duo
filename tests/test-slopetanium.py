#!/usr/bin/env python3
"""Firmware manager policy and non-destructive first-run bootstrap."""
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT/'overlay/system/rootfs/usr/libexec/banana/slopetanium-portmaster-bootstrap'
loader = importlib.machinery.SourceFileLoader('pm_bootstrap', str(HELPER))
spec = importlib.util.spec_from_loader(loader.name, loader)
bootstrap = importlib.util.module_from_spec(spec)
loader.exec_module(bootstrap)

class Integration(unittest.TestCase):
    def test_bootstrap_preserves_upstream_payload_and_existing_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); ports=p/'ports'; ports.mkdir(); archive=p/'pm.zip'
            payload={'PortMaster/harbourmaster': b'upstream installer', 'PortMaster/PortMaster.sh': b'#!/bin/bash\necho upstream\n', 'PortMaster/control.txt': b'upstream environment'}
            with zipfile.ZipFile(archive, 'w') as z:
                for name, data in payload.items(): z.writestr(name, data)
            bootstrap.install(archive, ports)
            for name, data in payload.items(): self.assertEqual((ports/name).read_bytes(), data)
            self.assertEqual((ports/'PortMaster.sh').read_bytes(), payload['PortMaster/PortMaster.sh'])
            (ports/'PortMaster/harbourmaster').write_bytes(b'user updated this')
            with self.assertRaises(RuntimeError): bootstrap.install(archive, ports)
            self.assertEqual((ports/'PortMaster/harbourmaster').read_bytes(), b'user updated this')

    def test_bootstrap_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); ports=p/'ports'; ports.mkdir(); archive=p/'bad.zip'
            with zipfile.ZipFile(archive,'w') as z: z.writestr('PortMaster/../../escape', b'no')
            with self.assertRaises(ValueError): bootstrap.install(archive, ports)
            self.assertFalse((p/'escape').exists())
            self.assertFalse((ports/'PortMaster').exists())

    def test_firmware_uses_one_pinned_manager_and_separate_destinations(self):
        pin=json.loads((ROOT/'sources.json').read_text())['Slopetanium']['commit']
        self.assertIn(pin, (ROOT/'overlay/buildroot/package/slopetanium/slopetanium.mk').read_text())
        helper=(ROOT/'overlay/system/rootfs/usr/libexec/banana/run-slopetanium').read_text()
        self.assertIn('P=/data/roms/ports',helper)
        self.assertIn('SLOP_APPS_DIR=/data/store/apps SLOP_APP_SHORTCUTS_DIR=/data/store/tiles',helper)
        self.assertIn('SLOP_SYSTEM_MANAGED=1',helper)
        conf=(ROOT/'build/source/system/rootfs/etc/banana/systems.conf').read_text()
        self.assertIn('[slopetanium]',conf)
        self.assertNotIn('[rocknixdsstore]',conf)

if __name__=='__main__': unittest.main()
