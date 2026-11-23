# Touchscreens

Duo Lite has two independent evdev touchscreens. ROCKNIX's device tree and
driver patches identify the upper controller as Himax HX83112A on
`4a88000.i2c` and the lower controller as FocalTech FT5452 on `4c80000.i2c`.
The existing `BANANA_TOUCH` variable still identifies the lower panel;
`BANANA_TOUCH_TOP` identifies the upper one.

On the development card, the upper I2C device existed and its driver module
was loaded, but no driver was bound and no input device was registered.
Retrying `drivers_probe` registered it immediately. Greenlight's compositor
received the hotplug event, and the user confirmed correct top-screen taps.
The firmware now retries an unbound upper controller after the launcher's
first successful modeset. An already-bound controller is left alone.

Udev assigns `WL_OUTPUT=DSI-1` to upper touch and `WL_OUTPUT=DP-1` to lower
touch. Compositors can therefore keep each device on its physical display,
including when an app disables one output. No global calibration matrix is
applied: compositor output transforms already handle panel orientation.

BananaOS's direct-evdev input maps each touchscreen into its own logical
canvas, with the inverse of the scanout rotation. It uses the top canvas
width instead of reusing the lower panel's 4:3 width. SDL's OS-owned Banana
panel backend similarly identifies the source touchscreen, rotates top-only
touches and ignores lower-panel events while only the upper panel is shown.
The legacy RG DS bottom-only mapping remains when upper metadata is absent.
Independent apps that read evdev directly receive native coordinates and
must apply their own display transforms, as Greenlight/Weston already does.

Run `python3 tests/test-touch.py` after preparing sources. For the compiled
SDL source, run `tools/duolite/test-touch-sdl.py` with the path to
`src/video/dummy/SDL_bananapanels.c`. The tests cover physical corners against
the real scanout mapper, unequal sizes, both rotations, disabled-panel
filtering, probe failures and leaving a bound controller untouched.
