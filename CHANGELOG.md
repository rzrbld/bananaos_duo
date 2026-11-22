# Changes

## 0.1.0-alpha.26

- Published the Duo Lite port as pinned upstream submodules, patches and device files.
- Added public GitHub release discovery with independent port versions.
- Retained BananaOS A/B package/download/write/checksum behavior and added OpenABL boot/recovery handling.
- Added tests for interrupted writes, damaged read-back, repeated installs before reboot, fresh-image paths, wrong-board packages and release ordering.
- Added Docker build and GitHub Actions check/build/release workflows, manifests and corresponding-source packaging.

Includes the Alpha25 emulator additions and earlier native firmware work: unequal-panel widescreen UI, original in-game menu, quiet fan/charging LED policy, Wi-Fi, sleep/wake, BananaDS and native Adreno emulation. The unchanged ROCKNIX OpenABL folder remains on the image's boot partition. Current limits are listed in `docs/STATUS.md`.
