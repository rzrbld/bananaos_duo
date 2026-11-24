# Wi-Fi scanning policy

The Duo Lite uses wpa_supplicant with its saved networks on writable storage.
Initial connection and reconnect after losing the link scan normally, with
exponential backoff when no saved network is available.

Background searches for a better access point while already connected are off
by default. This keeps their off-channel scanning out of streaming sessions.
Advanced opt-in is the writable file `/data/banana/wifi-roaming` containing `on`;
`off` or a missing file keeps the feature disabled. A Wi-Fi restart applies a
changed policy. Per-network overrides in manually maintained profiles are still
supported. No permanent BSSID pin is added.

The radio-driver key-removal fix remains enabled: disabling scheduled searches
does not revert that fix. Actual roaming, packet latency and video performance
are separate checks. Do not assume adequate bulk throughput proves low jitter.
Network credentials and raw radio logs do not belong in Git.
