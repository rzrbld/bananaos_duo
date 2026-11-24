# Development handoff

Last reviewed: **2026-11-24**. This file records a dated snapshot; check GitHub,
the device and local manifests before assuming a build is installed or published.
Stable project rules live in [AGENTS.md](../AGENTS.md), not in this snapshot.

## Versions and repositories

| Item | Verified state |
| --- | --- |
| Public firmware release | `v0.1.0-alpha.35`; later local development versions are not public OTA releases yet |
| Current local firmware | Alpha46 fully restored/hash-verified; this branch preserves the failed Alpha52 Venus experiment |
| Development handheld | Alpha45 running in slot B; kernel, DTB and complete immutable root matched the checked local image; gamepad registered, actual edit/normal grid scanouts checked and exact saved layout restored |
| Slopetanium | Public `v0.3.2-beta`; writable app independently updated from CI and all 34 packaged files verified; next nightly seed pin updated in `sources.json` |
| GBA DS Duo | Fork PR [#1](https://github.com/rzrbld/gba-ds/pull/1) merged; [v1.6.1.1](https://github.com/rzrbld/gba-ds/releases/tag/v1.6.1.1) published by CI and installed through Slopetanium; all 23 payload files matched the release ZIP |

The maintained local firmware checkout is `port/` inside the bring-up workspace.
The GBA DS fork checkout is `work/gba-ds-duo/`; Slopetanium is a separate sibling
repository. Paths and private device connection details belong to the workspace,
not public deployment configuration.

## Recent verified findings

- Alpha46 restores upper touchscreen initialization after the first
  display modeset and provides per-output compositor assignments. An initial
  live reprobe registered the existing Himax driver, and the user confirmed
  accurate top-panel touch in Greenlight. Native UI and SDL coordinate checks
  cover rotation, unequal panels and filtering a disabled lower output. The
  full image and source checks passed locally. Complete Alpha46 was A/B-installed
  in slot A; active kernel, DTB and complete immutable root hashes matched the
  built image. Both touchscreens registered automatically after reboot, with
  upper DSI-1 and lower DP-1 output assignments. The user subsequently confirmed
  top touch in the app and a real console stream. Sleep/resume still needs a
  separate touch regression check. A fresh SDL build exposed a short-context audio
  patch failure; its hunks are consolidated against the pinned SDL tarball,
  preserving the existing nonblocking writes, refill polling and prefill policy.

- Greenlight is an independent app at `rzrbld/greenlight`, not firmware content.
  CI published Duo.3, installed through Slopetanium and checked against all 598
  packaged files. Its software-rendering fallback produces video/audio/input
  but is choppy. Separate Electron42 + explicit ANGLE Turnip/Vulkan diagnostics
  now show a moving real console stream, confirmed smoother by the user; this
  configuration is not yet a published app release. Default ANGLE OpenGL tests
  on Electron42 and 45 froze the physical image and could stall GPU cleanup.
  Turnip test decoding remains software: the latest short sample measured
  about 5.7 ms decode time, 5 ms network RTT and 0.2 ms jitter buffering.
  Frame-arrival to browser-presentation estimates were about 32–33 ms; these
  are not measurements of button-to-photon latency.

- [Venus 5.4 bring-up](VIDEO.md): Alpha49 is installed and its kernel, DTB and
  complete root match the checked image. The user confirmed normal launcher
  responsiveness after the experimental interconnect driver was removed.
  Direct `h264_v4l2m2m` decoded the complete generated 720p60 clip at about
  148 fps; all 480 frame hashes matched the software reference. The kernel
  decoder has therefore produced correct pixels, separately from streaming.
  The device-signed Android firmware is staged read-only into RAM at boot.

- The VA-API bridge needed a VA 1.22 entry point for Electron's bundled libva;
  native firmware libva is 1.23. With that compatibility fix, actual 720p
  H.264 streaming reached Venus at roughly 60 decoded frames/s, but the user
  saw green/black frames. Other renderer/backend tests froze or restarted the
  device. The upstream adapter discarded the baseline no-reordering VUI and
  enabled zero display delay only for HEVC. A constrained-baseline-specific
  fix preserved all 480 pixels/frame hashes in an offline header-reconstruction
  test and in a complete on-device VA-API hardware decode, which then exited
  normally. A subsequent early-stop/second-context test still rebooted.

- Alpha52 compiled and passed full image/source checks, then was A/B-installed
  and hash-verified. Its first direct decode/early close completed and logged
  `vcodec power handoff uses genpd hwmode`, confirming `HW_CTRL_TRIGGER` selected
  the intended path. The second session after idle still rebooted the device.
  The flag correction therefore did **not** establish stable resume/teardown.
  Further hardware tests stopped, and the user requested return to Alpha46.
  The original Alpha46 kernel, DTB and entire root were restored through normal
  A/B updating and matched their historical hashes. Its device tree has no
  experimental Venus node. Root and network settings/user data were preserved.

- This work is isolated on `experimental/venus-sm6125`; main/nightly source
  stays on Alpha46. Do not merge or publish it as a stable firmware. The VA-API
  backend remains opt-in, with no MSM auto-selection aliases. Next investigation
  must cover power resume beyond the verified genpd callback, and producer
  synchronization for CPU-written exported video surfaces. Repeating the same
  on-device renderer/decoder trials without a relevant fix only reproduces resets.

- Greenlight fork commit `eb71ce1` adapts upstream resolution PR #1752 and
  defaults Duo to 720p, with separate 1080p/1440p/Auto and bitrate controls.
  Protocol and gamepad tests, the actual app build and ARM64 packaging passed.
  An isolated private payload received 1280×720 H.264 rather than the earlier
  2560×1440. Installed app code/profile were not replaced; no new public app
  release has been tagged. The user confirmed improved response, with remaining
  corruption in the accelerated rendering experiment.

- Alpha45 removes the multi-row frame and page counter, reuses the themed
  horizontal rail for touch page navigation, enlarges the selected grid icon by
  10% with a bold system-accent outline, and uses normal themed face buttons for
  editing. The one-row bubble/carousel remains. Source and image checks passed;
  real-icon tests verify blue/red selection in dark/light themes, page scrubbing,
  edit-only zoom, normal footer actions and retained ordering/collection links.
  Complete Alpha45 was A/B-installed and its active kernel, DTB and full root
  matched the built image. A brief installed input-event test captured three-row
  edit and normal scanouts, then restored the original row count and exact
  writable layout bytes. Actual 1280×960 scanouts show the requested styling.

- Alpha44 incorporates the user's correction to the home UI: the original
  bubble/carousel remains in one row, compact grids remain at two to four rows,
  and the original normal face buttons return at every density (X is Edit).
  Zoom buttons and their hit targets exist only while editing. Source checks,
  real launcher previews and the expanded input/rendered regression passed,
  including inactive hidden zoom targets and the normal X footer at all densities.
  The complete firmware passed image checks and A/B installation; its active
  kernel, DTB and full root hashes matched. Actual 1280×960 scanout shows the
  restored one-row bubble, carousel and footer without normal-mode zoom buttons.
  The writable layout file's checksum was unchanged across the update.

- Alpha43 adds the standard Dark/Light home editor (X, A pick/place, B cancel),
  one-to-four-row density (touch −/+ or editing L/R), and optional installed-port
  home shortcuts (editing Y). Emulators precede apps by default; custom stable-ID
  ordering, density and port visibility persist in writable home-layout.conf.
  Source checks, actual-library regressions and rendered/input tests passed;
  real launcher entry-point previews covered all densities, dark/light themes and
  unequal panels. Tests cover collection remapping, canonical port statistics,
  canceled moves, rescan/reinstallation and settings retention. Alpha43 was built
  completely, image-checked, A/B-installed and hash-verified. Its running 1280×960
  lower-panel capture shows the new menu and icons; the user requested the one-row/footer restoration recorded above. Ports/PortMaster and Slopetanium's own views remain separate.

- Alpha41 fixed stale Qualcomm submission/DSP positions after prepare. The
  silent hardware probe advanced 31,680 frames per 0.6 s after both explicit
  prepare and XRUN recovery, versus 2,880 / 1,920 on Alpha40. The user then heard
  audio but reported distortion. An emulator-free SDL test reproduced repeated
  underruns. Alpha42 prefills two playback periods in a three-period ring and
  polls refill availability briefly; capture buffering is unchanged. Installed
  Alpha42 consumed 196,608 bytes of queued 48 kHz stereo S16 silence in one second
  without logged underruns, versus 71,680 on Alpha41. A controlled GBA DS test
  using the complete candidate library ran 59.3–60 FPS, advanced the PCM pointer
  at 48 kHz and exited normally with temporary saves. The installed-firmware test
  also completed normally, and the user confirmed that GBA DS audio sounded okay
  on Alpha42. This confirmation is specific to the reported playback issue.

- Slopetanium v0.3.2-beta caches successful startup checks for one hour across
  launches; only stale repositories are refreshed. Manual X / Check for updates
  bypasses the cache, and failed network checks can retry after a minute. Existing
  periodic intervals are preserved; new settings default to hourly. All nine
  saved timestamps stayed unchanged in the Duo preview and the installed release
  performed zero automatic rechecks on reopening. Menus no longer fade in;
  retained shelf composition and solid-colour texture fills reduced the measured
  first-open submission from about 630 ms to 270 ms in the balanced test profile.
  The installed normal-helper test measured about 330 ms cold / 150 ms warm;
  timings vary with workload. Existing layout/pixel tests and ten new cache
  regressions passed. An installed-API test also confirmed zero startup check
  jobs followed by one successful forced manual refresh of a fresh entry.

- Alpha38 restored gamepad registration by making rumble optional. A failed
  haptic provider must not defer or prevent the controller probe.
- Alpha39 fixed Slopetanium's exFAT startup and moved its code to writable
  storage. Its actual-card self-update/rollback and settings retention passed.
- Slopetanium v0.3.1-beta recognizes legacy PortMaster launchers without port
  metadata while retaining native-app detection. Vurus used the PortMaster path;
  the original GBA DS ZIP installed through the native-app path.
- Upstream GBA DS v1.6 crashes on this CPU at `ldaddal` (`0x463960`); the CPU's
  feature list lacks LSE atomics. The Linux build used `-mcpu=cortex-a55`.
  The authorized fork uses ARMv8-A plus tuning for both the app and mGBA.
- The fork rotates the final GPU target using OS-provided panel mounting. Its
  pixel/pointer tests pass at all four right angles. The real device produced a
  1920×1080 logical top screenshot and generated its library logos without SIGILL.
- Real gameplay exposed an OS SDL audio-thread hang in blocking ALSA playback
  when closing a game. Alpha40 uses the existing nonblocking path
  and recovers startup underruns. Temporary testing with its built library ran
  about 59 FPS, recovered an underrun and exited normally; the launcher restored.
  This is software evidence, not a new user confirmation of audible output.
- Fork installer testing creates `GBA DS Duo.sh` without replacing the existing
  upstream `GBA DS.sh` tile or package. GBA DS remains a separately updated app.
  The CI-built v1.6.1.1 installation matched all 23 packaged files; the upstream
  executable hash was unchanged. Its installed-release gameplay/exit smoke test
  on Alpha40 passed (about 57 FPS in the measured interval), with temporary saves
  and automatic launcher restoration. The store core exited after installation.

## Outstanding checks and boundaries

- Recheck audible output and physical panel orientation with the user when they
  return if those results have not been observed directly.
- Bluetooth pairing needs broader device testing. 3DS still combines screens on
  the upper panel; split-screen/touch integration is not implemented. Wii game
  compatibility and motion-dependent controls need broader testing.
- Headphone popping was user-confirmed fixed after Alpha32. Preserve that codec
  PA ordering and the working headset/built-in microphone routes.
- Keep the quiet fan ceiling and emergency policy; rumble is optional.

Alpha40 component verification is recorded in the local installed-image manifest.
The fan tachometer read about 4,570 RPM after reboot; its quiet policy is retained.
Public firmware remains Alpha35 until a separate CI release is published. The
installed Alpha40 immutable root is unchanged by the independent store update;
the next nightly seeds v0.3.2-beta for fresh cards.

Private local evidence for this work is under `work/duolite/gba-ds-diagnosis/`
and `work/duolite/local40/`. Earlier verified image manifests and exFAT tests are
under `work/duolite/local39/`. These are workspace paths, intentionally untracked.
