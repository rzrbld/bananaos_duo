# BananaOS Duo Lite

[![Checks](https://github.com/rzrbld/bananaos_duo/actions/workflows/ci.yml/badge.svg)](https://github.com/rzrbld/bananaos_duo/actions/workflows/ci.yml)

A native [BananaOS](https://github.com/JorreFog/BananaLinux) port for the **Retroid Pocket Duo Lite**: dual-screen launcher, BananaDS, native Adreno graphics, quiet fan controls and A/B system updates through OpenABL.

**Alpha firmware.** Read [what works and the remaining limits](docs/STATUS.md) before installing. This project is maintained independently from upstream BananaOS.

## Download and install

Download the `.img.gz` from [Releases](https://github.com/rzrbld/bananaos_duo/releases). Verify it against `SHA256SUMS-duolite.txt`, then write the image to a spare microSD card. Start it through OpenABL, selecting **Retroid Pocket Duo Lite** for the device tree. Enter Wi-Fi on the handheld; network credentials are not included in releases.

The boot partition includes the **unchanged ROCKNIX `/openabl` folder** for manual installation from rooted Android. Existing OpenABL users can boot directly. Instructions and the source image hashes are in [INSTALL.md](docs/INSTALL.md).

SSH is enabled by default: user `root`, password `rocknix`. Its address is shown in Wi-Fi settings; SSH can be disabled in Settings.

## Updates and recovery

Open **Settings → System → Updates**. Leave **Test versions** enabled to see alpha releases from this repository. Downloading and installing are separate actions. Installation writes the inactive SD root slot, verifies its contents and only then changes the OpenABL boot entry. Restart to use the new version.

The running system remains available as **Previous version**. OpenABL also has a recovery entry. Offline updates use the same `banana-duolite-<version>.update.tar` package in `banana/updates` on the card. See [UPDATES.md](docs/UPDATES.md), including the read-only installed-firmware hash check.

Port versions, such as `0.1.0-alpha.32`, are independent of the pinned upstream BananaOS version. The top bar shows our Duo Lite alpha number.

## Games

Console icons appear before games are added. Copy your own games into the folders on the data partition; no games or user BIOS files are bundled.

| System | Folder under `roms/` | Emulator |
| --- | --- | --- |
| Nintendo DS | `nds` | BananaDS |
| Nintendo 3DS | `3ds` | Citra |
| PSP | `psp` | PPSSPP |
| Dreamcast | `dreamcast` | Flycast |
| Master System | `mastersystem` | Genesis Plus GX |
| Arcade | `mame` | MAME 2003-Plus |
| Amstrad CPC | `amstradcpc` | Caprice32 |
| Wii | `wii` | Dolphin |

GB/GBC, GBA, NES, SNES, Mega Drive, PlayStation, N64, PICO-8, C64 and ZX Spectrum are also included. MAME needs a **MAME 2003-Plus** ROM set. 3DS needs decrypted dumps or homebrew; CIA installation is not implemented. See [STATUS.md](docs/STATUS.md) for display and performance limits.

The standard home launcher groups emulators before apps. Press **X** to edit icon order, **A** to pick up/place and **B** to cancel a move. Touch **− / +** (or **L / R** while editing) chooses one to four rows. **Y** in editing toggles installed ports on home. The layout stays on writable storage across updates; see [Home menu](docs/HOME-MENU.md).

The original BananaOS in-game menu provides save/load, resume, brightness, restart and quit. **F + X** opens it. Built-in rumble has a global On/Off switch under Display & sound; see [RUMBLE.md](docs/RUMBLE.md) for game/emulator requirements. Slopetanium has its own home-menu tile. It installs PortMaster packages into `roms/ports`, where both PortMaster and the Ports shelf find them. Native Linux apps from their original GitHub releases get individual home-menu tiles; their files stay in `/data/store/apps` and shortcuts in `/data/store/tiles`. PortMaster and individual ports remain free to update themselves; Slopetanium runs from `/data/slopetanium/packages` and updates independently through its own upstream releases. Its settings, cache and backups stay in `/data/slopetanium/conf`; firmware only seeds a missing installation. On a fresh card, its first launch downloads and verifies the unchanged upstream PortMaster package if Wi-Fi is available.

## Build and contribute

Start with the [project documentation index](docs/README.md) and
[AGENTS.md](AGENTS.md). They record source ownership, scope, commit/release rules,
device-testing practice and the current development handoff.

```sh
git clone --recurse-submodules https://github.com/rzrbld/bananaos_duo.git
cd bananaos_duo
make test
make release                 # Docker, substantial disk space and build time
```

This repository contains only the port:

```text
upstream/   pinned BananaLinux and Buildroot submodules
patches/    changes to upstream code and the original game menu
overlay/    Duo Lite board files, packages and OS helpers
scripts/    prepare, build and release packaging
tests/      A/B update failure and release-feed tests
docs/       installation, status and maintenance
```

`make prepare` generates a complete source tree in `build/source`. Original menu sources are fetched at a pinned commit and verified by SHA-256. Build outputs and private bring-up logs stay out of Git. [BUILD.md](docs/BUILD.md) explains the workflow; [CONTRIBUTING.md](CONTRIBUTING.md) explains how to change the port.

## Credits and licenses

BananaOS, BananaDS, the launcher and the original menu are the work of **JorreFog and the Banana contributors**. Hardware support builds on **ROCKNIX**, Linux and Mesa. This port retains their attribution and links to exact source revisions in [sources.json](sources.json).

Port glue and documentation use the [MIT license](LICENSE). Existing files and patches retain their original licenses, including GPL-covered menu, kernel and emulator code. Releases include corresponding sources and license manifests. See [THIRD_PARTY.md](THIRD_PARTY.md).
