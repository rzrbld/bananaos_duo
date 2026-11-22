# Port status

Alpha firmware for **Retroid Pocket Duo Lite (SM6125 / Adreno 610)**. Tested on one handheld; broader game and hardware testing is still needed.

| Area | Status |
| --- | --- |
| Boot | Native Buildroot, immutable root, OpenABL BLS, SD A/B roots |
| Displays | Unequal native panels, rotated upper panel, widescreen launcher/apps and animation layouts |
| Wi-Fi | Scan, connect, saved-network reconnect and SSH tested |
| Bluetooth | BlueZ stack and firmware included; pairing/device compatibility needs broader testing |
| Cooling and LED | Fan settings and quiet policy implemented; emergency cooling retained; LED defaults to charging |
| Sleep and wake | Native suspend/resume and faster Wi-Fi wake path tested |
| Resume after timed power-off | BananaOS save-based resume; depends on emulator state support |
| Graphics | Mesa Freedreno GLES/KMS; Turnip Vulkan driver included; each emulator's selected renderer is documented in its recipe |
| Game menu | Original BananaFront menu adapted to the wide top display; save/load, resume, brightness, restart and quit tested |
| PortMaster | Vanilla installation with OS-managed paths/display/controller integration; application files and ports are not patched |
| Audio | Speaker/headphone routes and physical volume controls implemented; headset output/loudness confirmed. Built-in microphone passed an acoustic capture test. Headset microphone remains silent; see AUDIO.md. |

## Emulators

BananaDS runs with the Cortex-A73 target, JIT, Gengis and Banana 2D, including selected 2x rendering. Existing console cores use native GLES/KMS presentation. These settings do not guarantee a particular frame rate in every game.

The added Master System, CPC, MAME, PSP, Dreamcast, Wii and 3DS cores each rendered an authorized test game and passed original-menu pause/resume/quit checks. PSP save/load and 3DS D-pad movement were checked too. Installed-firmware PSP launch/menu checks passed after reboot. Tests used homebrew/freeware and temporary save paths; no test games are in release images.

**3DS:** Citra currently combines both emulated screens on the upper panel. Native split-panel and touchscreen integration are not implemented. Decrypted dumps and homebrew are supported by the loader; CIA installation is not implemented.

**Wii:** Dolphin uses Wiimote gamepad mapping and right-stick infrared pointing. Homebrew rendering was checked; commercial-game performance, motion-dependent games and controller extensions need testing.

**MAME:** the shipped core is MAME 2003-Plus, requiring its matching ROM set.

**PlayStation:** PCSX-ReARMed uses a user-supplied BIOS from `bios/` when available; its HLE fallback has compatibility limits.

Bring-up originally used ROCKNIX as a hardware reference, then moved to native BananaOS Buildroot. Release builds use the port's source recipes, not a repackaged ROCKNIX root filesystem.
