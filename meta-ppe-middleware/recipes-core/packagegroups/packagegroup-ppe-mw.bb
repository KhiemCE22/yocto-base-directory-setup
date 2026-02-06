SUMMARY = "Middleware stack for PPE detection"
DESCRIPTION = "Python runtime, OpenCV, ONNX Runtime, MQTT client, Flask, utilities"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

inherit packagegroup

RDEPENDS:${PN} = "\
    python3-core \
    python3-pip \
    python3-numpy \
    python3-pillow \
    python3-paho-mqtt \
    python3-flask \
    opencv \
    onnxruntime \
    gstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    htop \
    i2c-tools \
    ppe-telemetry-c \
    "

# Tùy board, nếu có tăng tốc phần cứng thì thêm:
# RDEPENDS:${PN}:append:rpi = " v4l-utils "
