# Mini Pupper

## Overview

![MP and MP2](imgs/MP.MP2.smallsize.jpg)

This branch contains modifications to the code of Stanford Pupper to make Mini Pupper and Mini Pupper 2 work.

## Use the pre-built image

1. Download the [pre-built image](https://drive.google.com/file/d/1B9kNB0XnqvkOrHszQJVyMPZ1RG85zfG3/view?usp=sharing) 
2. [flash it into your SD card](https://minipupperdocs.readthedocs.io/en/latest/guide/Assembly.html#step-1-3-write-the-image-into-microsd-card).
3. Use your own WiFi AP name and password to replace the default value in "/etc/netplan/50-cloud-init.yaml"
   You can use the SD card to boot the system, then edit line 16, 17 in "/etc/netplan/50-cloud-init.yaml", or
   You put the SD card into the SD reader and plug it into a Ubuntu PC, and then edit 50-cloud-init.yaml, just as shown in the below picture.

![changeWiFi](imgs/changeWiFi.png)
   
5. Reboot and enjoy

## Installation by self

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

