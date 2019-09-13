#!usr/bin/env python

# modules
import subprocess
import optparse
import re
import random

parser = optparse.OptionParser()  


def optional_arg(arg_default):
    def func(option, opt_str, value, parse):
        if parse.rargs and not parse.rargs[0].startswith('-'):
            val = parse.rargs[0]
            parse.rargs.pop(0)
        else:
            val = arg_default
        setattr(parse.values, option.dest, val)

    return func


def handle_arguments():
    parser.add_option("-i", "--interface", dest="interface", help="Accepts the interface to set the new MAC address")
    parser.add_option("-m", "--mac", dest="new_mac", help="Accepts the new MAC address")
    parser.add_option("-r", "--random", action='callback', callback=optional_arg('empty'), dest="random_mac",
                      help="Sets the MAC address randomly")
    parser.add_option("--reset", action='callback', callback=optional_arg('empty'), dest="reset_mac",
                      help="Resets the MAC address of given interface to its default")

    (values, arguments) = parser.parse_args()  
    if not values.interface:
        parser.error("[-] Specify the interface. Use --help for help menu.") 
    if not (values.new_mac or values.random_mac or values.reset_mac):
        parser.error("[-] Specify the MAC address. Use --help for help menu.")
    if values.new_mac and len(values.new_mac) != 17:
        parser.error("[-] Length does not match. This MAC address cannot be assigned.")
    return values
   

def change_mac(interface, new_mac_addr):
    print("Current MAC address = " + str(get_current_mac_addr(values.interface)))
    print("[+] Changing MAC address for " + interface + " to " + new_mac_addr)
    new_mac_addr = new_mac_addr[:17]  
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac_addr])
    subprocess.call(["ifconfig", interface, "up"])


def get_current_mac_addr(interface):
    ifconfig_result = subprocess.check_output(["ifconfig", interface])
    captured_mac_addr = re.search(r"(\w\w[-:]){5}\w\w", ifconfig_result)  
    if captured_mac_addr:
        return captured_mac_addr.group(0) 
    else:
        parser.error("[-] No any MAC address found on the specified interface.")


def generate_random_mac():
    random_line_no = random.randint(1, 23055)
    # print (i)
    with open("mac_vendor_codes.txt", "r") as mac_file:
        mac_vendor = mac_file.read().split("\n")[random_line_no]  
    vendor_code = mac_vendor[0:2] + ":" + mac_vendor[2:4] + ":" + mac_vendor[4:6]
    vendor = mac_vendor[7:]
    return (vendor_code + ":%02x:%02x:%02x" % (random.randint(0, 255),
                                               random.randint(0, 255),
                                               random.randint(0, 255),) + " (" + vendor + ")")


def reset_mac(interface):
    subprocess.call(["macchanger", "-p", interface])


def confirmation(mac):
    if get_current_mac_addr(values.interface) == mac.lower():
        print("[+] MAC address got changed successfully.")
    else:
        print("[-] MAC address did not get changed.")


with open("author.txt", "r") as author_mark:
    print(author_mark.read())  
values = handle_arguments()

if values.reset_mac and not values.random_mac and not values.new_mac:
    reset_mac(values.interface)

elif values.random_mac and not values.reset_mac and not values.new_mac:
    r_mac = generate_random_mac()
    change_mac(values.interface, r_mac)
    r_mac = r_mac[:17]
    confirmation(r_mac)

elif values.new_mac and not values.reset_mac and not values.random_mac:
    change_mac(values.interface, values.new_mac)
    current_mac_addr = get_current_mac_addr(values.interface)
    confirmation(values.new_mac)

else:
    parser.error("[-] Cannot perform this operation, check your arguments. Use --help for help menu.")

