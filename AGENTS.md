# Working on BananaOS Duo Lite

This repository is the native BananaOS Buildroot port for Retroid Pocket Duo
Lite. Read [docs/README.md](docs/README.md), especially
[scope](docs/SCOPE.md), [architecture](docs/ARCHITECTURE.md),
[development](docs/DEVELOPMENT.md) and [current state](docs/STATE.md).

## Established project decisions

- Maintain a small port over pinned upstream repositories. Author changes in
  `patches/`, `overlay/`, `scripts/` or `tests/`; `build/source` is generated.
  Keep `upstream/` submodules clean. Do not reset historical workspaces.
- Keep the OS immutable. Settings, installed apps, app updates and user data
  belong on writable storage. The data card can be exFAT: do not require symlinks,
  Unix ownership or executable mode bits there.
- Keep vanilla PortMaster, its updater and installed ports untouched. Put
  platform integration in OS helpers/profiles. Preserve user RetroArch settings.
  An app fork is a separate, explicit project decision, with its own repository,
  source changes and update feed; never silently patch installed app binaries.
- Slopetanium is a home-menu app and independently writable/updatable. Ports go
  through PortMaster and the Ports shelf; native apps get home-menu tiles. App
  code stays in the app's own repository and release ZIP.
- Preserve the supplied OpenABL directory byte-for-byte. System updates operate
  on the SD card's inactive A/B slot, never Android or the internal bootloader.
- Preserve the quiet fan policy and its emergency override. Optional rumble
  must never prevent buttons/axes from registering.
- Use the original BananaOS game-menu UI and system styling. Fix shared panel
  geometry rather than patching each reported page or stretching a 4:3 canvas.
- The upper panel is physically portrait, logically 1920×1080 after rotation;
  the lower panel is 1280×960. Read the hardware environment instead of assuming
  RG DS resolutions or connector names. Keep outer and inner theme patterns
  distinct when extending backgrounds.

## Build, release and commit rules

- Public release assets are built and published by GitHub Actions. Never upload
  locally built firmware/app ZIPs as public release assets or replace an existing
  published tag's files. Corresponding source archives are deliberate, not a
  duplicate of GitHub's automatic repository archive.
- Firmware builds run nightly at 00:00 UTC / 03:00 Moscow, or by manual dispatch.
  Do not add full firmware builds to normal pushes or tags. Local complete builds
  may update the development handheld; another card is used for nightly testing.
- When committing OS work without immediate CI, include `[skip ci]`. Keep the
  actual release/version files consistent. Never rewrite published tags/history.
- Every authored commit must include
  `Co-authored-by: Codex <noreply@openai.com>`. Preserve upstream attribution and
  the existing project author identity. See [CONTRIBUTING.md](CONTRIBUTING.md).
- Run checks appropriate to the change. Build a complete firmware before
  installing OS changes; do not leave an untracked collection of live edits.
  After installation, verify the active components against the built image.
- Generate SquashFS ownership under the Buildroot fakeroot environment. Never
  repack an extracted root using host UID/GID metadata. Preserve service owners
  and pass the privileged startup/setuid ownership image check before deployment.

## Device work and handoff

- Check for a running game or package installation before restarting anything.
  Do not terminate a user's session or overwrite saves to make testing easier.
  Temporary tests must restore the launcher and use separate save paths.
- Do not read saved Wi-Fi passwords; the user chose to enter Wi-Fi on-device.
  Do not publish credentials, keys, personal logs, games or microphone recordings.
- Separate source checks, local image checks, installed-hash verification and
  user-observed behavior in reports. A release being built is not a release
  published; a logical screenshot does not prove physical panel orientation.
- Update focused docs when behavior changes, and [docs/STATE.md](docs/STATE.md)
  with the verified handoff state. Keep transient commands and raw evidence out
  of the repository. Ask about unknown physical results instead of inventing them.
