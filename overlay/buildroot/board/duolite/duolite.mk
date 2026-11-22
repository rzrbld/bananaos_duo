BANANA_DUOLITE = $(BR2_EXTERNAL_BANANA_PATH)/board/duolite

define BANANA_DUOLITE_KERNEL_PATCHES
	for p in $(sort $(wildcard $(BANANA_DUOLITE)/linux-patches/*.patch)) $(sort $(wildcard $(BANANA_DUOLITE)/banana-kernel-patches/*.patch)); do \
		if patch --dry-run --batch --forward -p1 -d $(LINUX_DIR) < $$p >/dev/null 2>&1; then \
			patch --batch --forward -p1 --no-backup-if-mismatch -d $(LINUX_DIR) < $$p || exit 1; \
		elif patch --dry-run --batch -R -p1 -d $(LINUX_DIR) < $$p >/dev/null 2>&1; then \
			echo "Already upstream: $$p"; \
		else \
			patch --batch --forward -p1 --no-backup-if-mismatch -d $(LINUX_DIR) < $$p; exit 1; \
		fi; \
	done
	cp $(BANANA_DUOLITE)/dts/*.dts $(LINUX_DIR)/arch/arm64/boot/dts/qcom/
	cat $(BANANA_DUOLITE)/fan.dtsi >> $(LINUX_DIR)/arch/arm64/boot/dts/qcom/sm6125-retroid-pocket-duo-lite.dts
	grep -q sm6125-retroid-pocket-duo-lite.dtb $(LINUX_DIR)/arch/arm64/boot/dts/qcom/Makefile || \
		echo 'dtb-$$(CONFIG_ARCH_QCOM) += sm6125-retroid-pocket-duo-lite.dtb' >> $(LINUX_DIR)/arch/arm64/boot/dts/qcom/Makefile
endef
LINUX_POST_PATCH_HOOKS += BANANA_DUOLITE_KERNEL_PATCHES

define BANANA_DUOLITE_BANANADS_PATCH
	$(APPLY_PATCHES) $(@D) $(BR2_EXTERNAL_BANANA_PATH)/../tools/duolite/patches '*.patch'
endef
BANANADS_POST_PATCH_HOOKS += BANANA_DUOLITE_BANANADS_PATCH
BANANADS_CONF_OPTS += -DBANANADS_CPU=cortex-a73 -DBANANADS_PGO=off -DBANANADS_GENGIS=ON -DCMAKE_NO_SYSTEM_FROM_IMPORTED=ON

# Keep the SDK's imported standard include directory as -I, avoiding the GCC
# external-toolchain include_next failure caused by CMake's -isystem ordering.
VULKAN_TOOLS_CONF_OPTS += -DCMAKE_NO_SYSTEM_FROM_IMPORTED=ON

# Rebuild only the DTB when its local policy changes during bring-up.
define BANANA_DUOLITE_REFRESH_DTS
	cp $(BANANA_DUOLITE)/dts/*.dts $(LINUX_DIR)/arch/arm64/boot/dts/qcom/
	cat $(BANANA_DUOLITE)/fan.dtsi >> $(LINUX_DIR)/arch/arm64/boot/dts/qcom/sm6125-retroid-pocket-duo-lite.dts
endef
LINUX_PRE_BUILD_HOOKS += BANANA_DUOLITE_REFRESH_DTS

# Store and Doda Kvarter share the same pinned platform code.
define BANANA_DUOLITE_DODAKVARTER_PLATFORM
	$(APPLY_PATCHES) $(@D) $(BR2_EXTERNAL_BANANA_PATH)/patches/rocknixds-store 0004-kms-support-rotated-unequal-panels.patch
endef
DODAKVARTER_POST_PATCH_HOOKS += BANANA_DUOLITE_DODAKVARTER_PLATFORM

# Kryo 260 implements ARMv8.0; do not emit the RG DS Cortex-A55 ARMv8.2 ISA.
LIBRETRO_BANANANES_MAKE_OPTS += ARCH_FLAGS="-mcpu=cortex-a73" NO_PGO=1
