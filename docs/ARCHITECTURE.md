# Architecture and source ownership

## Repositories and components

| Component | Maintained location | Change policy |
| --- | --- | --- |
| Duo Lite firmware | [rzrbld/bananaos_duo](https://github.com/rzrbld/bananaos_duo) | Port overlay, patch series, packaging, tests and firmware CI |
| BananaLinux | `upstream/BananaLinux`, pinned in `sources.json` | Clean submodule; port modifications live in patches/overlay |
| Buildroot | `upstream/buildroot`, pinned in `sources.json` | Clean submodule plus external board/package definitions |
| BananaFront menu | File hashes and commit in `sources.json` | Fetch originals and apply the menu integration patch; retain GPL notices |
| Kernel and device firmware | Board `SOURCES`, kernel patch series and package recipes | Preserve provenance; small evidence-backed hardware changes |
| Mesa Freedreno / Turnip | `overlay/buildroot/package/mesa3d-adreno` | Pinned drivers; select and verify the renderer for each emulator |
| BananaDS / RetroArch / cores | Pinned upstream and port package recipes | OS-managed launch, input and menu integration; retain user RA configuration |
| Slopetanium | [rzrbld/slopetanium](https://github.com/rzrbld/slopetanium) | Separate app repository, app CI/releases and independent self-update |
| PortMaster and ports | Original PortMaster releases and port repositories | Vanilla code; firmware owns platform glue, not package content |
| GBA DS Duo | [rzrbld/gba-ds](https://github.com/rzrbld/gba-ds), based on [kyannon/gba-ds](https://github.com/kyannon/gba-ds) | Separate authorized fork for portable ARMv8 builds and explicit panel mounting |
| OpenABL installer | `openabl-source.json` and the supplied ROCKNIX image | Exact original files with hash verification |

`sources.json` is authoritative for the main upstream pins; individual package
recipes pin additional dependencies. Do not duplicate full external repositories
into the port to make an integration change.

## Source-to-image flow

`clean submodules + pinned menu files + patches + overlay`
→ `make prepare` → generated `build/source`
→ Docker/Buildroot → image components → checks/legal information → CI release.

`patches/0001-duo-lite.patch` adapts BananaLinux; the original menu has its own
integration patch. `0004-slopetanium-home-apps.patch` connects home-menu native
apps. `overlay/buildroot/patches/sdl2/` contains OS SDL compatibility fixes.
Kernel changes are under the board's kernel patch directories. Edit the authored
inputs and regenerate; do not develop permanent changes only in the generated tree.

## Runtime ownership

| Location | Owner / purpose |
| --- | --- |
| Immutable root | OS executables, libraries, hardware defaults and launch helpers |
| SD boot partition + two root partitions | OpenABL entries and A/B kernel, DTB and SquashFS payloads |
| `/data/banana` | Persistent OS settings and update data |
| `/data/roms`, `/data/saves`, `/data/retroarch` | Games, saves and user emulator configuration |
| `/data/roms/ports` | PortMaster and installed ports |
| `/data/store/apps` | Slopetanium-managed native app payloads, isolated by repository |
| `/data/store/tiles` | Generated home-menu launchers for native apps |
| `/data/slopetanium/packages` | Writable Slopetanium application code |
| `/data/slopetanium/conf` | Slopetanium settings, release cache and backups |
| `/run`, `/tmp` | Transient state, test tools and runtime configuration |

The development card's data filesystem is exFAT. Code requiring symlinks or
executable bits must be adapted at the owning layer. OS launch helpers can execute
a script through Bash; copying a Unix directory layout verbatim is insufficient.

## Display and app launch

The upper panel's native scanout is 1080×1920; OS rotation produces a logical
1920×1080 top screen. The bottom is 1280×960. Read
`/etc/banana/hardware.env`; do not bake connector order into individual pages.
Rendering coordinates, touch coordinates and scanout orientation are distinct.

Slopetanium launches from its OS helper and installs apps without rewriting their
payload. The OS `run-store-app` helper launches generated app entries. GBA DS Duo
honors explicit per-display rotation and defaults its updater to the fork. Its
separate `GBA DS Duo` tile avoids replacing an installed upstream GBA DS entry.
