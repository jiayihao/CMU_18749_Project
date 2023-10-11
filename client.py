# -*- coding: utf-8 -*-
#!/usr/bin/python3

import socket
import json
import time
import argparse
import threading
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
    
 
    def connect(self, ip, port, sock) -> bool:
        try:
            sock.connect((ip, port))
            return True
        except Exception:
            # print("[FAIL!] Connection To Server Fail.")
            return False

    def exchange(self, sock, cur_seq, svr) -> (str, dict):
        print(f"[{get_time()}] Sent <{self.cid}, {svr}, {cur_seq}, request>")
        data = {
                    "header": "client",
                    "client_id": self.cid,
                    "server_id": svr,
                    "request_num": self.seq,
                    "message": self.default_msg
                }
        try:
            sock.send(json.dumps(data).encode(FORMAT))
        except Exception:
            print("[FAIL!] Send Fail.")
            return
        msg = dict()
        try:
            message = sock.recv(1024).decode(FORMAT)
            message = json.loads(message)
            msg["server_id"] = message["server_id"]
            msg["request_num"] = message["request_num"]
        except Exception:
            print("[FAIL!] Receive Fail.")
            return
        
        return cur_seq, msg

    def check_duplication(self, cur_seq: int) -> bool:
        if cur_seq in self.status:
            return True
        else:
            self.status.add(cur_seq)
            return False

    def updating(self, cur_seq: str, svr: str, msg: dict) -> None:
        sid = msg["server_id"]
        seq = msg["request_num"]

        if not self.check_duplication(seq):
            self.seq += 1
            print(f"[{get_time()}] Received <{self.cid}, {sid}, {seq}, reply>")
        else:
            print(f"[{get_time()}] request_num {seq}: Discarded duplicate reply from {sid}.")


    def disconnect(self, sock):
        sock.shutdown(socket.SHUT_RDWR)

    def initialize(self, ip, port, seq, svr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not self.connect(ip, port, sock): return
        cur_seq, msg = self.exchange(sock, seq, svr)
        self.disconnect(sock)
        self.updating(cur_seq, msg["server_id"], msg)

    def run(self, ip, port, svr):
        while True:
            t1 = threading.Thread(target=self.initialize, name='Thread_1', args = (ip, 7777, self.seq, "S1"))
            t2 = threading.Thread(target=self.initialize, name='Thread_2', args = (ip, 8888, self.seq, "S2"))
            t3 = threading.Thread(target=self.initialize, name='Thread_3', args = (ip, 9999, self.seq, "S3"))
            t1.start()
            t2.start()
            t3.start()
            time.sleep(1)


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
