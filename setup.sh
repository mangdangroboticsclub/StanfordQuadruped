#!/bin/bash

set -e
echo "setup.sh started at $(date)"

### Get directory where this script is installed
BASEDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# check Ubuntu version
source /etc/os-release

if [[ $UBUNTU_CODENAME != 'jammy' ]]
then
    echo "Ubuntu 22.04 LTS (Jammy Jellyfish) is required"
    echo "You are using $VERSION"
    exit 1
fi

cd ~
if [ ! -d ~/mini_pupper_bsp ]
then
[[ "$1" == "v1" ]] && git clone https://github.com/mangdangroboticsclub/mini_pupper_bsp.git mini_pupper_bsp
[[ "$1" == "v2" ]] && git clone https://github.com/mangdangroboticsclub/mini_pupper_2_bsp.git mini_pupper_bsp
[[ -d ~/StanfordQuadruped ]] || git clone https://github.com/mangdangroboticsclub/StanfordQuadruped.git /home/ubuntu/StanfordQuadruped
fi

cd ~/mini_pupper_bsp
./install.sh

cd ~/StanfordQuadruped
./install.sh

echo "setup.sh finished at $(date)"
source  ~/mini-pupper-release
if [ "$MACHINE" != "x86_64" ]
then
    sudo reboot
fi
