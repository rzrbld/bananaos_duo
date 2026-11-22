# Rumble

Alpha33 adds **Settings → Display & sound → Rumble**, with On/Off choices. It defaults to On. Off stops the built-in motor immediately and suppresses both gamepad effects and clients opening the standalone haptic device. The choice is stored in the OS power configuration and applied again at boot.

The existing Retroid gamepad exposes standard Linux `FF_RUMBLE`, backed by the AW86927 haptic supplier. Controller identity and button mappings stay the same. SDL and RetroArch can discover rumble normally, including SDL libraries supplied by PortMaster. No PortMaster installation or individual port is patched.

Games and their emulator/controller mode must support vibration. N64 Rumble Pak selection remains an emulator choice; this setting does not replace a Memory Pak or change its saves. Hardware without game rumble, such as the original PSP, does not acquire it automatically.

BananaDS connects its DS Rumble Pak callbacks to bounded force-feedback effects. On the Duo it inserts the virtual accessory when the gamepad advertises rumble; DSi mode is excluded. `input.rumble_pak=false` can disable that virtual accessory for a game override. The global OS Off setting still suppresses physical vibration without restarting a game.

The motor stops for suspend, device removal and effect-owner exit. Re-enabling rumble or waking the device does not replay old requests. Hardware I/O stays on the supplier's worker; input callbacks do not perform I2C transfers.

Validation so far: ARM64 compile checks for both drivers, launcher and BananaDS; fresh pinned BananaDS plus OS patches matches the compiled source; isolated daemon on/off tests and instrumented tests of the actual kernel routing/gating functions pass. Physical validation of the CI-built Alpha33 remains pending.
