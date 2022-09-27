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
systemctl enable restart_joy