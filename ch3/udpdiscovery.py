import socket
import os

#FOR: looking for easy targets to compromise on a network
#HOW: If you send a UDP packet to a closed port, you'll get reply in ICMP stating unreachable. Suggesting that there's a host there.

host = "192.168.0.196"

if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))

sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

#for windows to enable promiscuous mode.
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

print(sniffer.recvfrom(65565))

#turns off promiscuous if on Windows
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
