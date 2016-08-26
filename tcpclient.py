import socket, sys

target_host = "www.kotaku.com"

print(target_host)
target_port = 80

#denote ipv4 usage
#denote tcp usage
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#add failure case
client.connect((target_host, target_port))
client.send(bytes("GET / HTTP/1.1\r\nHost: kotaku.com\r\n\r\n", "utf-8"))
response = client.recv(4096)
print(response)
