# Audio diagnostics

Settings → Display & sound → Microphone test shows a live input meter.

- A records five seconds from the system's current microphone route.
- X plays that recording through the current audio output.
- B stops capture or playback, returns to settings and discards the recording.

The test keeps its audio in process memory. It creates no recording files and does not monitor the microphone through the speakers. Headset input selection follows the OS jack detection.

The utility does not prove that the device's microphone routing works: a silent input produces an empty meter and a silent recording. Built-in capture has passed the acoustic check below. The headset route still requires physical validation; do not treat startup noise as a successful microphone test.

## Duo Lite capture wiring

The built-in microphone is TX DMIC2 (gpio127/gpio128). Its PDM clock is supplied by the VA macro, while its samples reach the DSP over TX_CODEC_DMA_TX_3. The device tree registers VA as an auxiliary audio component and supplies these DAPM dependencies:

- TX DMIC2 ← VA DMIC2 ← VA_MCLK
- DMIC2 Pin ← MIC BIAS1

`qcom,dmic-sample-rate = <2400000>` selects the PDM clock rate. A separate VA capture PCM is deliberately not exposed: the device's DSP rejected AFE port 0xb021 in the bring-up test.

Hardware validation: capture a low-level 1 kHz speaker tone, then silence. During the tone, the microphone's 1 kHz component rose from below 0.3 sample units to over 370; it returned below 0.2 afterward. The measurements excluded the initial capture transient.

Headset ADC2 maps through SoundWire master port 1, channel bit 0. Its DAPM input and TX selection must both use channel 0 (`TX SWR_INPUT0`, `SWR_MIC0`). The known-working physical headset still returned zeros with this correction, analog gain enabled and all SoundWire inputs tested. Headset capture remains unresolved; this mapping correction is not a validated microphone fix.

References: [Qualcomm downstream TX macro](https://github.com/LineageOS/android_kernel_xiaomi_sm6125/blob/lineage-24.0/techpack/audio/asoc/codecs/bolero/tx-macro.c), [Linux VA macro](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/sound/soc/codecs/lpass-va-macro.c).
