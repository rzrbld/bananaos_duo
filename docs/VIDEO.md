# Duo Lite hardware video decoding

The board uses the SM6125 (trinket) Venus 5.x VPU, HFI v4xx / AR50. Its
Android firmware identifies itself as `VIDEO.VE.5.4-00058-PROD-4`. Adreno
Freedreno/Turnip handles graphics; selecting Vulkan does not enable this VPU.
Do not use the SM6115/QCM2290 Venus 6.0 configuration for this board.

Alpha48 includes the SM6125 video clock controller, Venus resources and
device-tree nodes. These are adapted from
[PeacockProject's SM6125 kernel](https://github.com/PeacockProject/linux_sm6125_ginkgo/tree/db3f159aa32c11688ee4873a6218ea113052fee6),
with original copyright/license headers retained in the patches. The DT
register cells match our kernel's 64-bit SoC address/size format. The Alpha47 interconnect experiment was withdrawn: the system has no matching
CPU/GPU/display bandwidth consumers, and the shared bus must retain the working
baseline policy. Venus currently uses that baseline bandwidth configuration;
full dynamic interconnect scaling needs a separate system-wide integration.

The firmware helper runs before udev's initial device trigger. It discovers
Android's `modem_a` / `modem_b` partitions through sysfs, maps the partition
read-only and mounts its FAT filesystem read-only. It validates and copies the
complete signed `image/venus.mdt` + `venus.b00`–`venus.b04` set into
`/run/banana/firmware/qcom/sm6125/`, then unmounts and detaches the mapping.
The kernel's firmware search path includes that RAM directory; normal root
firmware lookup remains available. The board requests `qcom/sm6125/venus.mdt`.
Android partitions are never written, and device-extracted blobs are not
included in the repository or public image. Missing/incompatible firmware is
logged without preventing the launcher from booting.

Validation must distinguish these steps:

1. Fresh kernel patch application, kernel/modules/DTB compilation and full-image
   checks, including the unchanged OpenABL folder.
2. Complete A/B update and verification of the installed kernel, DTB and root.
3. Venus firmware initialization and V4L2 decoder registration on hardware.
4. Explicit `ffmpeg -c:v h264_v4l2m2m` decoding of the local diagnostic clip,
   checking completion and kernel faults rather than accepting a device node.
5. Electron/Greenlight selecting a working hardware decoding backend.

A V4L2 decoder does not by itself make Electron's VA-API backend use it. Until
step 5 is verified, Greenlight remains software-decoded even when Turnip/Vulkan
composition is enabled. See current validation status in [STATE.md](STATE.md).

Alpha47 registered the decoder and completed 180 local 720p60 H.264 frames at
about 113 frames/s with `h264_v4l2m2m`, exit 0. A subsequent test coincided with
an unexpected restart; the user also reported a sluggish launcher. Alpha46 was
restored through the normal A/B switch. This is not stable-decoder validation.
Alpha48 removes the experimental global interconnect driver and its paths to
isolate that regression. Repeat decode/close and idle stability remain required.
