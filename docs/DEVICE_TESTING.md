# Device testing and installation

## Before changing a running device

Confirm the model, current release, active root slot, connectivity and free
storage. IP addresses and temporary SSH master sockets can change after reboot;
discover or verify them instead of trusting a prior session. The RG DS is an
optional BananaOS UI/reference device, not the firmware target.

Check `/run/banana/game.pid`, running processes and Slopetanium's busy state.
Leave a user's game or active package transaction alone. Ask them to save/return
to the launcher when necessary. Use separate save/state directories for tests.
Temporary helpers must restore launcher respawn, performance state, mounts and
child processes even when a test fails or times out.

The user enters Wi-Fi credentials on the device. Do not extract its saved Wi-Fi
password to preconfigure images. Keep SSH keys, tokens, personal logs, recordings
and game content out of Git and public artifacts. Do not add extra authentication
requirements merely as a convenience for testing; use the documented device login.

## Firmware updates

1. Build the complete image from authored source and run its image checks. Record
   the version, source commit and hashes of `Image`, the Duo Lite DTB and
   `rootfs.squashfs`.
2. Use the normal BananaOS update package/installer. Check no game/transaction is
   active. The updater writes and verifies the inactive SD slot before changing
   the boot default. Preserve the currently running slot as recovery.
3. Restart only after successful installation. Reconnect, verify the running
   release/slot and compare the installed components with the built image using
   `scripts/verify-installed.py`; see [UPDATES.md](UPDATES.md).
4. Check registered buttons/axes, Wi-Fi reconnect, both screens, fan behavior and
   the affected feature. Report measured results separately from user observations.

Do not apply a random set of writable live edits in place of a firmware build.
A temporary, explicitly scoped test may bind a library built in the complete
candidate image, then restore the original mount; record that this was a test,
not installation. Do not touch Android/internal boot storage or the original
OpenABL installer during system updates.

## Useful regression checks

| Change | Check |
| --- | --- |
| Screen geometry | Top 1920×1080 logical, bottom 1280×960; real pages, animations, notifications and pointer placement; confirm physical orientation separately |
| App installation | Inspect the original ZIP; main-menu tile for Apps, PortMaster/Ports listing for ports; independent update and configuration retention |
| Emulator launch | Intended GPU renderer, controls, original menu, aspect ratio, save/load/resume and normal quit using temporary saves |
| Audio | Playback stays advancing; startup underrun recovery; launch/exit; headset → speakers → headset; both mic paths and volume overlay |
| Input/rumble | Gamepad registers with or without a motor; mappings unchanged; global rumble toggle respected |
| Cooling/power | Quiet mode remains quiet; no repeated spin-up boost; safe thermal override; sleep/wake, Wi-Fi reconnect and normal/fast shutdown separately |
| Update path | Inactive-slot write, checksum/read-back, recovery after failure, correct feed/version and active-image hash verification |

Successful process startup does not prove controls, sound or microphone capture.
Meter movement from a bias transient does not establish working speech capture.
A ROM producing a frame does not establish broad game compatibility. Preserve
those distinctions in tests and reports.
