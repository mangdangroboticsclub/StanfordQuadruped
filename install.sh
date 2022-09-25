#!/bin/bash

# check Ubuntu version
source /etc/os-release

if [[ $UBUNTU_CODENAME != 'jammy' ]]
then
    echo "Ubuntu 22.04.1 LTS (Jammy Jellyfish) is required"
    echo "You are using $VERSION"
    exit 1
fi

yes | sudo apt-get install libatlas-base-dev
yes | pip3 install numpy transforms3d pigpio pyserial
yes | pip install numpy transforms3d pigpio pyserial
yes | sudo pip install numpy transforms3d pigpio pyserial
sudo apt-get install -y unzip

cd ..
git clone https://github.com/stanfordroboticsclub/PupperCommand.git
cd PupperCommand
sed -i "s/pi/ubuntu/" joystick.service
sudo bash install.sh
cd ..

git clone https://github.com/stanfordroboticsclub/UDPComms.git
cd UDPComms
sudo bash install.sh
cd ..

git clone https://github.com/stanfordroboticsclub/PS4Joystick.git
cd PS4Joystick
sed -i "s/pi/ubuntu/" joystick.service
sudo bash install.sh
cd ..
sudo systemctl enable joystick

wget https://github.com/joan2937/pigpio/archive/v74.zip
unzip v74.zip
cd pigpio-74
make
sudo make install
cd ..

cd StanfordQuadruped
sudo ln -s $(realpath .)/robot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable robot
sudo systemctl start robot
