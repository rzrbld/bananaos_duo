#!/usr/bin/env python3
"""Check added-system settings coverage and execute the native control helper."""
import configparser
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'build/source'
HELPER = SOURCE / 'system/rootfs/usr/libexec/banana/retroarch-controls-duolite'


class EmulatorSettings(unittest.TestCase):
    def test_added_systems_have_matching_settings_and_default_cores(self):
        systems = configparser.ConfigParser(interpolation=None)
        systems.read(SOURCE / 'buildroot/board/duolite/systems-extra.conf')
        ui = (SOURCE / 'ui/src/settings.cpp').read_text()
        table = ui.split('RA_SYSTEMS[] = {', 1)[1].split('\n\t};', 1)[0]
        for system in systems.sections():
            with self.subTest(system=system):
                row = next((line for line in table.splitlines()
                            if re.match(r'\s*\{ "' + re.escape(system) + r'",', line)), '')
                self.assertTrue(row, 'system missing from shared Buttons/Emulators table')
                core = systems[system]['run'].split()[1]
                self.assertIn('{ "' + core + '",', row)

    def test_runtime_controls_are_isolated_and_use_sdl_bindings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            card, defaults = root/'settings', root/'defaults'
            cfg, commands = root/'append.cfg', root/'commands'
            defaults.write_text('ra_btn_r2.psp = ff\nra_swap_ab.psp = on\n')
            card.write_text('ra_btn_l2.psp = save\nra_btn_r2.psp = game\n'
                            'ra_btn_l3.psp = pause\nra_btn_r3.psp = none\n'
                            'ra_swap_ab.psp = off\nra_swap_ab.psp = on\n'
                            'ra_btn_r2.wii = load\n')
            originals = (card.read_bytes(), defaults.read_bytes())

            def run(system):
                cfg.write_text('existing_profile = "kept"\n')
                subprocess.run(['sh', '-eu', '-c',
                                '. "$1"; duolite_ra_controls "$2" "$3" "$4" "$5" "$6"',
                                'controls-test', str(HELPER), str(cfg), str(commands),
                                system, str(card), str(defaults)], check=True)
                return cfg.read_text()

            text = run('psp')
            self.assertEqual(commands.read_text(), 'l2 SAVE_STATE\nl3 PAUSE_TOGGLE\nr3 -\n')
            self.assertIn('input_player1_l2_axis = "+30"', text)
            self.assertIn('input_player1_l3_btn = "32"', text)
            self.assertNotIn('input_player1_r2_', text)  # Game's own overrides default FF.
            self.assertIn('input_player1_a_btn = "1"', text)
            self.assertIn('input_player1_b_btn = "0"', text)
            self.assertTrue(text.startswith('existing_profile = "kept"\n'))
            run('wii')
            self.assertEqual(commands.read_text(), 'r2 LOAD_STATE\n')  # No stale PSP commands.
            run('')
            self.assertFalse(commands.exists())
            card.write_text('')
            text = run('psp')
            self.assertEqual(commands.read_text(), 'r2 FAST_FORWARD\n')  # Template fallback.
            self.assertIn('input_player1_r2_axis = "+31"', text)
            self.assertEqual(defaults.read_bytes(), originals[1])
            # The helper must never write the saved card configuration.
            self.assertEqual(card.read_text(), '')


if __name__ == '__main__':
    unittest.main()
