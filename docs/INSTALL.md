# Installation

Use the release `.img.gz` for a fresh microSD card. Flashing replaces the contents of the selected card. Verify the checksum, write the image with an image writer, then put it in the Duo Lite. The first boot prepares the writable data partition; the OS root remains immutable.

OpenABL must be installed on the handheld. Choose **Retroid Pocket Duo Lite** as the device tree. Enter Wi-Fi using the on-device keyboard. ROMs, saves, settings and update downloads live on the writable data partition.

## Optional OpenABL installation from Android

The boot partition's `openabl` directory is copied byte-for-byte from `ROCKNIX-SM6115.aarch64-20261101.img.gz`. Its four original files and hashes are recorded in [the provenance manifest](../overlay/buildroot/board/duolite/openabl-source.json). Neither the firmware build nor a BananaOS A/B update runs these scripts.

For the same manual rooted-Android procedure used by ROCKNIX:

1. Copy the entire folder to Android Internal Storage as `/sdcard/openabl`.
2. Run `backup_abl.sh` as root and keep the backup.
3. Run `flash_abl.sh` as root.
4. Reboot holding Volume Down, then select **Change boot mode** and start the SD system.

The included `restore_backup_abl.sh` is unchanged. Existing OpenABL installations do not need this procedure. Android installation itself was not executed during the port's packaging tests; the imported files and boot-partition layout were verified.

The image uses ROCKNIX's Android-visible Microsoft Basic Data partition type for the FAT boot volume. OpenABL reads its BLS entry in `loader/entries/banana.conf`.

## Recovery

After an update, choose **Previous version** in BananaOS or the recovery entry in OpenABL. These select the other root slot without replacing games or saves. If neither OS starts, a spare freshly written card can boot independently of the failed card.
