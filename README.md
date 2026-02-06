# yocto-base-directory-setup

## Setup virtual host
### Use dev container on VScode
Open workspace in vscode and dev container extension will auto recognize the setup configuration in **.devcontainer**.

Select  "Reopen in Container" to connect to the virtual host.
### Use docker CLI
If you don’t use VSCode, you can bring up the container manually:

```bash
docker compose up -d
docker exec -it <yocto-container> /bin/bash
```
## Setup environment using kas

Clone or prepare repositories

Make sure you have the base layers (poky, meta-openembedded, meta-raspberrypi, etc.) in your workspace or let kas fetch them automatically.


### Setup `build_dir` (files be mounted in docker volumes) to locate the build directory when using kas.
```bash
KAS_BUILD_DIR=/yocto-build/<build_dir>
```
### Prepare repo
``` bash
kas checkout kas/<your-machine>.yml
```
### Build an image
```bash
kas build kas/<your-machine>.yml
```
___Note___: This command will clone required layers into the workspace (if not already present).

### Rebuild or resume
```bash
kas shell kas//<your-machine>.yml
bitbake <distro>
```
