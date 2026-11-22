LIBRETRO_PPSSPP_VERSION = fa50bb1976065c4f8b1b47af227d367fe9771555
LIBRETRO_PPSSPP_SITE = https://github.com/hrydgard/ppsspp.git
LIBRETRO_PPSSPP_SITE_METHOD = git
LIBRETRO_PPSSPP_GIT_SUBMODULES = YES
# Linux/libretro uses system FFmpeg and none of the mobile, web or test submodules.
LIBRETRO_PPSSPP_DL_ENV = GIT_CONFIG_COUNT=8 \
	GIT_CONFIG_KEY_0=submodule.pspautotests.update GIT_CONFIG_VALUE_0=none \
	GIT_CONFIG_KEY_1=submodule.ffmpeg.update GIT_CONFIG_VALUE_1=none \
	GIT_CONFIG_KEY_2=submodule.ios/MoltenVK.update GIT_CONFIG_VALUE_2=none \
	GIT_CONFIG_KEY_3=submodule.SDL/macOS.update GIT_CONFIG_VALUE_3=none \
	GIT_CONFIG_KEY_4=submodule.assets/debugger.update GIT_CONFIG_VALUE_4=none \
	GIT_CONFIG_KEY_5=submodule.ext/libadrenotools.update GIT_CONFIG_VALUE_5=none \
	GIT_CONFIG_KEY_6=http.lowSpeedLimit GIT_CONFIG_VALUE_6=1024 \
	GIT_CONFIG_KEY_7=http.lowSpeedTime GIT_CONFIG_VALUE_7=60
LIBRETRO_PPSSPP_LICENSE = GPL-2.0-or-later
LIBRETRO_PPSSPP_LICENSE_FILES = LICENSE.TXT
LIBRETRO_PPSSPP_DEPENDENCIES = sdl2 zlib libzip zstd ffmpeg freetype libpng libegl libgles
LIBRETRO_PPSSPP_CONF_OPTS = -DCMAKE_NO_SYSTEM_FROM_IMPORTED=ON -DBUILD_SHARED_LIBS=OFF \
	-DLIBRETRO=ON -DFORCED_CPU=aarch64 -DUSING_GLES2=ON -DUSING_EGL=OFF \
	-DUSING_FBDEV=ON -DVULKAN=OFF -DUSE_VULKAN_DISPLAY_KHR=OFF \
	-DUSING_X11_VULKAN=OFF -DUSE_WAYLAND_WSI=OFF -DUSING_QT_UI=OFF \
	-DUSE_SYSTEM_FFMPEG=ON -DUSE_SYSTEM_FREETYPE=ON -DUSE_SYSTEM_LIBZIP=ON \
	-DUSE_SYSTEM_LIBPNG=ON -DUSE_SYSTEM_ZSTD=ON -DUNITTEST=OFF \
	-DSIMULATOR=OFF -DHEADLESS=OFF -DUSE_DISCORD=OFF -DOPENXR=OFF

define LIBRETRO_PPSSPP_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/lib/ppsspp_libretro.so $(TARGET_DIR)/usr/lib/libretro/ppsspp_libretro.so
	mkdir -p $(TARGET_DIR)/usr/share/banana/duolite/system/PPSSPP
	cp -a $(@D)/assets/. $(TARGET_DIR)/usr/share/banana/duolite/system/PPSSPP/
	rm -rf $(TARGET_DIR)/usr/share/banana/duolite/system/PPSSPP/debugger
endef

$(eval $(cmake-package))
