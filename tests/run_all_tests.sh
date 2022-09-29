#!/bin/bash

# check Ubuntu version
source /etc/os-release

if [[ $UBUNTU_CODENAME != 'jammy' ]]
then
    echo "Ubuntu 22.04.1 LTS (Jammy Jellyfish) is required"
    echo "You are using $VERSION"
    exit 1
fi

cd ~
[[ -d ~/StanfordQuadruped ]] || git clone https://github.com/mangdangroboticsclub/StanfordQuadruped.git

source  ~/mini_pupper_venv/bin/activate
pip install numpy transforms3d pigpio pyserial
cd ~/StanfordQuadruped/tests/integration_tests
COVERAGE_PROCESS_START=$(pwd)/.coveragerc coverage run -m pytest -v
coverage combine
coverage report
coverage html
