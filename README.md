# ARP Spoofer 1.0.0

## What is this script?

This is a ARP spoofer tool created with Python using Scapy module.

## Commented code

There is one .py file with the code fully commented (for educational purposes) and another .py file that contains only the code with necessary comments (if you don't see both files, it's because it is in progress).

## How to use the script?

- To spoof the targets, the user bacically needs to provide an two valid IPv4 addresses (Example: 192.168.0.1). By doing this, the attacker will be the man-in-the-middle and will intercept any packages comming from any of the two IPv4 addresses;
- This can be done by using the argument -t --target;
- If the user pass an invalid IPv4 address, the script will ask the user to input a new valid IPv4 address for any of the two targets;
- This script needs to run as sudo or root, otherwise the user will get an error;
- This code is meant to work with Python3.

Example 1 - Specifing both targets IPv4 addresses:

```
sudo ./arp_spoofer.py -t 192.168.0.1 192.168.0.100
```
