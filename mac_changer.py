#!/usr/bin/env python3
from subprocess import call, check_output
from optparse import OptionParser
import re
import random

parser = OptionParser()


class MacChanger:
    """Class for Mac Changer"""

    def __init__(self, interface, new_mac=None):

        """variable initialization"""

        self.interface = interface
        self.new_mac = new_mac
        self.vendor = "Unknown"


    def get_current_mac_addr(self):
        """Current Mac address grabbing"""

        ifconfig_result = str(check_output(["ifconfig", self.interface]))
        captured_mac_addr = re.search(r"(\w\w[-:]){5}\w\w", ifconfig_result)
        if captured_mac_addr:
            return captured_mac_addr.group(0)
        else:
            parser.error(
                "[-] No any MAC address found on the specified interface.")

    def generateRM(self):
        """Generate Random Mac Address"""

        random_line_no = random.randint(1, 23055)
        with open("mac_vendor_codes.txt", "r") as mac_file:
            mac_vendor = mac_file.read().split("\n")[random_line_no]
        vendor_code = mac_vendor[0:2] + ":" + \
                      mac_vendor[2:4] + ":" + mac_vendor[4:6]
        self.vendor = mac_vendor[7:]
        return vendor_code + ":%02x:%02x:%02x" % (random.randint(0, 255),
                                                  random.randint(0, 255),
                                                  random.randint(0, 255),), self.vendor

    def change_mac(self):
        """Change the Mac Address"""

        if not self.new_mac:
            self.new_mac, self.vendor = self.generateRM()
        print("Current MAC address = " +
              str(self.get_current_mac_addr()))
        print("[+] Changing MAC address for " +
              self.interface + " to " + self.new_mac + " (%s)" % self.vendor)
        call(["ifconfig", self.interface, "down"])
        call(["ifconfig", self.interface,
              "hw", "ether", self.new_mac])
        call(["ifconfig", self.interface, "up"])

        self.confirmation()

    def reset_mac(self):
        """Reset The Mac Adress"""

        call(["macchanger", "-p", self.interface])

    def confirmation(self):
        """Just to Confirm"""

        if self.get_current_mac_addr() == self.new_mac.lower():
            print("[+] MAC address got changed successfully.")
        else:
            print("[-] MAC address did not get changed.")


def banner():
    """Author things"""

    print('''
___  ___             _____ _                                 
|  \\/  |            /  __ \\ |                                
| .  . | __ _  ___  | /  \\/ |__   __ _ _ __   __ _  ___ _ __ 
| |\\/| |/ _` |/ __| | |   | '_ \\ / _` | '_ \\ / _` |/ _ \\ '__|
| |  | | (_| | (__  | \\__/\\ | | | (_| | | | | (_| |  __/ |   
\\_|  |_/\\__,_|\\___|  \\____/_| |_|\\__,_|_| |_|\\__, |\\___|_|   
                                              __/ |          
                                             |___/    ~by Mobeen       
    ''')


def handle_arguments():
    """Optparas Handling"""

    parser.add_option("-i", "--interface", dest="interface",
                      help="Accepts the interface to set the new MAC address")
    parser.add_option("-m", "--mac", dest="new_mac",
                      help="Accepts the new MAC address")
    parser.add_option("-r", "--random", action='store_true', dest="random_mac",
                      help="Sets the MAC address randomly")
    parser.add_option("--reset", action='store_true', dest="reset_mac",
                      help="Resets the MAC address of given interface to its default")

    (values, arguments) = parser.parse_args()
    if not values.interface:
        parser.error("[-] Specify the interface. Use --help for help menu.")
    if not (values.new_mac or values.random_mac or values.reset_mac):
        parser.error("[-] Specify the MAC address. Use --help for help menu.")
    if values.new_mac and len(values.new_mac) != 17:
        parser.error(
            "[-] Length does not match. This MAC address cannot be assigned.")
    return values


def main():
    banner()
    values = handle_arguments()
    mac_C = MacChanger(values.interface)
    if values.reset_mac and not values.random_mac and not values.new_mac:
        mac_C.reset_mac()

    elif values.random_mac and not values.reset_mac and not values.new_mac:
        mac_C.change_mac()
    elif values.new_mac and not values.reset_mac and not values.random_mac:
        mac_C.__init__(values.interface, values.new_mac)
        mac_C.change_mac()
    else:
        parser.print_help(
            "[-] Cannot perform this operation, check your arguments. Use --help for help menu.")


if __name__ == "__main__":
    main()
