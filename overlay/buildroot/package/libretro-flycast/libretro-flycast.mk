LIBRETRO_FLYCAST_VERSION = 7adbf3caef251b153e348df3f469a0f35878339d
LIBRETRO_FLYCAST_SITE = https://github.com/flyinghead/flycast.git
LIBRETRO_FLYCAST_SITE_METHOD = git
LIBRETRO_FLYCAST_GIT_SUBMODULES = YES
# Native libretro has no standalone SDL UI or Windows/macOS/mobile frontends.
LIBRETRO_FLYCAST_DL_ENV = GIT_CONFIG_COUNT=12 \
	GIT_CONFIG_KEY_0=submodule.core/deps/Spout.update GIT_CONFIG_VALUE_0=none \
	GIT_CONFIG_KEY_1=submodule.core/deps/Syphon.update GIT_CONFIG_VALUE_1=none \
	GIT_CONFIG_KEY_2=submodule.core/deps/SDL.update GIT_CONFIG_VALUE_2=none \
	GIT_CONFIG_KEY_3=submodule.core/deps/freetype.update GIT_CONFIG_VALUE_3=none \
	GIT_CONFIG_KEY_4=submodule.core/deps/oboe.update GIT_CONFIG_VALUE_4=none \
	GIT_CONFIG_KEY_5=submodule.core/deps/libadrenotools.update GIT_CONFIG_VALUE_5=none \
	GIT_CONFIG_KEY_6=submodule.core/deps/gamesdk.update GIT_CONFIG_VALUE_6=none \
	GIT_CONFIG_KEY_7=submodule.core/deps/breakpad.update GIT_CONFIG_VALUE_7=none \
	GIT_CONFIG_KEY_8=submodule.core/deps/DreamPicoPort-API.update GIT_CONFIG_VALUE_8=none \
	GIT_CONFIG_KEY_9=submodule.core/deps/googletest.update GIT_CONFIG_VALUE_9=none \
	GIT_CONFIG_KEY_10=http.lowSpeedLimit GIT_CONFIG_VALUE_10=1024 \
	GIT_CONFIG_KEY_11=http.lowSpeedTime GIT_CONFIG_VALUE_11=60
LIBRETRO_FLYCAST_LICENSE = GPL-2.0-or-later
LIBRETRO_FLYCAST_LICENSE_FILES = LICENSE
LIBRETRO_FLYCAST_DEPENDENCIES = zlib libzip libegl libgles
LIBRETRO_FLYCAST_CONF_OPTS = -DCMAKE_NO_SYSTEM_FROM_IMPORTED=ON -DBUILD_SHARED_LIBS=OFF \
	-DLIBRETRO=ON \
	-DUSE_OPENGL=ON \
	-DUSE_GLES=ON \
	-DUSE_VULKAN=OFF \
	-DWITH_SYSTEM_ZLIB=ON \
	-DUSE_OPENMP=ON

define LIBRETRO_FLYCAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/flycast_libretro.so $(TARGET_DIR)/usr/lib/libretro/flycast_libretro.so
endef

$(eval $(cmake-package))
