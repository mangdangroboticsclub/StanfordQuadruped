#!/bin/bash

# check Ubuntu version
source /etc/os-release

if [[ $UBUNTU_CODENAME != 'jammy' ]]
then
    echo "Ubuntu 22.04.1 LTS (Jammy Jellyfish) is required"
    echo "You are using $VERSION"
    exit 1
fi

sudo apt-get update
sudo apt-get -y install bridge-utils python3 python-is-python3 python3-venv python3-virtualenv
sudo brctl addbr br0
sudo ip addr add 10.0.0.10/24 dev br0
sudo ip link add dummy1 type dummy
sudo ip link set dev dummy1 master br0
sudo ip link set dummy1 up
sudo ip link set br0 up

cd ~
[[ -d ~/StanfordQuadruped ]] || git clone https://github.com/mangdangroboticsclub/StanfordQuadruped.git
[[ -d ~/mini_pupper_venv ]] || python -m venv ~/mini_pupper_venv
[[ -d ~/UDPComms ]] || git clone https://github.com/stanfordroboticsclub/UDPComms.git
[[ -d ~/mini_pupper_web_controller ]] || git clone https://github.com/mangdangroboticsclub/mini_pupper_web_controller.git

source  ~/mini_pupper_venv/bin/activate
pip install numpy transforms3d pigpio pyserial coverage pytest netifaces msgpack
pip install ~/UDPComms/
pip install ~/mini_pupper_web_controller/joystick_sim
echo "import coverage; coverage.process_startup()" > ~/mini_pupper_venv/lib/python3.10/site-packages/.pth
cd ~/StanfordQuadruped/tests/integration_tests
COVERAGE_PROCESS_START=$(pwd)/.coveragerc coverage run -m pytest -v
coverage combine
coverage report
coverage html
