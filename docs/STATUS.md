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
| Audio | Speaker/headphone routes and physical volume controls implemented; headset output/loudness confirmed. Built-in microphone passed an acoustic capture test. Headset microphone capture is user-confirmed after correcting its SoundWire mapping. Alpha31 speaker/headphone hotplug passed the user test; the headphone pop fix was user-confirmed on Alpha32. See AUDIO.md. |
| Rumble | Alpha33 adds standard gamepad force feedback, BananaDS Rumble Pak hooks and a global on/off switch. CI-build hardware validation pending; see RUMBLE.md. |

## Emulators

BananaDS runs with the Cortex-A73 target, JIT, Gengis and Banana 2D, including selected 2x rendering. Existing console cores use native GLES/KMS presentation. These settings do not guarantee a particular frame rate in every game.

The added Master System, CPC, MAME, PSP, Dreamcast, Wii and 3DS cores each rendered an authorized test game and passed original-menu pause/resume/quit checks. PSP save/load and 3DS D-pad movement were checked too. Installed-firmware PSP launch/menu checks passed after reboot. Tests used homebrew/freeware and temporary save paths; no test games are in release images.

Alpha34 adds all seven systems to **Settings → Other systems → Buttons** and **Emulators**. Emulators lists installed cores even when only one is available; compatible downloaded alternatives appear automatically. Buttons assigns L2/R2/L3/R3 actions and swaps A/B and X/Y per system. The native Duo launcher applies these through temporary append configuration, including SDL trigger-axis suppression; user RetroArch files are retained. Detailed core-specific options remain in RetroArch's in-game menu. Automated settings coverage and control-helper checks pass; installed-firmware testing is pending the CI build.

**3DS:** Citra currently combines both emulated screens on the upper panel. Native split-panel and touchscreen integration are not implemented. Decrypted dumps and homebrew are supported by the loader; CIA installation is not implemented.

**Wii:** Dolphin uses Wiimote gamepad mapping and right-stick infrared pointing. Homebrew rendering was checked; commercial-game performance, motion-dependent games and controller extensions need testing.

**MAME:** the shipped core is MAME 2003-Plus, requiring its matching ROM set.

**PlayStation:** PCSX-ReARMed uses a user-supplied BIOS from `bios/` when available; its HLE fallback has compatibility limits.

Bring-up originally used ROCKNIX as a hardware reference, then moved to native BananaOS Buildroot. Release builds use the port's source recipes, not a repackaged ROCKNIX root filesystem.


## Android reference measurements

Read from this Duo Lite over ADB on 2026-11-22. These are reference measurements, not additional BananaOS performance presets.

| Android mode | CPU governor | Little / big minimum (MHz) | KGSL maximum / minimum power-level index |
| --- | --- | --- | --- |
| Standard | schedutil | 1017.6 / 1056 | 3 / 4 |
| Performance | schedutil | 1420.8 / 1401.6 | 2 / 3 |
| High Performance | performance | 1612.8 / 1804.8 | 0 / 1 |

CPU ceilings were 1804.8 / 2016 MHz. Android kept the GPU's `msm-adreno-tz` governor, hardware clock gating and an 80 ms idle timer. Its frequency table spans 320–950 MHz; the mode-specific KGSL power-level limits narrow that range. These vendor controls cannot be copied directly to the mainline MSM driver.

Android fan PWM uses a 50,000 ns period. Quiet measured 8,000 ns duty (16%), about 4,800 RPM; Sport measured 15,000 ns (30%), about 7,440 RPM. Smart varied around 20% / 5,640 RPM during observation; its complete temperature curve has not been obtained. The existing Linux quiet ceiling remains in force.

Android exposes `s2idle`, asynchronous suspend and sync-on-suspend, with a 20-second freezer timeout. CPU0 exposes WFI and a deeper `silver-c3` state. A comparative Android suspend/wake timing measurement is still outstanding.
