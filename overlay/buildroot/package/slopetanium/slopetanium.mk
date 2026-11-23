# Build the pinned upstream application; keep its source and assets upstream.
SLOPETANIUM_VERSION = 8fb57d911ac838677c0a665d8ff2e5ec90a7919f
SLOPETANIUM_SITE = $(call github,rzrbld,slopetanium,$(SLOPETANIUM_VERSION))
SLOPETANIUM_LICENSE = MIT
SLOPETANIUM_LICENSE_FILES = LICENSE ui/third_party/LICENSE.BananaLinux
SLOPETANIUM_DEPENDENCIES = sdl2 freetype python3 host-pkgconf

define SLOPETANIUM_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/ui CROSS="$(TARGET_CROSS)" CXX="$(TARGET_CXX)" \
		PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" CXXFLAGS="$(TARGET_CXXFLAGS) -O2" \
		LDFLAGS="$(TARGET_LDFLAGS) -Wl,--gc-sections -Wl,--as-needed" OUT=slopetanium-ui
endef

define SLOPETANIUM_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/ui/slopetanium-ui $(TARGET_DIR)/usr/bin/slopetanium-ui
	mkdir -p $(TARGET_DIR)/usr/share/banana/rnds/icons $(TARGET_DIR)/usr/share/slopetanium $(TARGET_DIR)/usr/share/banana/apps/slopetanium/media
	cp -a $(@D)/port/slopetanium/app $(@D)/port/slopetanium/web $(@D)/port/slopetanium/assets $(TARGET_DIR)/usr/share/slopetanium/
	$(INSTALL) -m 0644 $(@D)/LICENSE $(TARGET_DIR)/usr/share/slopetanium/LICENSE
	cp -a $(@D)/ui/third_party/LICENSE.BananaLinux $(@D)/ui/third_party/README.md $(TARGET_DIR)/usr/share/slopetanium/
	touch $(TARGET_DIR)/usr/share/banana/apps/slopetanium/Slopetanium.app
	$(INSTALL) -m 0644 $(@D)/port/slopetanium/assets/icons/slopetanium-icon-96.png $(TARGET_DIR)/usr/share/banana/rnds/icons/slopetanium.png
endef

$(eval $(generic-package))
