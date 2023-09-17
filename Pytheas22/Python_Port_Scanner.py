from .Port_Scanner import PortScanner
import BetterPrinting as bp


class PythonPortScannerList(PortScanner):
    def __init__(self, port_range=False, well_known_ports=False):
        super().__init__()
        self.well_known_ports = well_known_ports
        self.port_range = port_range
        self.lst = []
        if self.well_known_ports and self.port_range:
            bp.color("Only one of 'port_range' and 'well_known_ports' variables can be chosen", PortScanner.random_color)
            quit()

    def make_lst(self):
        if not self.port_range and self.well_known_ports:
            self.lst += PortScanner.well_known_ports

        if not self.well_known_ports and self.port_range:
            self.lst += self.get_lst(self.port_range)
            if "E" in self.lst:
                if "".join(self.lst) == "ERROR (EXAMPLE: 20-80)":
                    bp.color("".join(self.lst), PortScanner.random_color)
                    quit()
        return self.lst


class PythonPortScanner(PythonPortScannerList):

    def __init__(self, every_lst, ssh_bruteforce=False):
        super().__init__()
        self.every_lst = every_lst
        self.ssh_bruteforce = ssh_bruteforce

    def print_gui(self):
        bp.color(self.gui, PortScanner.random_color)

    def scan_one_addr(self, ip):
        self.print_gui()
        self.make_lst()

        self.start_scanning(self.every_lst, ip, ssh=self.ssh_bruteforce)

    def scan_internal_network(self):
        PortScanner.pps = True
        self.print_gui()
        self.make_lst()
        get_ip = PortScanner.internal_network()
        self.start_scanning(self.every_lst, get_ip, ssh=self.ssh_bruteforce)

    def scan_ip_cameras(self):
        self.print_gui()
        self.make_lst()
        PortScanner.ip_cameras(PortScanner, port_lst=self.every_lst, ssh=self.ssh_bruteforce)


