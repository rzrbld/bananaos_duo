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

The **Firmware** workflow builds complete images on `v*` tags or manual dispatch. Manual builds retain downloadable Actions artifacts. A matching version tag additionally publishes a GitHub release after build, image verification, tests, source collection and checksum verification succeed. Alpha tags produce prereleases. Assets upload to a draft first; publishing the draft makes the complete release discoverable by the handheld.

Tag builds publish directly from the verified build job to GitHub Releases. Manual-build Actions artifacts are retained for one day. Source packaging also collects the pinned GCC runtime and glibc sources from Bootlin, alongside its SDK configuration and the Buildroot license manifests.

The first hardware-tested release can be published from an identical local source tree and verified build. An existing published release is retained when its tag's workflow finishes; CI never replaces those assets.

## Updating upstream

Update a submodule deliberately, update its matching commit in `sources.json`, then rebase the patch series and regenerate the prepared tree. Do not follow a moving upstream branch at build time. Run tests, build the image and validate it on hardware before tagging a release. Pinned Actions commits are listed with their upstream release versions in the workflow files.
