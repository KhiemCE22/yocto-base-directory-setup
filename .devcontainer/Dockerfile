FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USERNAME=yocto

RUN apt-get update && apt-get install -y --no-install-recommends \
    gawk wget git-core diffstat unzip texinfo gcc-multilib build-essential chrpath socat cpio \
    python3 python3-pip python3-pexpect python3-git python3-jinja2 xz-utils debianutils iputils-ping \
    libegl1-mesa libsdl1.2-dev xterm zstd liblz4-tool file locales rsync curl ca-certificates \
    bc jq pigz bmap-tools parted gdisk dosfstools mtools kmod sudo vim less \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir kas
# Locale
RUN sed -i 's/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Create matching user to avoid root-owned files on host
RUN groupadd -g ${GROUP_ID} ${USERNAME} \
  && useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash ${USERNAME} \
  && usermod -aG sudo ${USERNAME} \
  && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-yocto-nopasswd

# Setup workspace
COPY . /opt/seed/yocto-ppe-workspace
RUN chown -R yocto:yocto /opt/seed

# copy seed volume 
COPY .devcontainer/seed-volume.sh /usr/local/bin/seed-volume.sh
RUN chmod +x /usr/local/bin/seed-volume.sh

RUN mkdir -p /home/${USERNAME}/ws/yocto-ppe-workspace \
            /home/${USERNAME}/ws/build \
            /home/${USERNAME}/ws/caches 
          
RUN chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/ws/yocto-ppe-workspace \
            /home/${USERNAME}/ws/build \
            /home/${USERNAME}/ws/caches


# QoL
RUN git config --system core.autocrlf false

USER ${USERNAME}
WORKDIR /home/${USERNAME}
