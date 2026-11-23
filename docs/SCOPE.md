# Project scope

Ship a native BananaOS firmware for the **Retroid Pocket Duo Lite**, using
Buildroot and an immutable root with recoverable SD A/B updates. ROCKNIX and
Android provide hardware references; the firmware is not a renamed ROCKNIX
filesystem. The device is SM6125 / Adreno 610 despite the reference image's
`SM6115` filename. Select the Duo Lite device tree in OpenABL.

The port owns boot integration, native Linux hardware support, graphics,
dual-panel presentation, input, quiet cooling, charging LED behavior, networking,
audio and microphones, power handling, the original BananaOS launcher/menu, and
system integration for emulators and independently installed apps.

Preserve these boundaries:

- The boot card may carry the original OpenABL installer, unchanged. Firmware
  updates do not install a bootloader, modify Android or write internal storage.
- The OS supplies libraries, device profiles and launch helpers. A game or port
  failing is not permission to edit its files or updater. Diagnose timing,
  renderer selection, CPU instructions, dependencies and paths at the proper layer.
- PortMaster remains vanilla. Slopetanium selects packages and delegates ports
  to it. Native apps come from each application's own release assets.
- When an upstream app actually needs a source fix, maintain it transparently in
  its own fork and update feed. GBA DS is an explicitly authorized example.
- Firmware seeds missing app installations. It must not overwrite a separately
  updated Slopetanium or user settings on every boot or OS update.
- Keep the original menu design and behavior. UI extensions must use each
  panel's logical dimensions and preserve both layers of the theme background.
- Resume after timed power-off is emulator save-state based. Do not describe it
  as a validated kernel RAM hibernation feature. Suspend/wake and shutdown are
  separate paths with separate tests.

Include emulator cores, icons and empty ROM folders without requiring users to
add games first. Do not bundle commercial games, user BIOS files, test ROMs or
personal configuration. Homebrew tests require redistributable sources and
temporary storage; a recipe containing a core does not establish game compatibility.

Changes must preserve the quiet fan mode, standard controller mapping, speaker/
headphone switching, microphone routes and existing save/configuration files.
Keep emergency thermal protection; Android vendor governor settings are measured
references, not interchangeable mainline Linux controls.
