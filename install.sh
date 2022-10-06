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
yes | pip3 install numpy transforms3d pyserial
yes | pip install numpy transforms3d pyserial
yes | sudo pip install numpy transforms3d pyserial
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

cd StanfordQuadruped
sudo ln -s $(realpath .)/robot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable robot
sudo systemctl start robot


sudo mv restart_joy.service /lib/systemd/system/
sudo mv joystart.sh /sbin/
sudo systemctl enable restart_joy
