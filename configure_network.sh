#!/bin/bash

set -e

sudo apt-get install -y bridge-utils

SSID=${1:-Mangdang}
PASSWORD=${2:-mangdang}
NETPLAN_FILE=/etc/netplan/99-mini-pupper-network.yaml

sudo tee "$NETPLAN_FILE" >/dev/null <<EOF
network:
    version: 2
    ethernets:
        eth0:
            dhcp4: true
            optional: true
    wifis:
        wlan0:
            dhcp4: true
            optional: true
            access-points:
                "$SSID":
                    password: "$PASSWORD"
    bridges:
        br0:
            addresses: [10.0.0.10/24]
            parameters:
                stp: true
                forward-delay: 4
            dhcp4: false
            optional: true
EOF

sudo chmod 600 "$NETPLAN_FILE"
sudo netplan generate

echo "Netplan file generated at $NETPLAN_FILE."
echo "To avoid disconnecting the current Wi-Fi session, netplan was not applied immediately."
echo "Apply manually when safe: sudo netplan apply"
