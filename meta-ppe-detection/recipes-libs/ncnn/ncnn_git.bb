SUMMARY = "NCNN: High-performance neural network inference framework"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=d2141d1a2c978a089d3de7a67db0bbd2"

SRC_URI = "git://github.com/Tencent/ncnn.git;protocol=https;branch=master"
SRCREV = "${AUTOREV}"
S = "${WORKDIR}/git"

inherit cmake

# Cấu hình tối ưu cho ARMv8 (NEON) và tắt các tính năng không cần thiết
EXTRA_OECMAKE += "-DNCNN_VULKAN=OFF -DNCNN_BUILD_EXAMPLES=OFF -DNCNN_PYTHON=OFF -DNCNN_OPENMP=ON -DNCNN_SHARED_LIB=ON"

# 1. Loại bỏ libncnn.so khỏi package -dev (mặc định Yocto tự thêm vào đây)
FILES_SOLIBSDEV = ""

# 2. Đưa tất cả file .so vào package chính
FILES:${PN} += "${libdir}/libncnn.so"

# 3. Giữ nguyên bỏ qua lỗi QA
INSANE_SKIP:${PN} += "dev-so"

# 4. Gom các file cmake vào đúng chỗ
FILES:${PN}-dev += "${libdir}/cmake"

# 5. (Mẹo nhỏ) Thêm dòng này để Yocto không coi package chính là trống 
# nếu lỡ như file .so vẫn bị hụt
ALLOW_EMPTY:${PN} = "1"