# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
#
# The following license files were not able to be identified and are
# represented as "Unknown" below, you will need to check them yourself:
#   LICENSE
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=4ad4271aecccecc014d14016e2e20245"

SRC_URI = "git://github.com/ntduong31/EdgeVisionRT.git;protocol=https;branch=master \
           file://0001-Remove-ncnn-from-deps-to-use-system-provider.patch \
           "

# Modify these as desired
PV = "1.0+git"
SRCREV = "2ab1588df2bf985096494c195b7461b2ed74398c"

S = "${WORKDIR}/git"

# NOTE: unable to map the following CMake package dependencies: Vulkan OpenCV ncnn
# NOTE: the following library dependencies are unknown, ignoring: B
#       (this is based on recipes that have previously been built and packaged)
DEPENDS = "ncnn opencv"

inherit cmake

# Tối ưu hóa tập lệnh ARM NEON cho Pi 5
TARGET_CXXFLAGS += "-march=armv8.2-a+fp16+dotprod"
# Dùng tạm cho QEMU
#TARGET_CXXFLAGS += "-march=armv8-a+simd"
EXTRA_OECMAKE = "-DCMAKE_BUILD_TYPE=Release -DNCNN_VULKAN=OFF"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 yolo_inference ${D}${bindir}

    install -d ${D}${datadir}/edgevisionrt/models
    install -m 0644 ${S}/models/yolov8n_ncnn_model/*.param ${D}${datadir}/edgevisionrt/models
    install -m 0644 ${S}/models/yolov8n_ncnn_model/*.bin ${D}${datadir}/edgevisionrt/models

    install -d ${D}${datadir}/edgevisionrt/videos
    install -m 0644 ${S}/human.mp4 ${D}${datadir}/edgevisionrt/videos/
}

FILES:${PN} += "${bindir}/yolo_inference ${datadir}/edgevisionrt/models/*"
FILES:${PN} += "${datadir}/edgevisionrt/videos/*"

