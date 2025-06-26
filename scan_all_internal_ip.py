from Pytheas22 import Python_Port_Scanner

scanner = Python_Port_Scanner.PythonPortScannerList(well_known_ports=True)
scanner_lst = scanner.make_lst()

start_scan = Python_Port_Scanner.PythonPortScanner(scanner_lst)
# IF YOU WANT TO SCAN ALL IP'S FROM YOUR NETWORK SIMPLY WRITE 
# Python_Port_Scanner.PortScanner.scan_all = True
start_scan.scan_internal_network()
