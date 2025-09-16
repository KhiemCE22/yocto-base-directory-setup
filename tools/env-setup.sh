#!/usr/bin/env bash
set -euo pipefail

# Run this inside the container
TOP=$(pwd)

# Choose branch
YOCTO_BRANCH=scarthgap

# Clone layers if missing
[ -d poky ] || git clone -b ${YOCTO_BRANCH} https://git.yoctoproject.org/poky
[ -d meta-openembedded ] || git clone -b ${YOCTO_BRANCH} https://github.com/openembedded/meta-openembedded.git
[ -d meta-raspberrypi ] || git clone -b ${YOCTO_BRANCH} https://github.com/agherzan/meta-raspberrypi.git

echo "Done. Next:
  source poky/oe-init-build-env build-rpi5
  # then edit conf/bblayers.conf and conf/local.conf
  # e.g., MACHINE = \"raspberrypi5\"
  #       DL_DIR = \"${TOP}/downloads\"
  #       SSTATE_DIR = \"${TOP}/sstate-cache\"
  # bitbake core-image-minimal
"
