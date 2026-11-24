MESA3D_ADRENO_VERSION = 26.3.1
MESA3D_ADRENO_SOURCE = mesa-$(MESA3D_ADRENO_VERSION).tar.xz
MESA3D_ADRENO_SITE = https://archive.mesa3d.org
MESA3D_ADRENO_LICENSE = MIT, SGI, Khronos
MESA3D_ADRENO_LICENSE_FILES = docs/license.rst licenses/MIT licenses/SGI-B-2.0
MESA3D_ADRENO_INSTALL_STAGING = YES
MESA3D_ADRENO_PROVIDES = libegl libgles libgbm
MESA3D_ADRENO_DEPENDENCIES = host-bison host-flex host-python-glslang host-python-mako host-python-packaging host-python-pyyaml libdrm expat zlib vulkan-headers
MESA3D_ADRENO_CONF_OPTS = \
	-Dgallium-drivers=freedreno -Dvulkan-drivers=freedreno -Dfreedreno-kmds=msm \
	-Dllvm=disabled -Dglvnd=disabled \
	-Degl=enabled -Dgbm=enabled -Dopengl=true -Dgles1=disabled -Dgles2=enabled \
	-Dgallium-rusticl=false -Dmicrosoft-clc=disabled -Dvideo-codecs= \
	-Dgallium-va=disabled -Dbuild-tests=false -Dvalgrind=disabled \
	-Dlibunwind=disabled -Dlmsensors=disabled

ifeq ($(BR2_PACKAGE_MESA3D_ADRENO_DESKTOP),y)
MESA3D_ADRENO_PROVIDES += libgl
MESA3D_ADRENO_DEPENDENCIES += xlib_libX11 xlib_libXext xlib_libXdamage xlib_libXfixes xlib_libXrandr xlib_libXxf86vm xlib_libxshmfence xorgproto libxcb
MESA3D_ADRENO_CONF_OPTS += -Dplatforms=x11 -Dglx=dri -Dglx-direct=true
else
MESA3D_ADRENO_CONF_OPTS += -Dplatforms= -Dglx=disabled
endif

$(eval $(meson-package))
