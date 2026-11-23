# Source provenance and licenses

This repository is a port layer over [JorreFog/BananaLinux](https://github.com/JorreFog/BananaLinux), with the original upstream copyright retained. Its complete attribution file remains in the upstream submodule and prepared source tree. The port does not replace component licenses with its own MIT license.

| Component | Source and pin | License / notices |
| --- | --- | --- |
| BananaLinux launcher and system | `upstream/BananaLinux`, commit in `sources.json` | Upstream MIT license and `THIRD_PARTY.md` |
| Slopetanium | `rzrbld/slopetanium`, pin in `sources.json` and package recipe; downloaded during build | MIT; BananaLinux compositor attribution retained in installed notices |
| Buildroot | `upstream/buildroot`, commit in `sources.json` | GPL-2.0 and package-specific licenses |
| Original game menu | JorreFog/BananaFront, commit and per-file hashes in `sources.json`; fetched during preparation | GPL-3.0; fetched `COPYING` is preserved and installed with provenance |
| ROCKNIX kernel support | `overlay/buildroot/board/duolite/SOURCES` | Linux/kernel patches GPL-2.0 and original per-file notices |
| OpenABL installer | Exact supplied ROCKNIX image and four SHA-256s in `openabl-source.json` | Original files and contents unchanged; not run by system updates |
| Qualcomm firmware | Pinned recipes for linux-firmware and ROCKNIX extra-firmware | Component-specific binary licenses/notices; Adreno firmware notices installed |
| Mesa Freedreno / Turnip | `overlay/buildroot/package/mesa3d-adreno` | Mesa MIT/SGI/Khronos notices |
| BananaDS | Upstream package pin plus `tools/duolite/patches` in the prepared tree | GPL-3.0 and its dependencies' licenses |
| RetroArch and added cores | Pinned upstream package recipes plus port packages | GPL for RetroArch/Citra/PPSSPP/Flycast/Dolphin/Caprice32; Genesis Plus GX and MAME 2003-Plus retain their original noncommercial licenses |

Release source archives include the prepared OS source, port patches, Buildroot and its collected source archives and license manifests. Package recipes record the exact downloaded revisions. Local-source packages are included through the prepared tree, in addition to Buildroot's legal-info archive. No homebrew test binaries or commercial games are distributed with the firmware.
