do_install:append() {
    install -d ${D}${sysconfdir}/wpa_supplicant

    printf 'ctrl_interface=/run/wpa_supplicant\n\
ctrl_interface_group=0\n\
update_config=1\n\
\n\
network={\n\
    ssid="Căn Hộ LK L1.02 _5G"\n\
    psk="7979797979"\n\
    key_mgmt=WPA-PSK\n\
}\n' > ${D}${sysconfdir}/wpa_supplicant/wpa_supplicant.conf

    chmod 600 ${D}${sysconfdir}/wpa_supplicant/wpa_supplicant.conf
}

SYSTEMD_AUTO_ENABLE:${PN} = "enable"
SYSTEMD_SERVICE:${PN} = "wpa_supplicant@wlan0.service"