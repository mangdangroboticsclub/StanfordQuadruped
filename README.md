# mini pupper

## Overview

This branch contains modifications to the code of Stanford Pupper to make mini pupper work from [MangDang](https://www.mangdang.net)  

## Installation

Before installation, you need install [mini_pupper_bsp](https://github.com/mangdangroboticsclub/mini_pupper_bsp.git)  repo and run the test script to ensure your installation works as expected.

After install [mini_pupper_bsp](https://github.com/mangdangroboticsclub/mini_pupper_bsp.git), please follow the below steps.
Clone this repo : 
```
cd /home/ubuntu/
git clone https://github.com/mangdangroboticsclub/StanfordQuadruped.git
cd StanfordQuadruped
./install.sh
```

configure the network, this will overwrite your current network configuration, enable the wireless network and breate a bridge interface with the IP address of 10.0.0.10/24 as required by UDPComms. This will not work if any of your interfaces is already connected to the 10.0.0.0/24 network. The network configuration becomes active with the next reboot.

```
./configure_network.sh <SSID> <password>
sudo reboot
```
In case you want to use keyboard to control mini pupper, please refer to the below repo,
https://github.com/stanfordroboticsclub/PupperKeyboardController.git

```
sudo apt-get install libsdl2-2.0-0
sudo pip3 install pygame
git clone https://github.com/stanfordroboticsclub/PupperKeyboardController.git
```

