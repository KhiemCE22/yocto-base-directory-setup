SUMMARY = "PPE inference (static ONNX) service"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://detect_static_onnx.py \
    file://ppe-detect-static.service \
    file://ppe_model.onnx \
    file://classes.txt \
    file://static_img.jpg \
    file://ppe-infer-tmpfiles.conf \
"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "ppe-detect-static.service"

RDEPENDS:${PN} = "\
    python3-core \
    python3-numpy \
    python3-pillow \
    opencv \
    onnxruntime \
    systemd \
"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/detect_static_onnx.py ${D}${bindir}/detect_static_onnx.py

    # Model
    install -d ${D}/opt/models
    install -m 0644 ${WORKDIR}/ppe_model.onnx ${D}/opt/models/ppe_model.onnx
    install -m 0644 ${WORKDIR}/classes.txt    ${D}/opt/models/classes.txt
    install -m 0644 ${WORKDIR}/static_img.jpg ${D}/opt/models/static_img.jpg

    # Persist data
    install -d ${D}${localstatedir}/lib/ppe

    # Service
    install -d ${D}${sysconfdir}/systemd/system
    install -m 0644 ${WORKDIR}/ppe-detect-static.service ${D}${sysconfdir}/systemd/system/ppe-detect-static.service

    # Tmpfiles config
    install -d ${D}${libdir}/tmpfiles.d
    install -m 0644 ${WORKDIR}/ppe-infer-tmpfiles.conf ${D}${libdir}/tmpfiles.d/ppe-infer.conf
}

FILES:${PN} += " \
    ${bindir}/detect_static_onnx.py \
    /opt/models/ppe_model.onnx \
    /opt/models/classes.txt \
    /opt/models/static_img.jpg \
    ${localstatedir}/lib/ppe \
    ${libdir}/tmpfiles.d/ppe-infer.conf \
    ${sysconfdir}/systemd/system/ppe-detect-static.service \
"
SYSTEMD_AUTO_ENABLE = "enable"
