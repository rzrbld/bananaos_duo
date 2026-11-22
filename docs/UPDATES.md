# A/B updates

The Duo Lite uses the original BananaOS updater's release discovery, resumable downloads, SHA-256 verification, package format and inactive-root writer. Its board helper adds OpenABL BLS entries in place of RG DS extlinux entries.

The release feed is `https://api.github.com/repos/rzrbld/bananaos_duo/releases?per_page=20`. Alpha releases are public GitHub prereleases, controlled by the existing **Test versions** setting. The upstream password-protected beta server is not used for Duo Lite. A separate feed cache prevents old upstream results being reused.

## Layout and installation order

The SD card is `/dev/mmcblk0`: boot FAT on partition 1, root A on partition 2, root B on partition 3, writable data on partition 4. Internal Android storage is not an update target.

1. Lock the updater; check the running root, SD partition labels and inactive-slot mount state. Refuse while a game or another held job is running.
2. Check the package's board, device tree and complete checksums before writes. Duo Lite refuses RG DS and universal packages.
3. Preserve a working recovery entry. Fresh-card `/Image` paths are normalized into the running slot's directory first.
4. Make the running slot the default if an earlier pending update selected the inactive one. Remove the inactive kernel marker before writing its root.
5. Write and read back the inactive root. Copy and read back the kernel and DTB. An interrupted or corrupt write leaves that slot unavailable for switching.
6. Record the version and atomically replace `loader/entries/banana.conf` after a sync. The recovery entry still names the working system.
7. Restart when the user chooses. Games, saves, user RetroArch configuration, PortMaster and individual ports are retained.

This retains the previous version; it is not an automatic boot-count rollback system. If a complete update fails to start, select the recovery entry manually.

## Package contract

Each release includes:

- `banana-duolite-<version>.img.gz`: full image for a fresh card.
- `banana-duolite-<version>.update.tar`: one directory containing `Image`, `sm6125-retroid-pocket-duo-lite.dtb`, `rootfs.squashfs`, `VERSION`, `board` and `sha256sums`.
- `SHA256SUMS-duolite.txt`: hashes for every published asset; required by OTA discovery.
- `release-manifest.json`: source pins, component hashes and OpenABL provenance.
- A corresponding-source archive including prepared OS sources, Buildroot source archives, license manifests and the port.

The package's `VERSION` and filename match the port version in `/etc/banana/release`; `/etc/banana/version` retains the upstream version. Tags are `v<version>`. Increment both repository `VERSION` and `overlay/buildroot/board/duolite/RELEASE`, plus the top-bar `BUILD` number.

On a handheld, `update check`, `update download`, `update apply <package>`, `update status` and `update switch` are available at `/usr/libexec/banana/update`. Applying writes the other slot but does not reboot automatically.

Alpha25 predates the native OpenABL updater. Its one-time migration to Alpha26 runs the new OS updater from RAM against the verified update package; subsequent releases use Settings and the public release feed directly.
