FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"
SRC_URI:append = " file://wifi-brcmfmac.cfg"

# Thêm config fragment cho WiFi Broadcom (brcmfmac)
KERNEL_CONFIG_FRAGMENTS:append = " wifi-brcmfmac.cfg"
