VENUS_VAAPI_VERSION = 37e1030aba11f66e303e4f5fb0c3a13e2a78265e
VENUS_VAAPI_SITE = $(call github,snowf14k3,venus-vaapi-driver,$(VENUS_VAAPI_VERSION))
VENUS_VAAPI_LICENSE = MIT
VENUS_VAAPI_LICENSE_FILES = LICENSE
VENUS_VAAPI_DEPENDENCIES = host-pkgconf libva libdrm
VENUS_VAAPI_CONF_OPTS = -Dprobe_limit=8

# Buildroot's libva searches /usr/lib/va; Electron's bundled libva may use
# /usr/lib/dri. Both resolve to the same OS-owned backend. MSM is the DRM
# driver name, not a second implementation.
define VENUS_VAAPI_DRIVER_ALIASES
	mkdir -p $(TARGET_DIR)/usr/lib/va
	ln -sf ../dri/venus_drv_video.so $(TARGET_DIR)/usr/lib/va/venus_drv_video.so
	ln -sf ../dri/venus_drv_video.so $(TARGET_DIR)/usr/lib/va/msm_drv_video.so
	ln -sf venus_drv_video.so $(TARGET_DIR)/usr/lib/dri/msm_drv_video.so
endef
VENUS_VAAPI_POST_INSTALL_TARGET_HOOKS += VENUS_VAAPI_DRIVER_ALIASES

$(eval $(meson-package))
