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
	-Dplatforms= -Dllvm=disabled -Dglx=disabled -Dglvnd=disabled \
	-Degl=enabled -Dgbm=enabled -Dopengl=true -Dgles1=disabled -Dgles2=enabled \
	-Dgallium-rusticl=false -Dmicrosoft-clc=disabled -Dvideo-codecs= \
	-Dgallium-va=disabled -Dbuild-tests=false -Dvalgrind=disabled \
	-Dlibunwind=disabled -Dlmsensors=disabled

$(eval $(meson-package))
