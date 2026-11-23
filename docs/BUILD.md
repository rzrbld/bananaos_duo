# Building and releases

Use Linux with Git, Python 3.12 or newer, Make, a C/C++ compiler and Docker. A full cold build downloads a toolchain and large emulator sources; allow several hours and approximately 50 GB or more of free disk space. `JOBS=4` is the default; set it for the available CPU/RAM.

```sh
git submodule update --init --recursive
make prepare
make test
JOBS=4 make release
```

Host launcher checks also need `libdrm-dev`, `libfreetype-dev`, `libasound2-dev` and `zlib1g-dev`. CI compiles the launcher and runs the unequal-panel tests. The Docker builder installs the cross-build dependencies itself.

`build/source` is generated from the clean pinned submodules, `patches/` and `overlay/`. Original menu files are downloaded at the BananaFront commit in `sources.json`; each file and its license are checked against SHA-256 before integration. Kernel support comes from the ROCKNIX revision recorded in the board's `SOURCES` file. Emulator and graphics recipes pin their versions separately.

After changing patches or overlay files, run `make clean-source && make prepare`. This removes only the generated source tree. Keep authored changes in the port, not in `build/source` or the upstream submodules. A fresh build output is appropriate after changing package recipes or major source pins; Buildroot incremental builds do not automatically rebuild every changed package.

Build work, downloaded archives and the compiler cache live in `build/work`. Final assets live in `dist`. `make check` verifies the built GPT/FAT/squashfs contents, native executables, release source, emulator assets and unchanged OpenABL files. `make release` also collects Buildroot legal information and bundles corresponding sources. No ROMs, BIOS files, network passwords or local bring-up logs are packaged.

If a source archive exceeds the release asset limit, it is split into numbered `.part000`, `.part001`, … files. Verify their checksums, concatenate them in order with `cat ...part* > sources.tar.gz`, then extract the gzip tar.

## Automation

The **Checks** workflow runs on main pushes and pull requests: source reconstruction, real updater tests against file-backed slots, the upstream A/B regression tests, hardware-policy tests, launcher compilation and panel tests.

The **Firmware** workflow runs nightly at **00:00 UTC / 03:00 Moscow**, or through **Run workflow**. Pushing commits or version tags does not start a full firmware build. Quick **Checks** still run on main pushes and pull requests.

Nightly builds use `main` and retain the complete image, update package, checksums and corresponding sources as the `duolite-firmware` Actions artifact for one day. These are test builds: they do not change the handheld's public release feed. Local builds may be installed on a development handheld; the nightly image can be tested independently on another card.

After validating a version, manually run **Firmware** with its matching `v*` tag selected to publish the release. The tag must match `VERSION` and the board's `RELEASE`. That run performs the same build, image checks, tests, source collection and checksum verification, uploads assets to a draft, and only then publishes the complete release. Alpha tags produce prereleases. Existing releases retain their verified assets; a rebuild never replaces them.

Source packaging collects the pinned GCC runtime and glibc sources from Bootlin, alongside its SDK configuration and the Buildroot license manifests.

## Updating upstream

Update a submodule deliberately, update its matching commit in `sources.json`, then rebase the patch series and regenerate the prepared tree. Do not follow a moving upstream branch at build time. Run tests, build the image and validate it on hardware before tagging a release. Pinned Actions commits are listed with their upstream release versions in the workflow files.
