# Audio diagnostics

Settings → Display & sound → Microphone test shows a live input meter.

- A records five seconds from the system's current microphone route.
- X plays that recording through the current audio output.
- B stops capture or playback, returns to settings and discards the recording.

The test keeps its audio in process memory. It creates no recording files and does not monitor the microphone through the speakers. Headset input selection follows the OS jack detection.

The utility does not prove that the device's microphone routing works: a silent input produces an empty meter and a silent recording. Built-in capture has passed the acoustic check below. Headset capture was also confirmed by the user after the SoundWire mapping correction; startup noise alone is not evidence of working capture.

## Duo Lite capture wiring

The built-in microphone is TX DMIC2 (gpio127/gpio128). Its PDM clock is supplied by the VA macro, while its samples reach the DSP over TX_CODEC_DMA_TX_3. The device tree registers VA as an auxiliary audio component and supplies these DAPM dependencies:

- TX DMIC2 ← VA DMIC2 ← VA_MCLK
- DMIC2 Pin ← MIC BIAS1

`qcom,dmic-sample-rate = <2400000>` selects the PDM clock rate. A separate VA capture PCM is deliberately not exposed: the device's DSP rejected AFE port 0xb021 in the bring-up test.

Hardware validation: capture a low-level 1 kHz speaker tone, then silence. During the tone, the microphone's 1 kHz component rose from below 0.3 sample units to over 370; it returned below 0.2 afterward. The measurements excluded the initial capture transient.

Android testing on this same Duo confirmed both microphones work. Its device tree places ADC2 on TX master port 3, channel bit 1, and its mixer profile remaps ADC2 to ADC3. The Linux test configuration now uses the five-port Bolero TX layout, slave-port mapping `<2 3 4 5>`, the ADC2 master-channel override, and `TX SWR_INPUT2` / `SWR_MIC2`. The old three-port layout put ADC capture onto the reserved PCM-out port. The new route still requires a physical capture test before it can be called working.

The user confirmed headset capture works after correcting the SoundWire mapping. Android-style headphone companders were disabled again after a playback regression during the trial; the corrective profile retains the previous LOHIFI output mode. Pops at boot and emulator transitions remained unresolved through Alpha31. Jack-change testing on both Alpha27 and Alpha29 exposed a stalled stream and an unbounded launcher write; the corrective build uses nonblocking writes and a bounded wait so route changes can release the PCM.

References: [Qualcomm downstream TX macro](https://github.com/LineageOS/android_kernel_xiaomi_sm6125/blob/lineage-24.0/techpack/audio/asoc/codecs/bolero/tx-macro.c), [Linux VA macro](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/sound/soc/codecs/lpass-va-macro.c).

Installed Alpha31 validation: three consecutive two-second capture / one-second silent-playback cycles completed without errors or stalls. The user confirmed headset audio, speaker audio after unplugging, and headset audio after reconnecting. The existing quiet fan policy was retained (PWM 32, approximately 4,500 RPM).

Alpha32 tests a driver-level headphone PA ordering change, adapted from [Jonathan Marek's WCD938x fix](https://lkml.iu.edu/hypermail/linux/kernel/2511.3/00064.html). It moves headphone amplifier enable/disable into the playback mute callback, inside the active SoundWire stream, and enables the amplifier after its supply settle delay. Capture callbacks leave playback untouched; repeated mute calls do not unbalance IRQ enables. An instrumented test executes the actual driver helpers to check those invariants. After installing the complete Alpha32 firmware, the user confirmed that the headphone popping was gone. The installed codec module hash matched the tested build.

## SDL game shutdown

Alpha40 also addresses an independent userspace shutdown failure. A live GBA DS
trace showed `SDL_CloseAudioDevice` joining its playback thread while that thread
was blocked inside ALSA playback/poll. SDL's nonblocking ALSA path keeps writes
interruptible when the audio thread is disabled. Its availability wait now also
recovers startup underruns, as the write path already does, instead of marking
the audio device permanently disconnected.

Temporary hardware testing with the library from the complete Alpha40 candidate
recovered a startup underrun, ran a game at about 59 FPS and exited normally.
That test restored the launcher and original library mount. It does not establish
a new user confirmation of audible output, jack hotplug or microphone behavior;
those remain separate regression checks. The kernel headphone PA ordering and
microphone routing are unchanged by this SDL patch.
