import os
import sys
import time


def install():
    print("\n\bSTARTING INSTALLATION\n\n")
    time.sleep(1)
    print("pip install Pytheas22")
    os.system("pip install Pytheas22")

    if sys.platform == "linux":
        print("sudo apt install netdiscover")
        os.system("sudo apt install netdiscover")
        print("sudo apt install dnsutils")
        os.system("sudo apt install dnsutils")
        print("sudo apt install dsniff")
        os.system("sudo apt install dsniff")
        print("\n\nFinished\n\n")


if sys.platform == "linux":
    if os.getuid() != 0:
        print("\nThis program must be run in root!!!!\n".upper())
        quit()

install()
