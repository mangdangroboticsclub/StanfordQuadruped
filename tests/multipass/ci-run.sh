#!/bin/bash

SERVER='minipupper'
START_TIME=$SECONDS

set -e

### Get directory where this script is installed
BASEDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "-------------------------------------------------------------------------------"
echo "Installing '$SERVER'"
echo "-------------------------------------------------------------------------------"

multipass delete $SERVER 2>/dev/null || echo "No multipass instance named '$SERVER'"
multipass purge
multipass launch -c 4 -m 2G -d 32G -n $SERVER --cloud-init cloud-config.yaml jammy

IP=$(multipass info $SERVER | grep IPv4 | awk -F' ' '{print $2}')

scp -o "IdentitiesOnly=yes" -i id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ../install_test_environment.sh ubuntu@$IP:
scp -o "IdentitiesOnly=yes" -i id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ../run_all_tests.sh ubuntu@$IP:
ssh -o "IdentitiesOnly=yes" -i id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ubuntu@$IP ./install_test_environment.sh

# Summary
echo "-------------------------------------------------------------------------------"
ELAPSED_TIME=$(($SECONDS - $START_TIME))
echo "Installation of '$SERVER' ended in $(($ELAPSED_TIME / 60))min $(($ELAPSED_TIME % 60))sec"
echo "ssh -o "IdentitiesOnly=yes" -i id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ubuntu@$IP"
echo "-------------------------------------------------------------------------------"
