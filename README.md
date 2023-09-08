Pytheas22
=========

![image](https://github.com/Kill0geR/KeyloggerScreenshot/assets/106278241/e0eccdd6-8a59-4d3a-aef6-0419719de5ac)


Created by: Fawaz Bashiru

Pytheas22 is an innovative Port Scanner. It scans IP-Cameras of countries, your home network and individual IP-Addresses or websites. Analysis of the IP-Cameras and the scanned home network will be saved in a database. Every open port will have a documentation. Pytheas22 can also arpsooof a device on your network

If the port 22 of an IP-Address or a website is open pytheas22 will try to login to the host via bruteforce.


Pytheas22 is recommended to be used in Kali linux but works on every linux distro

First of all
===========

Change to root:

`sudo su`


Clone my project with:

`git clone https://github.com/Kill0geR/Pytheas22`


Change to Pytheas22 directory:

`cd Pytheas22`


Install requirements:

`pip install -r requirements.txt`


Install nmap (kali linux has it already installed (not needed in Windows))

`sudo apt-get install nmap`

Install nslookup (kali linux has it already installed (not needed in Windows))

`sudo apt install dnsutils`

Install dsniff (for arpspoffing)
`sudo apt install dsniff`

If finished run the main.py file

`python main.py`


It is very easy to use so everything will be explained in main.py

Thank you for using Pytheas22

Additional
==========
* Works on Linux and Windows
  
* It takes around 1.11 seconds to scan a list with 31 elements

* Pytheas22 is very easy to use.

* Bruteforce list is trained on ip-cameras

* DO NOT USE THIS TO ATTACK SOMEONE FOREIGN. I BUILD IT FOR EDUCATIONAL PURPOSES.
