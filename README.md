Pytheas22
=========

![image](https://github.com/Kill0geR/KeyloggerScreenshot/assets/106278241/e0eccdd6-8a59-4d3a-aef6-0419719de5ac)


Created by: Fawaz Bashiru

Pytheas22 is an innovative Port Scanner. It scans IP-Cameras of countries, your home network and individual IP-Addresses or websites. Analysis of the IP-Cameras and the scanned home network will be saved in a database. Every open port will have a documentation.

If the port 22 of an IP-Address or a website is open pytheas22 will try to log in to the host via bruteforce.

Check out my github: https://github.com/Kill0geR/Pytheas22

Making a range of ports
=========
```python
from Pytheas22 import Python_Port_Scanner

scanner = Python_Port_Scanner.PythonPortScannerList(well_known_ports=True)
scanner_lst = scanner.make_lst()
```
This makes a list of every well_known ports
Output of that list will look like this:

```
[20, 21, 22, 23, 25, 53, 80, 110, 119, 123, 135, 139, 143, 161, 194, 389, 443, 445, 515, 520, 636, 3389, 5060, 5061, 5357, 8001, 8002, 8080, 9080, 9999, 62078]
```

If you want to make your own list simply do this:
```python
from Pytheas22 import Python_Port_Scanner

scanner = Python_Port_Scanner.PythonPortScannerList(port_range="20-80")
scanner_lst = scanner.make_lst()
```
This will make a list from 20 to 80
Output of that list will look like this:

```
[20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80]

```

Scanning with Pytheas22
---------------------
After you made your list you have to choose what you want to scan

* To scan your home network:

```python
from Pytheas22 import Python_Port_Scanner

scanner = Python_Port_Scanner.PythonPortScannerList(well_known_ports=True)
scanner_lst = scanner.make_lst()

start_scan = Python_Port_Scanner.PythonPortScanner(scanner_lst)
# IF YOU WANT TO SCAN ALL IP'S FROM YOUR NETWORK SIMPLY WRITE 
# Python_Port_Scanner.PortScanner.scan_all = True
start_scan.scan_internal_network()
```

* To scan ip cameras:
```python
from Pytheas22 import Python_Port_Scanner

scanner = Python_Port_Scanner.PythonPortScannerList(well_known_ports=True)
scanner_lst = scanner.make_lst()

start_scan = Python_Port_Scanner.PythonPortScanner(scanner_lst)
start_scan.scan_ip_cameras()
```

* To scan one host:
```python
from Pytheas22 import Python_Port_Scanner

scanner = Python_Port_Scanner.PythonPortScannerList(well_known_ports=True)
scanner_lst = scanner.make_lst()

start_scan = Python_Port_Scanner.PythonPortScanner(scanner_lst)
start_scan.scan_one_addr("127.0.0.1") #websites also work like start_scan.scan_one_addr("https://google.com")
```

* All included:
````python
from Pytheas22 import Port_Scanner

Port_Scanner.PortScanner.question(Port_Scanner.PortScanner)

````
This will have every scanning opportunity. Every step will be questioned like in the picture. Just like the GitHub version


Bruteforcing hosts with open ssh ports
---------------------------

To Bruteforce hosts with open ssh ports simply set the parameter 'ssh_bruteforce' from PythonPortScanner to True:
```python
from Pytheas22 import Python_Port_Scanner

scanner = Python_Port_Scanner.PythonPortScannerList(well_known_ports=True)
scanner_lst = scanner.make_lst()

start_scan = Python_Port_Scanner.PythonPortScanner(scanner_lst, ssh_bruteforce=True)
start_scan.internal_network()
```
The wordlist for that bruteforce is on my GitHub: https://github.com/Kill0geR/Pytheas22


Additional
==========
* Works on Linux and Windows (recommended in Linux)

* Pytheas22 is very easy to use.

* Bruteforce list is trained on ip-cameras

* DO NOT USE THIS TO ATTACK SOMEONE FOREIGN. I BUILD IT FOR EDUCATIONAL PURPOSES.
