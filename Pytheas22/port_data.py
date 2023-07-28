import re
import subprocess


def check_ports(open_port, ip):
    data = ""
    all_port_data = {20: "File Transfer Protocol (FTP) data transfer",
                     21: "File Transfer Protocol (FTP) control (command)",
                     22: f"Secure Shell (SSH) secure logins, file transfers (scp, sftp) and port forwarding. \n To Bruteforce the target set ssh_bruteforce Parameter to True",
                     23: f"Telnet protocol—unencrypted text communications\nConnect with tellnet {ip}",
                     25: "Simple Mail Transfer Protocol (SMTP) used for email routing between mail servers ",
                     53: "Domain Name System (DNS). Translates an internet address into an address consisting of numbers ",
                     80: f"Hypertext Transfer Protocol (HTTP). Unsafe Protocol for websites. \n Website from target: http://{ip}",
                     110: "Post Office Protocol, version 3. This is for Mail",
                     119: "Network News Transfer Protocol (NNTP) retrieval of newsgroup messages",
                     123: "Network Time Protocol (NTP), used for time synchronization",
                     135: "Lightweight Directory Access Protocol (LDAP). This is the authentication protocol used in windows",
                     139: "Microsoft-DS (Directory Services) Active Directory, Windows shares",
                     143: "Internet Message Access Protocol (IMAP), management of electronic mail messages on a server",
                     161: "Simple Network Management Protocol (SNMP)",
                     194: "Internet Relay Chat (IRC)",
                     389: "Lightweight Directory Access Protocol (LDAP). This is the authentication protocol used in windows",
                     443: f"Hypertext Transfer Protocol Secure (HTTPS). Save Protocol for websites. \n Website from target: https://{ip}",
                     445: "Microsoft-DS (Directory Services) Active Directory, Windows shares",
                     515: "Line Printer Daemon (LPD), print service",
                     520: "Routing Information Protocol (RIP). Old version of routing protocol",
                     636: "Lightweight Directory Access Protocol over TLS/SSL (LDAPS)",
                     3389: f"Remote Desktop Protocol (RDP). Can access computers from anywhere if port is open like now\nAccess Computer on Windows with Remotedesktop and on Linux with Remmina",
                     5060: "Session Initiation Protocol (SIP)",
                     5061: "Session Initiation Protocol (SIP) over TLS",
                     5357: "Web Services for Devices (WSDAPI)",
                     8001: f"Streaming \nThere might be a website: http://{ip}:8001",
                     8002: f"Cisco Systems Unified Call Manager Intercluster\nThere might be a website: http://{ip}:8002",
                     8080: f"HTTP alternativ\nThere might be a website: http://{ip}:8080",
                     9080: "Microsoft Groove Software",
                     9999: "Communication",
                     62078: "Lightning Connector Apple Device"}

    if open_port in all_port_data:
        data = all_port_data[open_port]
        if open_port == 53:
            if re.findall(r"\d+.\d+.\d+.\d+", ip):
                all_data = subprocess.run(["nslookup", ip], capture_output=True)
                split_data = str(all_data).split("\\n")
                name = ""
                for each in split_data[0][::-1]:
                    if "=" == each:
                        break
                    name += each

                name = name[::-1]
                lst_name = [*name]
                lst_name[0] = ""
                name = "".join(lst_name)
                data += f"\nThis is the website: '{name}' of this IP"
    else:
        data += f"There might be a website: http://{ip}:{open_port}"

    return data
