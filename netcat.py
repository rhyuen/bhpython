import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print("My Netcat clone.")
    print()
    print("Usage: netcat.py -t target_host -p port")
    print("-l --listen                  -listen on [host]:[port] for incoming connections.")
    print("-e --execute=file_to_run     -execute the given file on receiving conn.")
    print("-c --command                 -initialize a command shell.")
    print("-u --upload_destination      -post-conn receipt, upload file and write to dest.")
    print("\n")
    print("Examples: ")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -c")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -e=c\"cat /etc/passwd\"")
    print("echo '1234567890' | ./netcat.py -t 192.168.11.12 -p 135")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",
        ["help", "listen", "execute", "target", "port", "command","upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    #handles the last example
    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(bytes(buffer))

    if listen:
        server_loop()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.STREAM)

    try:
        client.connect((target, port))
        if len(buffer):
            client.send(bytes(buffer))
        while True:
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response,)
            buffer = raw_input("")
            buffer += "\n"
            client.send(bytes(buffer))

    except:
        print("[*] Exception occurred.  Exiting.")
        client.close()


def server_loop():
    global target
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()



def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        file_buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        try:
            #wb flag means binary mode turned on
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(bytes(file_buffer))
            file_descriptor.close()
            client_socket.send(bytes("Success: Saved file to %s\r\n" % upload_destination))
        except:
            client_socket.send(bytes("Failure: No save to %s\r\n" % upload_destination))

    if len(execute):
        output = run_command(execute)
        client_socket.send(bytes(output))

    if command:
        while True:
            client_socket.send(bytes("<NTC:#> "))

            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer +=  client_socket.recv(1024)

            response = run_command(cmd_buffer)
            client_socket.send(bytes(response))

main()
