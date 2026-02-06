require recipes-core/images/core-image-minimal.bb

# Tiện ích dev & SSH
IMAGE_FEATURES += "ssh-server-dropbear tools-debug debug-tweaks package-management"

# Gói phục vụ IO/protocol test (Python + MQTT + HTTP + UVC/GStreamer)
IMAGE_INSTALL:append = " \
  nano htop i2c-tools v4l-utils ethtool iperf3 tcpdump \
  python3 python3-pip python3-aiohttp python3-paho-mqtt \
  gstreamer1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  libgpiod python3-gpiod \
  packagegroup-ppe-mw ppe-infer \
  wpa-supplicant ppe-wifi-config \
  linux-firmware-rpidistro-bcm43430 \
  kernel-module-brcmfmac kernel-module-brcmutil \
"