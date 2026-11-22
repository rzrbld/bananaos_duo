ALSA_UCM_CONF_VERSION = 1.2.16.1
ALSA_UCM_CONF_SOURCE = alsa-ucm-conf-$(ALSA_UCM_CONF_VERSION).tar.bz2
ALSA_UCM_CONF_SITE = https://www.alsa-project.org/files/pub/lib
ALSA_UCM_CONF_LICENSE = BSD-3-Clause
ALSA_UCM_CONF_LICENSE_FILES = LICENSE

define ALSA_UCM_CONF_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/alsa
	cp -a $(@D)/ucm2 $(TARGET_DIR)/usr/share/alsa/
	cp -a $(BR2_EXTERNAL_BANANA_PATH)/board/duolite/ucm2/. $(TARGET_DIR)/usr/share/alsa/ucm2/
endef

$(eval $(generic-package))
