#!/usr/bin/env python3
"""Check touchscreen probing and the actual unequal-panel coordinate mapper."""
import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'overlay/buildroot/board/duolite/rootfs/usr/libexec/banana/duolite-touchscreen'
loader = importlib.machinery.SourceFileLoader('touchscreen', str(HELPER))
spec = importlib.util.spec_from_loader(loader.name, loader)
touchscreen = importlib.util.module_from_spec(spec)
loader.exec_module(touchscreen)


class Touchscreen(unittest.TestCase):
    def fixture(self, root):
        devices = root / 'bus/i2c/devices'
        devices.mkdir(parents=True)
        parent = root / 'devices/4a88000.i2c/i2c-1'
        device = parent / '1-0048'
        (device / 'of_node').mkdir(parents=True)
        (device / 'of_node/compatible').write_bytes(b'himax,hx83112a\0')
        (devices / 'i2c-1').symlink_to(parent)
        (devices / device.name).symlink_to(device)
        return device

    def test_already_bound_is_not_reset(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            device = self.fixture(root)
            (device / 'driver').mkdir()
            touchscreen.initialize(root, load=lambda: self.fail('must not reload'))
            self.assertFalse((root / 'bus/i2c/drivers_probe').exists())

    def test_unbound_probe_and_failure_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            loaded = []
            with self.assertRaisesRegex(RuntimeError, 'remained unbound'):
                touchscreen.initialize(root, load=lambda: loaded.append(True))
            self.assertEqual(loaded, [True])
            self.assertEqual((root / 'bus/i2c/drivers_probe').read_text(), '1-0048\n')

    def test_other_controller_is_not_probed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            device = self.fixture(root)
            (device / 'of_node/compatible').write_bytes(b'focaltech,ft5452\0')
            with self.assertRaisesRegex(RuntimeError, 'not found'):
                touchscreen.initialize(root, load=lambda: self.fail('wrong controller'))
            self.assertFalse((root / 'bus/i2c/drivers_probe').exists())

    def test_physical_corners_match_scanout_at_every_rotation(self):
        source = r'''
#include "touch_geometry.h"
#include "scanout.h"
#include <cassert>
#include <cmath>
#include <vector>
int main() {
    for (int rotation : {0, 90, 180, 270}) {
        const int w = 12, h = 20;
        const int sw = rotation % 180 ? h : w, sh = rotation % 180 ? w : h;
        std::vector<uint32_t> canvas(sw*sh), panel(w*h);
        for (int i=0; i<sw*sh; i++) canvas[i] = i+1;
        banana::fitScanout((uint8_t*)panel.data(), w*4, w, h, rotation, canvas.data(), sw, sh);
        for (int y : {0,h-1}) for (int x : {0,w-1}) {
            auto p = banana::touchPoint(float(x)/(w-1),float(y)/(h-1),rotation,sw,sh);
            assert(canvas[lround(p.y)*sw+lround(p.x)] == panel[y*w+x]);
        }
    }
    auto bottom = banana::touchPoint(1,1,0,1280,960);
    auto top = banana::touchPoint(0,0,270,1707,960);
    assert(bottom.x == 1279 && bottom.y == 959);
    assert(top.x == 1706 && top.y == 0);
}'''
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            (path / 'test.cpp').write_text(source)
            subprocess.run(['g++', '-std=c++17', '-I'+str(ROOT/'build/source/ui/src'),
                            str(path/'test.cpp'), '-o', str(path/'test')], check=True)
            subprocess.run([str(path/'test')], check=True)


if __name__ == '__main__':
    unittest.main()
