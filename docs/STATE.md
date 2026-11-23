# Development handoff

Last reviewed: **2026-11-23**. This file records a dated snapshot; check GitHub,
the device and local manifests before assuming a build is installed or published.
Stable project rules live in [AGENTS.md](../AGENTS.md), not in this snapshot.

## Versions and repositories

| Item | Verified state |
| --- | --- |
| Public firmware release | `v0.1.0-alpha.35`; later local development versions are not public OTA releases yet |
| Firmware source/candidate | `0.1.0-alpha.40`, complete local image built and checked; SDL audio shutdown fix plus startup-underrun recovery |
| Development handheld | Alpha39 was verified before this session's work; Alpha40 installation/verification is in progress and must be confirmed before declaring it installed |
| Slopetanium | Public `v0.3.1-beta`; firmware seed pin in `sources.json`; writable app was independently updated and tested on exFAT |
| GBA DS Duo | Fork PR [#1](https://github.com/rzrbld/gba-ds/pull/1) merged; `v1.6.1.1` tagged; CI release publication in progress |

The maintained local firmware checkout is `port/` inside the bring-up workspace.
The GBA DS fork checkout is `work/gba-ds-duo/`; Slopetanium is a separate sibling
repository. Paths and private device connection details belong to the workspace,
not public deployment configuration.

## Recent verified findings

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
  when closing a game. The Alpha40 candidate uses the existing nonblocking path
  and recovers startup underruns. Temporary testing with its built library ran
  about 59 FPS, recovered an underrun and exited normally; the launcher restored.
  This is software evidence, not a new user confirmation of audible output.
- Fork installer testing creates `GBA DS Duo.sh` without replacing the existing
  upstream `GBA DS.sh` tile or package. GBA DS remains a separately updated app.

## Outstanding checks and boundaries

- Complete/verify Alpha40 installation and the CI-built GBA DS release. Update
  this snapshot with the actual final states; do not infer them from queued jobs.
- Recheck audible output and physical panel orientation with the user when they
  return if those results have not been observed directly.
- Bluetooth pairing needs broader device testing. 3DS still combines screens on
  the upper panel; split-screen/touch integration is not implemented. Wii game
  compatibility and motion-dependent controls need broader testing.
- Headphone popping was user-confirmed fixed after Alpha32. Preserve that codec
  PA ordering and the working headset/built-in microphone routes.
- Keep the quiet fan ceiling and emergency policy; rumble is optional.

Private local evidence for this work is under `work/duolite/gba-ds-diagnosis/`
and `work/duolite/local40/`. Earlier verified image manifests and exFAT tests are
under `work/duolite/local39/`. These are workspace paths, intentionally untracked.
