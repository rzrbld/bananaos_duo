# Build the pinned upstream application; keep its source and assets upstream.
SLOPETANIUM_VERSION = c3933298d40c9f4d1e54ccceda8730562fe92492
SLOPETANIUM_SITE = $(call github,rzrbld,slopetanium,$(SLOPETANIUM_VERSION))
SLOPETANIUM_LICENSE = MIT
SLOPETANIUM_LICENSE_FILES = LICENSE ui/third_party/LICENSE.BananaLinux
SLOPETANIUM_DEPENDENCIES = sdl2 freetype python3 host-python3 host-pkgconf

define SLOPETANIUM_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/ui CROSS="$(TARGET_CROSS)" CXX="$(TARGET_CXX)" \
		PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" CXXFLAGS="$(TARGET_CXXFLAGS) -O2" \
		LDFLAGS="$(TARGET_LDFLAGS) -Wl,--gc-sections -Wl,--as-needed" OUT=slopetanium-ui
endef

define SLOPETANIUM_INSTALL_TARGET_CMDS
	rm -rf $(TARGET_DIR)/usr/share/slopetanium
	mkdir -p $(TARGET_DIR)/usr/share/banana/rnds/icons $(TARGET_DIR)/usr/share/slopetanium $(TARGET_DIR)/usr/share/banana/apps/slopetanium
	$(HOST_DIR)/bin/python3 $(SLOPETANIUM_PKGDIR)/make-seed.py $(@D) $(TARGET_DIR)/usr/share/slopetanium/seed.zip
	printf 'v0.3.0-beta\n' > $(TARGET_DIR)/usr/share/slopetanium/seed-version
	touch $(TARGET_DIR)/usr/share/banana/apps/slopetanium/Slopetanium.app
	$(INSTALL) -m 0644 $(@D)/port/slopetanium/assets/icons/slopetanium-icon-96.png $(TARGET_DIR)/usr/share/banana/rnds/icons/slopetanium.png
endef

$(eval $(generic-package))
