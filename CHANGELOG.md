# Changes

## 0.1.0-alpha.40

- Kept SDL ALSA playback interruptible so closing a game cannot wait forever in a blocked audio write.
- Included Slopetanium v0.3.1-beta with correct routing of legacy PortMaster archives.

## 0.1.0-alpha.39

- Fixed Slopetanium startup on exFAT cards without data-partition symlinks.
- Moved Slopetanium itself to writable storage with atomic independent updates and rollback.
- Kept persistent settings, downloads and backups on the data card.

## 0.1.0-alpha.38

- Fixed gamepad registration when the optional rumble motor fails to initialize.
- Removed synchronous haptic module loading from the asynchronous gamepad probe.
- Kept button/axis mapping unchanged; expose force feedback only with a ready motor.

## 0.1.0-alpha.37

- Replaced the old Store with pinned, firmware-built Slopetanium on the home menu.
- Kept PortMaster package installation in its standard Ports folder.
- Added individual home tiles for installed native apps, refreshed immediately after Slopetanium exits.
- Separated immutable manager code from persistent settings/cache and upstream app payloads.
- Added the Duo Lite top-panel rotation profile and first-run checksum-verified vanilla PortMaster bootstrap.

## 0.1.0-alpha.27

- Added native speaker/headphone routing, jack switching and physical volume control for the integrated Duo Lite audio card.
- Included the Duo Lite ALSA UCM profiles and writable runtime mixer configuration.
- Fixed the built-in microphone's missing VA PDM-clock and MIC BIAS1 dependencies; verified capture with an acoustic tone test.
- Added Settings → Display & sound → Microphone test using the standard BananaOS theme, live level meter and RAM-only five-second recording/playback.
- Released launcher audio while the microphone test is open, preventing playback conflicts and menu clicks in recordings.
- Adapted the volume indicator to the wide launcher and added its handling to the single-screen game panel.
- Retained the existing kernel quiet-fan ceiling and emergency cooling policy.

Known issue: a known-working headset microphone is detected, but capture remains silent. The corrected SoundWire mapping alone does not resolve it.

## 0.1.0-alpha.26

- Published the Duo Lite port as pinned upstream submodules, patches and device files.
- Added public GitHub release discovery with independent port versions.
- Retained BananaOS A/B package/download/write/checksum behavior and added OpenABL boot/recovery handling.
- Added tests for interrupted writes, damaged read-back, repeated installs before reboot, fresh-image paths, wrong-board packages and release ordering.
- Added Docker build and GitHub Actions check/build/release workflows, manifests and corresponding-source packaging.

Includes the Alpha25 emulator additions and earlier native firmware work: unequal-panel widescreen UI, original in-game menu, quiet fan/charging LED policy, Wi-Fi, sleep/wake, BananaDS and native Adreno emulation. The unchanged ROCKNIX OpenABL folder remains on the image's boot partition. Current limits are listed in `docs/STATUS.md`.
