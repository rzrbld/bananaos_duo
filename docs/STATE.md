# Development handoff

Last reviewed: **2026-11-24**. This file records a dated snapshot; check GitHub,
the device and local manifests before assuming a build is installed or published.
Stable project rules live in [AGENTS.md](../AGENTS.md), not in this snapshot.

## Versions and repositories

| Item | Verified state |
| --- | --- |
| Public firmware release | `v0.1.0-alpha.35`; later local development versions are not public OTA releases yet |
| Current local firmware | `0.1.0-alpha.55`; signal-aware roaming and the corrected WCN3990 teardown fix over the stable base; experimental Venus remains separate |
| Development handheld | Alpha55 installed in slot A; active kernel, DTB and complete root hashes verified; DTB identical to Alpha46, stable kernel configuration unchanged, kernel rebuilt with the scoped Wi-Fi fix |
| Slopetanium | Public `v0.3.2-beta`; writable app independently updated from CI and all 34 packaged files verified; next nightly seed pin updated in `sources.json` |
| GBA DS Duo | Fork PR [#1](https://github.com/rzrbld/gba-ds/pull/1) merged; [v1.6.1.1](https://github.com/rzrbld/gba-ds/releases/tag/v1.6.1.1) published by CI and installed through Slopetanium; all 23 payload files matched the release ZIP |

The maintained local firmware checkout is `port/` inside the bring-up workspace.
The GBA DS fork checkout is `work/gba-ds-duo/`; Slopetanium is a separate sibling
repository. Paths and private device connection details belong to the workspace,
not public deployment configuration.

## Recent verified findings

- Alpha56 work: firmware CI run 45316271038 compiled and passed image/source
  checks, then failed at `legal-info` because tests had generated Python bytecode
  inside authored overlay directories, changing prepare's fingerprint. Preparation
  now excludes `__pycache__`, `.pyc` and `.pyo` from both fingerprint and overlay
  copying; its regression still detects real content/mode changes. The complete
  test-then-prepare sequence passed locally.
- The live fuel gauge and charge ratio agreed at 66%. The near-full launcher
  icon was a scale mismatch: its 1.6x frame was drawn at native asset size while
  its fill used the Duo's 2x logical scale. Status art now scales from its 1x
  dimensions to the actual UI scale. Real dark/light rendered regressions verify
  25%, 66% and 100% fills at 1x/1.6x/2x. No battery calibration was changed.
- Seven original transparent 32px console sprites replace generic icons for
  3DS, PSP, Dreamcast, Master System, MAME, Amstrad CPC and Wii. Their exact
  system aliases override the generic category map; user themes remain separate.
  Complete Alpha56 image and on-device validation are pending.

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
  The user confirmed clean, responsive real console streaming on restored
  Alpha46 with explicit 720p negotiation and ANGLE over native Turnip/Vulkan.
  They described this as the best streaming result on the handheld so far.
  The measured H.264 stream was 1280×720 at roughly 60 decoded frames/s;
  decoding remains explicitly software. GPU composition is accelerated.
  This does not establish button-to-photon latency or cloud-streaming behavior.
  App commit `afa7c4a` preserves the tested launcher settings;
  [Duo.4](https://github.com/rzrbld/greenlight/releases/tag/v2.4.2-duo.4)
  was built and published by CI. The downloaded ZIP matched the published
  checksum, passed ARM64/exFAT/native-driver checks and contained no browser
  profile or credential-store paths. Earlier Duo.3 was installed through Slopetanium and
  verified against all 598 packaged files, but its CPU composition was choppy.
  The successful Duo.4 trial used isolated code and an authenticated profile
  copy. The public CI release was then installed through Slopetanium and all
  598 packaged files matched its checksums. The successful authenticated profile
  was reused locally with the previous profile backed up; no profile content
  was read, printed or published. The installed release has the exact tested
  launcher flags; a subsequent user stream test is still separate from the trial.

- Greenlight Duo.6 was built/published by app CI and installed through
  Slopetanium; all 598 packaged files verified. Built-in face buttons now use
  Xbox positions (B→A, A→B, Y→X, X→Y). Home quits; Select+Start is no longer a
  quit chord. Navigation-loop tests cover menus/streams, chord pass-through and
  external Guide isolation. Physical confirmation of these new controls is pending.

- Wi-Fi diagnosis found no configured connected-state background scanning.
  A manual scan moved the Duo from a weaker 20 MHz link to an 80 MHz AP;
  local TCP measured about 299 Mbps down / 171 Mbps up with power saving on,
  versus 310 / 174 with it off. Original power saving was restored. The user
  then changed the farther AP; both now advertise channel 36 / 80 MHz, and
  the Duo is associated with the stronger point. Alpha53 adds a default
  `simple:15:-70:1800` background-roaming policy without pinning a BSSID,
  changing country codes or modifying saved credentials. It also includes
  `iw` for diagnostics. The weak threshold is below the measured healthy
  nearby link; the 30-minute healthy-link fallback avoids frequent scan jitter. This uses the verified Alpha46 kernel/DTB and excludes
  the experimental Venus changes. Source regressions and complete SD image
  validation passed. The local image reused the verified original Alpha46 root,
  changing only the authored Wi-Fi helper, release/build labels and adding the
  pinned ARM64 iw binary. All other original file contents were compared.
  Kernel/DTB are byte-identical to Alpha46. The complete A/B update was installed
  in slot A; all three active component hashes matched the image. Wi-Fi joined
  automatically after reboot, using channel 36 / 80 MHz with a reported
  433 Mbps receive rate. A bounded private monitor was started; user-observed
  walking/stream recovery is still pending. Android throughput has not been
  measured under the same conditions, so Android performance parity is unproven.

- Alpha53 walking feedback: the stream continued/recovered without reopening
  Greenlight. The user clarified that quality and frame rate normalized over
  about ten seconds, **not** that Wi-Fi was disconnected for ten seconds.
  Monitoring caught a same-IP AP transition with about a three-second ath10k
  old-key timeout. Both APs advertise Neighbor Report and BSS Transition, but
  the observed authentication suite is PSK without advertised FT.
  Alpha54 adapts David Heidelberg's WCN3990 pairwise-delete RFC, restricted to
  this hardware and explicit pairwise removal. The removal command is still
  sent; new keys, group keys, other hardware and send errors keep their checks.
  The actual C routine passed branch/error regressions. A clean stable-source
  kernel build passed with configuration identical to running Alpha53 and a DTB
  byte-identical to original Alpha46. Complete Alpha54 installed/hash-verified,
  but controlled handovers still took 3.3–3.8 seconds: the added guard incorrectly
  tested WMI_KEY_PAIRWISE as a bit, although its real value is zero. Alpha55
  instead checks mac80211's actual pairwise-key flag and keeps the WMI group
  exclusion. The regression now imports flag definitions from the real kernel
  headers rather than synthetic constants. Corrected kernel build/test passed;
  complete Alpha55 source/image checks and installed component verification
  passed. Controlled handovers completed in 582 ms and 399 ms with unchanged
  IP; the kernel logged about 255–260 ms from disconnect to association and no
  key timeout. The original AP was restored and the launcher left running.
  These are controlled idle tests, not a post-fix Xbox streaming measurement.
  The user's stream/quality recovery test is deferred until next session.
  CI run [45316271038](https://github.com/rzrbld/bananaos_duo/actions/runs/45316271038)
  was manually started on functional source commit `91c22ad`. It is a main-branch
  artifact build, not a public OTA release; completion is still pending.
  Upstream reference: https://lore.kernel.org/linux-wireless/20260918-ath10k-del-v1-1-53cd7a7d682b@ixit.cz/

- Experimental Venus work is preserved separately on
  [`experimental/venus-sm6125`](https://github.com/rzrbld/bananaos_duo/tree/experimental/venus-sm6125).
  Complete native and VA-API 720p clips produced correct pixels, but streaming
  showed green/black frames and repeated decode/teardown tests rebooted the
  device. Alpha52's power-handoff correction did not solve the second-session
  reset. The user requested rollback; the entire historical Alpha46 payload,
  including its device tree, was restored and hash-verified. Do not merge the
  experimental branch into stable/nightly or describe Venus streaming as working.

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

## Next session: user requests (2026-11-24)

- Battery indicator: Slopetanium showed about 69% after roughly three hours of
  testing/streaming while the OS launcher still appeared almost full. Compare
  their actual capacity sources and icon scaling before changing calibration.
- Redraw icons for the newly added consoles in the existing system style.
  Either use image generation or provide exact asset dimensions, transparency,
  formats and theme/style references so the user can generate them.
- Add Steam PC game streaming as an independently installable Slopetanium app.
  Evaluate a suitable ARM64 client; validate controller input, top touch, audio,
  aspect ratio and latency without bundling user authentication into releases.

## Outstanding checks and boundaries

- Recheck audible output and physical panel orientation with the user when they
  return if those results have not been observed directly.
- Bluetooth pairing needs broader device testing. 3DS still combines screens on
  the upper panel; split-screen/touch integration is not implemented. Wii game
  compatibility and motion-dependent controls need broader testing.
- Headphone popping was user-confirmed fixed after Alpha32. Preserve that codec
  PA ordering and the working headset/built-in microphone routes.
- Keep the quiet fan ceiling and emergency policy; rumble is optional.

Current local/installed versions are listed above. Public firmware remains
Alpha35 until a separate tagged CI release is published. Main-branch firmware
CI produces test artifacts; it does not publish a release automatically.

Latest private firmware/roaming evidence is under `work/duolite/local55/`, with
the preceding failed guard test under `work/duolite/local54/`. No device network
logs or credentials are committed.

Earlier private local evidence is under `work/duolite/gba-ds-diagnosis/`
and `work/duolite/local40/`. Earlier verified image manifests and exFAT tests are
under `work/duolite/local39/`. These are workspace paths, intentionally untracked.
