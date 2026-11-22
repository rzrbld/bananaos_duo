#!/usr/bin/env python3
"""Physical LED/battery selection and kernel fan-floor interface, isolated sysfs."""
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

class Hardware(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = tempfile.TemporaryDirectory(prefix='banana-hw-test-')
        cls.binary = Path(cls.build.name) / 'hardware'
        subprocess.run(['cc', '-O1', '-g', '-Wall', '-Wextra', '-Wno-unused-parameter',
                        str(HERE / 'duolite-hardware.c'), '-Wl,--wrap=fopen',
                        '-Wl,--wrap=open', '-Wl,--wrap=opendir', '-o', str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.build.cleanup()

    def run_case(self, mode, plugged, status, level=128, profile='auto', floor=True, percent=47):
        with tempfile.TemporaryDirectory(prefix='banana-sysfs-') as tmp:
            root = Path(tmp)
            def put(path, value):
                target = root / 'sys' / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(str(value))
            # Enumerated first deliberately: a gamepad battery must be ignored.
            put('class/power_supply/aaa-controller/type', 'Battery')
            put('class/power_supply/aaa-controller/capacity', 1)
            put('class/power_supply/aaa-controller/status', 'Discharging')
            put('class/power_supply/battery/type', 'Battery')
            put('class/power_supply/battery/capacity', percent)
            put('class/power_supply/battery/status', status)
            put('class/power_supply/usb/type', 'USB')
            put('class/power_supply/usb/online', int(plugged))
            led = 'class/leds/rgb:status/'
            for key in ['brightness', 'trigger', 'multi_intensity', 'delay_on', 'delay_off']:
                put(led + key, 'initial')
            put('class/leds/input10:rgb:indicator/brightness', 'unchanged')
            put('class/backlight/backlight/bl_power', 0)
            put('class/backlight/serial0-0/bl_power', 0)
            put('class/hwmon/hwmon23/name', 'pwmfan')
            put('class/hwmon/hwmon23/pwm1', 140)
            if floor:
                put('class/hwmon/hwmon23/pwm1_floor', 0)
            subprocess.run([str(self.binary), tmp, mode, str(level), profile, str(percent)], check=True)
            def get(path):
                return (root / 'sys' / path).read_text()
            self.assertEqual(get('class/leds/input10:rgb:indicator/brightness'), 'unchanged')
            self.assertEqual(get('class/hwmon/hwmon23/pwm1'), '140')
            self.assertEqual(get('class/backlight/backlight/bl_power'), '4')
            self.assertEqual(get('class/backlight/serial0-0/bl_power'), '4')
            if floor:
                self.assertEqual(get('class/hwmon/hwmon23/pwm1_floor'),
                                 {'auto':'0','low':'32','medium':'36','high':'40'}.get(profile,'0'))
            return {key: get(led + key) for key in ['brightness', 'trigger', 'multi_intensity']}

    def test_charging_only(self):
        self.assertEqual(self.run_case('charging', False, 'Discharging')['brightness'], '0')
        light = self.run_case('charging', True, 'Charging')
        self.assertEqual((light['brightness'], light['multi_intensity']), ('128', '255 128 0'))
        light = self.run_case('charging', True, 'Full')
        self.assertEqual(light['multi_intensity'], '0 255 0')

    def test_off_and_brightness(self):
        self.assertEqual(self.run_case('off', True, 'Charging')['brightness'], '0')
        self.assertEqual(self.run_case('battery', False, 'Discharging', 0)['brightness'], '0')
        self.assertEqual(self.run_case('charging', True, 'Charging', 999)['brightness'], '255')
        self.assertEqual(self.run_case('charging', True, 'Charging', -1)['brightness'], '0')

    def test_low_battery(self):
        self.assertEqual(self.run_case('battery', False, 'Discharging', percent=15)['multi_intensity'], '255 0 0')
        critical = self.run_case('battery', False, 'Discharging', percent=4)
        self.assertEqual((critical['multi_intensity'], critical['trigger']), ('255 0 0', 'timer'))
        self.assertEqual(self.run_case('charging', False, 'Discharging', percent=4)['brightness'], '0')
        self.assertEqual(self.run_case('charging', True, 'Not charging')['multi_intensity'], '255 128 0')

    def test_battery_and_profiles(self):
        for profile in ['auto','low','medium','high','invalid']:
            light = self.run_case('battery', False, 'Discharging', profile=profile)
            self.assertEqual(light['multi_intensity'], '0 255 0')
        self.run_case('charging', False, 'Discharging', profile='low', floor=False)

if __name__ == '__main__':
    unittest.main()
