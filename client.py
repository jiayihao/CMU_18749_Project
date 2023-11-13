# -*- coding: utf-8 -*-
#!/usr/bin/python3

import socket
import json
import time
import argparse
import threading
from color import *
lock = threading.Lock()

# IP = socket.gethostbyname(socket.gethostname())
IP = "localhost"
PORT = 7777
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "q"
SERVERS = {"S1": 7777, "S2": 8888, "S3": 9999}
SVR = "S1"


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class Client(object):
    def __init__(self, client_id):
        threading.Thread.__init__(self)
        self.cid = client_id
        self.seq = 101
        self.status = set()
        self.default_msg = "Client Hello!"
    
 
    def connect(self, ip, port, sock,srv) -> bool:
        try:
            sock.connect((ip, port))
            return True
        except Exception:
            print("[FAIL!] Server "+ srv +" is unreachable.")
            return False

    def exchange(self, sock, seq, svr_id) -> dict:
        print(f"[{get_time()}] Sent <{self.cid}, {svr_id}, {seq}, request>")
        data = {
                    "header": "client",
                    "client_id": self.cid,
                    "server_id": svr_id,
                    "request_num": seq,
                    "message": self.default_msg
                }
        try:
            sock.send(json.dumps(data).encode(FORMAT))
            
        except Exception:
            #print("[FAIL!] Send Fail.")
            pass
           
        msg = dict()
        try:
            message = sock.recv(1024).decode(FORMAT)
            message = json.loads(message)
            msg["server_id"] = message["server_id"]
            msg["request_num"] = message["request_num"]
            msg["message"] = message["message"]
        except Exception:
            pass

        return msg

    def check_duplication(self, seq: int) -> bool:
        if seq in self.status:
            return True
        else:
            self.status.add(seq)
            return False

    def updating(self, msg: dict) -> None:
        lock.acquire()
        sid = msg["server_id"]
        seq = msg["request_num"]

        if not self.check_duplication(seq):
            self.seq += 1
            print_color(f"[{get_time()}] Received <{self.cid}, {sid}, {seq}, reply>",COLOR_BLUE)
        else:
            print_color(f"[{get_time()}] request_num {seq}: Discarded duplicate reply from {sid}.",COLOR_RED)
        lock.release()

    def disconnect(self, sock):
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
    def initialize(self, ip, port, seq, server_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not self.connect(ip, port, sock,server_id): return
        if server_id=="S1":
            msg = self.exchange(sock, seq, server_id)
        self.disconnect(sock)
        if server_id=="S1":
            self.updating(msg)

    def run(self, ip, port, svr):
        while True:
            print("\n")
            t1 = threading.Thread(target=self.initialize, name='Thread_1', args = ("10.70.37.171", 7777, self.seq, "S1"))
            t2 = threading.Thread(target=self.initialize, name='Thread_2', args = ("127.0.0.1", 8888, self.seq, "S2"))
            t3 = threading.Thread(target=self.initialize, name='Thread_3', args = ("127.0.0.1", 9999, self.seq, "S3"))
            t1.start()
            t2.start()
            t3.start()
            time.sleep(5)


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='client_id', type=str, help='client_id', default = "C1")
    parser.add_argument('-s', dest='server_id', type=str, help='server_id', default = "S1")
    parser.add_argument('-a', dest='server_IP', type=str, help='server_IP', default = IP)
    parser.add_argument('-p', dest='server_port', type=str, help='server_port', default = PORT)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = getArgs()
    c = Client(args.client_id)
    c.run(args.server_IP, args.server_port, args.server_id)
