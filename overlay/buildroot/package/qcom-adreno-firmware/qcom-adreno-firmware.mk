QCOM_ADRENO_FIRMWARE_VERSION = 20251011
QCOM_ADRENO_FIRMWARE_SITE = https://gitlab.com/kernel-firmware/linux-firmware/-/raw/$(QCOM_ADRENO_FIRMWARE_VERSION)/qcom
QCOM_ADRENO_FIRMWARE_SOURCE = a630_sqe.fw
QCOM_ADRENO_FIRMWARE_EXTRA_DOWNLOADS = \
	https://gitlab.com/kernel-firmware/linux-firmware/-/raw/$(QCOM_ADRENO_FIRMWARE_VERSION)/LICENSE.qcom \
	$(QCOM_ADRENO_FIRMWARE_SITE)/NOTICE.txt
QCOM_ADRENO_FIRMWARE_LICENSE = Proprietary
QCOM_ADRENO_FIRMWARE_LICENSE_FILES = LICENSE.qcom NOTICE.txt
QCOM_ADRENO_FIRMWARE_REDISTRIBUTE = YES

define QCOM_ADRENO_FIRMWARE_EXTRACT_CMDS
	cp $(QCOM_ADRENO_FIRMWARE_DL_DIR)/a630_sqe.fw $(@D)/
	cp $(QCOM_ADRENO_FIRMWARE_DL_DIR)/LICENSE.qcom $(@D)/
	cp $(QCOM_ADRENO_FIRMWARE_DL_DIR)/NOTICE.txt $(@D)/
endef

define QCOM_ADRENO_FIRMWARE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/a630_sqe.fw $(TARGET_DIR)/lib/firmware/qcom/a630_sqe.fw
	$(INSTALL) -D -m 0644 $(@D)/LICENSE.qcom $(TARGET_DIR)/usr/share/licenses/qcom-adreno-firmware/LICENSE.qcom
	$(INSTALL) -D -m 0644 $(@D)/NOTICE.txt $(TARGET_DIR)/usr/share/licenses/qcom-adreno-firmware/NOTICE.txt
endef

$(eval $(generic-package))
