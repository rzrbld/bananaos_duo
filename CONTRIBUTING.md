# Contributing

Read [AGENTS.md](AGENTS.md) and the [documentation index](docs/README.md).
[DEVELOPMENT.md](docs/DEVELOPMENT.md) covers commits and CI;
[ARCHITECTURE.md](docs/ARCHITECTURE.md) identifies the owning repository and layer.

Please report the port release number, handheld model, emulator/app and a reproducible sequence. Remove Wi-Fi credentials and other private data from logs before attaching them.

Keep changes small and in the appropriate place:

- `overlay/` adds Duo Lite files and build packages.
- `patches/0001-duo-lite.patch` changes the pinned BananaLinux tree.
- `patches/0002-original-menu-integration.patch` adapts the fetched original menu.
- `sources.json` and the upstream submodules pin external source revisions.

Preserve upstream attribution and original licenses. Do not commit built images, ROMs, BIOS files, credentials, downloaded source trees or raw device logs. Release assets belong in GitHub Releases.

Keep emulator/app integration in OS-managed helpers and immutable profiles. Avoid modifying PortMaster, its updater, port scripts or game data. Preserve user RetroArch configuration and the unchanged OpenABL folder.

Run `make test` and the relevant host tests. Changes to the boot/update path require failure-path tests and hardware verification. Firmware release tags must match `VERSION` and the board's `RELEASE` file. Describe the behavior tested and any remaining limitations in the PR.

Include `Co-authored-by: Codex <noreply@openai.com>` in every authored commit.
Use `[skip ci]` for OS commits that should wait for nightly validation. Local
complete firmware builds may update the development handheld; public assets are
built and published only through GitHub Actions. Update the focused docs and
[STATE.md](docs/STATE.md) when handing off verified work.
