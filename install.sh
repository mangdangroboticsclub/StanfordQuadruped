#!/bin/bash

set -e

# check Ubuntu version
source /etc/os-release

if [[ $UBUNTU_CODENAME != 'jammy' && $UBUNTU_CODENAME != 'noble' ]]
then
    echo "Ubuntu 22.04.1 LTS (Jammy Jellyfish) is required or Ubuntu 24.04 LTS (noble)"
    echo "You are using $VERSION"
    exit 1
fi

### Get directory where this script is installed
BASEDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

clone_or_update_repo() {
    local repo_url=$1
    local repo_dir=$2

    if [ -d "$repo_dir/.git" ]
    then
        git -C "$repo_dir" pull --ff-only || true
    else
        git clone "$repo_url" "$repo_dir"
    fi
}

pip_supports_break_system_packages() {
    python3 -m pip help install 2>/dev/null | grep -q -- '--break-system-packages'
}

pip_install_compat() {
    if pip_supports_break_system_packages
    then
        sudo python3 -m pip install --break-system-packages "$@"
    else
        sudo python3 -m pip install "$@"
    fi
}

patch_legacy_pip_installs() {
    local script_file=$1
    if [ ! -f "$script_file" ]
    then
        return
    fi

    sed -E -i 's@(^|[[:space:]])sudo[[:space:]]+pip3?[[:space:]]+install@\1python3 -m pip install --break-system-packages@g' "$script_file"
    sed -E -i 's@(^|[[:space:]])pip3?[[:space:]]+install@\1python3 -m pip install --break-system-packages@g' "$script_file"
}

patch_ds4drv_py312_compat() {
    local ds4drv_root
    ds4drv_root=$(python3 - <<'PY'
import glob
matches = glob.glob('/usr/local/lib/python*/dist-packages/ds4drv')
print(matches[0] if matches else '')
PY
)

    if [ -z "$ds4drv_root" ]
    then
        return
    fi

    local ds4drv_config="$ds4drv_root/config.py"
    local ds4drv_input="$ds4drv_root/actions/input.py"

    if [ -f "$ds4drv_config" ]
    then
        sudo sed -i 's/configparser.SafeConfigParser/configparser.ConfigParser/g' "$ds4drv_config"
    fi

    if [ -f "$ds4drv_input" ]
    then
        sudo sed -i 's/joystick.device.device.fn/getattr(joystick.device.device, "fn", getattr(joystick.device.device, "path", "unknown"))/g' "$ds4drv_input"
    fi
}

### Append to release file
echo STANFORD_VERSION=\"$(cd $BASEDIR; ~/mini_pupper_bsp/get-version.sh)\" >> ~/mini-pupper-release

source  ~/mini-pupper-release
if [ "$IS_RELEASE" == "YES" ]
then
    cd $BASEDIR
    TAG_COMMIT=$(git rev-list --abbrev-commit --tags --max-count=1)
    TAG=$(git describe --abbrev=0 --tags ${TAG_COMMIT} 2>/dev/null || true)
    if [ "v$STANFORD_VERSION" != "$TAG" ]
    then
        sed -i "s/IS_RELEASE=YES/IS_RELEASE=NO/" ~/mini-pupper-release
    fi
fi

sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y unzip
sudo apt-get install -y bluez

# Prefer distro packages for core deps, then pip fallback for transforms3d.
sudo apt-get install -y python3-numpy python3-serial python3-pip
if python3 -c "import transforms3d" >/dev/null 2>&1
then
    true
else
    pip_install_compat transforms3d
fi

# Allow downstream installers to run on Ubuntu 24 where pip is externally managed.
export PIP_BREAK_SYSTEM_PACKAGES=1

# add bridge to network configuration
$BASEDIR/configure_network.sh
# reconfigure network each time network configuration has changed
echo $BASEDIR/configure_network.sh >> /home/ubuntu/mini_pupper_bsp/System/check-reconfigure.sh

cd ~
clone_or_update_repo https://github.com/stanfordroboticsclub/PupperCommand.git PupperCommand
cd PupperCommand
sed -i "s/pi/ubuntu/" joystick.service
patch_legacy_pip_installs install.sh
sed -i "s|sudo ln -s |sudo ln -sf |" install.sh
sudo env PIP_BREAK_SYSTEM_PACKAGES=1 bash install.sh

cd ~
clone_or_update_repo https://github.com/stanfordroboticsclub/UDPComms.git UDPComms
cd UDPComms
patch_legacy_pip_installs install.sh
sed -i "s|sudo ln -s |sudo ln -sf |" install.sh
sudo env PIP_BREAK_SYSTEM_PACKAGES=1 bash install.sh

cd ~
clone_or_update_repo https://github.com/stanfordroboticsclub/PS4Joystick.git PS4Joystick
cd PS4Joystick
sed -i "s/pi/ubuntu/" joystick.service
patch_legacy_pip_installs install.sh
if ! grep -q "import shutil" PS4Joystick.py
then
    sed -i '1aimport shutil' PS4Joystick.py
fi
sed -i 's@subprocess.run(\["hciconfig", "hciX", "up"\])@subprocess.run(["hciconfig", "hciX", "up"], check=False) if shutil.which("hciconfig") else None@' PS4Joystick.py
sudo env PIP_BREAK_SYSTEM_PACKAGES=1 bash install.sh
patch_ds4drv_py312_compat

cd ~
sudo systemctl enable joystick

cd ~/StanfordQuadruped
sudo ln -sf $(realpath .)/robot.service /etc/systemd/system/robot.service
sudo systemctl daemon-reload
sudo systemctl enable robot
sudo systemctl start robot

if [ -f restart_joy.service ]
then
    sudo install -m 644 restart_joy.service /lib/systemd/system/restart_joy.service
elif [ ! -f /lib/systemd/system/restart_joy.service ]
then
    echo "restart_joy.service not found"
    exit 1
fi

if [ -f joystart.sh ]
then
    sudo install -m 755 joystart.sh /sbin/joystart.sh
elif [ ! -f /sbin/joystart.sh ]
then
    echo "joystart.sh not found"
    exit 1
fi

sudo systemctl enable restart_joy

if systemctl cat battery_monitor >/dev/null 2>&1
then
    sudo mkdir -p /etc/systemd/system/battery_monitor.service.d
    sudo tee /etc/systemd/system/battery_monitor.service.d/override.conf >/dev/null <<'EOF'
[Service]
Type=simple
RemainAfterExit=no
Restart=always
RestartSec=2
EOF
fi

sudo systemctl daemon-reload
source  ~/mini-pupper-release
if [ "$MACHINE" == "x86_64" ]
then
    if [ "$HARDWARE" == "mini_pupper_2" ]
    then
        sudo systemctl start esp32-proxy &
        sudo systemctl start battery_monitor &
    else
        sudo systemctl start battery_monitor
    fi
    sudo systemctl start rc-local
    sudo systemctl start robot
fi
