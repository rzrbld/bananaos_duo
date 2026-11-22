QCOM_QRTR_VERSION = 1.2
QCOM_QRTR_SITE = $(call github,linux-msm,qrtr,v$(QCOM_QRTR_VERSION))
QCOM_QRTR_LICENSE = BSD-3-Clause
QCOM_QRTR_LICENSE_FILES = LICENSE
QCOM_QRTR_INSTALL_STAGING = YES
QCOM_QRTR_DEPENDENCIES =
QCOM_QRTR_CONF_OPTS = -Dqrtr-ns=enabled -Dsystemd-service=disabled

$(eval $(meson-package))
