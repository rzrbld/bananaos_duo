QCOM_RMTFS_VERSION = 1.1.1
QCOM_RMTFS_SITE = $(call github,linux-msm,rmtfs,v$(QCOM_RMTFS_VERSION))
QCOM_RMTFS_LICENSE = BSD-3-Clause
QCOM_RMTFS_LICENSE_FILES = LICENSE
QCOM_RMTFS_DEPENDENCIES = qcom-qrtr udev

define QCOM_RMTFS_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) CC="$(TARGET_CC)" CFLAGS="$(TARGET_CFLAGS)" LDFLAGS="$(TARGET_LDFLAGS) -lqrtr -ludev -lpthread"
endef

define QCOM_RMTFS_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/rmtfs $(TARGET_DIR)/usr/bin/rmtfs
endef

$(eval $(generic-package))
