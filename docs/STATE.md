# Development handoff

Last reviewed: **2026-11-23**. This file records a dated snapshot; check GitHub,
the device and local manifests before assuming a build is installed or published.
Stable project rules live in [AGENTS.md](../AGENTS.md), not in this snapshot.

## Versions and repositories

| Item | Verified state |
| --- | --- |
| Public firmware release | `v0.1.0-alpha.35`; later local development versions are not public OTA releases yet |
| Current local firmware | `0.1.0-alpha.42`, complete local image built and checked; Qualcomm PCM recovery plus SDL playback prefill/refill fixes |
| Development handheld | Alpha42 running in slot A; kernel, DTB and complete immutable root matched the checked local image; gamepad registered and launcher restored |
| Slopetanium | Public `v0.3.2-beta`; writable app independently updated from CI and all 34 packaged files verified; next nightly seed pin updated in `sources.json` |
| GBA DS Duo | Fork PR [#1](https://github.com/rzrbld/gba-ds/pull/1) merged; [v1.6.1.1](https://github.com/rzrbld/gba-ds/releases/tag/v1.6.1.1) published by CI and installed through Slopetanium; all 23 payload files matched the release ZIP |

The maintained local firmware checkout is `port/` inside the bring-up workspace.
The GBA DS fork checkout is `work/gba-ds-duo/`; Slopetanium is a separate sibling
repository. Paths and private device connection details belong to the workspace,
not public deployment configuration.

## Recent verified findings

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
