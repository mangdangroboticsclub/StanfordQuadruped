# Mini Pupper 2Pro

## Overview

![MP and MP2](imgs/MP.MP2.smallsize.jpg)

This branch is for Mini Pupper 2Pro version.

## Use the pre-built image

1. Download the [pre-built image](https://drive.google.com/drive/folders/175PWfA3oIgC565D_2thNbvp9qQf6Y6-V?usp=sharing) , web server is included.
2. [flash it into your SD card](https://minipupperdocs.readthedocs.io/en/latest/guide/Assembly.html#step-1-3-write-the-image-into-microsd-card).
3. Play your Mini Pupper.

   - Use a controller to control

     If you have a PS4 controller or MangDang controller before, you can play it according to [Quick Start Guide](https://minipupperdocs.readthedocs.io/en/latest/guide/QuickStartGuide.html)
     
   - Use a web browser to control, please refer to [here](https://github.com/mangdangroboticsclub/mini_pupper_web_controller).

## Installation by self

Before installation, you need to install the BSP(board support package) repo for your [Mini Pupper 2Pro](https://github.com/mangdangroboticsclub/mini_pupper_2_bsp/tree/mini_pupper_2pro_bsp).

After that, please follow the below steps to install this repo.

```
cd /home/ubuntu/
git clone https://github.com/mangdangroboticsclub/StanfordQuadruped.git -b mini_pupper_2pro StanfordQuadruped
cd StanfordQuadruped
./install.sh
```

configure the network, this will overwrite your current network configuration, enable the wireless network and breate a bridge interface with the IP address of 10.0.0.10/24 as required by UDPComms. This will not work if any of your interfaces is already connected to the 10.0.0.0/24 network. The network configuration becomes active with the next reboot.

```
./configure_network.sh <SSID> <password>
sudo reboot
```


If you want to use the web browser or keyboard to control your Mini Pupper, please continue to [here](https://github.com/mangdangroboticsclub/mini_pupper_web_controller).

