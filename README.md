# Mini Pupper

## Overview

![MP and MP2](imgs/MP.MP2.smallsize.jpg)

This branch contains modifications to the code of Stanford Pupper to make Mini Pupper and Mini Pupper 2 work.

## Installation

Before installation, you need to install [mini_pupper_bsp](https://github.com/mangdangroboticsclub/mini_pupper_bsp.git)  repo and run the test script to ensure your installation works as expected.

After that, please follow the below steps.

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


If you want use the web browser or keyboard to control your Mini Pupper, please continue to [here](https://github.com/mangdangroboticsclub/mini_pupper_web_controller).

