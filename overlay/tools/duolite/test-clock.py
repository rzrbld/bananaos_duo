#!/usr/bin/env python3
"""Validate RTC-offset recovery without changing the host clock."""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import json

source = Path(__file__).resolve().parents[2]/'buildroot/board/duolite/rootfs/usr/libexec/banana/duolite-clock'
loader = SourceFileLoader('duolite_clock', str(source))
module = module_from_spec(spec_from_loader(loader.name, loader)); loader.exec_module(module)
WALL = 1795376763

class Clock(unittest.TestCase):
    def test_counter_continues(self):
        self.assertEqual(module.estimate({'wall':WALL,'rtc':100},140),WALL+40)
    def test_counter_reset_does_not_move_time_back(self):
        self.assertEqual(module.estimate({'wall':WALL,'rtc':100},5),WALL)
    def test_bad_saved_values(self):
        for bad in ({}, {'wall':False,'rtc':1}, {'wall':1,'rtc':1}, {'wall':WALL,'rtc':-1}, []):
            self.assertIsNone(module.estimate(bad,10))
        self.assertEqual(module.estimate({'wall':WALL,'rtc':0},0xffffffff),WALL)
    def test_save_and_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp)/'saved.json';rtc=Path(tmp)/'rtc';rtc.write_text('100')
            with patch.object(module,'DATA',data),patch.object(module,'RTC',rtc):
                with patch.object(module.time,'time',return_value=WALL):
                    self.assertEqual(module.main('save'),0)
                self.assertEqual(json.loads(data.read_text()),{'wall':WALL,'rtc':100})
                # An unset clock must never overwrite the good offset.
                with patch.object(module.time,'time',return_value=1):
                    self.assertEqual(module.main('save'),0)
                self.assertEqual(json.loads(data.read_text())['wall'],WALL)
                rtc.write_text('125')
                with patch.object(module.time,'time',return_value=1),patch.object(module.subprocess,'run') as run:
                    self.assertEqual(module.main('restore'),0)
                    run.assert_called_once_with(['date','-u','-s','@'+str(WALL+25)],check=True)
                with patch.object(module.time,'time',return_value=WALL+200),patch.object(module.subprocess,'run') as run:
                    self.assertEqual(module.main('restore'),0);run.assert_not_called()

if __name__=='__main__':unittest.main()
