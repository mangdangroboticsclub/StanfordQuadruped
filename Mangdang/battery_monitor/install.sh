#!/bin/bash

#Deploy service
grep -q "dtoverlay=i2c4,pins_6_7" /boot/config.txt || \
   echo "dtoverlay=i2c4,pins_6_7" >> /boot/config.txt

sudo cp stuff/i2c4.dtbo /boot/overlays -f
sudo cp stuff/max1720x_battery.ko /lib/modules/`uname -r`/kernel/drivers/power/supply/max1720x_battery.ko
sudo cp stuff/battery_monitor /usr/bin/
sudo cp stuff/battery_monitor.service /lib/systemd/system/

#Start the service
systemctl enable  battery_monitor.service
#systemctl start battery_monitor

echo "------------------------------------------------------"
echo "Please reboot your raspberry pi to apply all settings"
echo "rebooting---------------------"
sleep 1
