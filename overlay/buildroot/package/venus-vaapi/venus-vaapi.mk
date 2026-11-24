VENUS_VAAPI_VERSION = 37e1030aba11f66e303e4f5fb0c3a13e2a78265e
VENUS_VAAPI_SITE = $(call github,snowf14k3,venus-vaapi-driver,$(VENUS_VAAPI_VERSION))
VENUS_VAAPI_LICENSE = MIT
VENUS_VAAPI_LICENSE_FILES = LICENSE
VENUS_VAAPI_DEPENDENCIES = host-pkgconf libva libdrm
VENUS_VAAPI_CONF_OPTS = -Dprobe_limit=8

# Keep the experimental backend opt-in. Buildroot libva searches /usr/lib/va,
# while Electron's bundled libva uses /usr/lib/dri. Do not register an MSM
# auto-selection alias until streaming correctness and teardown are validated.
define VENUS_VAAPI_DRIVER_ALIASES
	mkdir -p $(TARGET_DIR)/usr/lib/va
	ln -sf ../dri/venus_drv_video.so $(TARGET_DIR)/usr/lib/va/venus_drv_video.so
	rm -f $(TARGET_DIR)/usr/lib/va/msm_drv_video.so $(TARGET_DIR)/usr/lib/dri/msm_drv_video.so
endef
VENUS_VAAPI_POST_INSTALL_TARGET_HOOKS += VENUS_VAAPI_DRIVER_ALIASES

$(eval $(meson-package))
