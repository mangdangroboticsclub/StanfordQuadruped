#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <ssid> <wifi password>"
    exit 1
fi

sudo apt-get install -y bridge-utils

cat > /tmp/mini-pupper.yaml << EOF
network:
    ethernets:
        eth0:
            dhcp4: true
            optional: true
    wifis:
        wlan0:
            access-points:
                hdumcke:
                    password: "let me in"
            dhcp4: true
            optional: true
    bridges:
        br0:
            addresses: [10.0.0.10/24]
            parameters:
                stp: true
                forward-delay: 4
            dhcp4: false
            optional: true
    version: 2
EOF

sudo rm -f /etc/netplan/*
sudo cp /tmp/mini-pupper.yaml /etc/netplan/
