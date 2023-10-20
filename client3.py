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
    
 
    def connect(self, ip, port, sock,svr) -> bool:
        try:
            sock.connect((ip, port))
            return True
        except Exception:
            print("[FAIL!] Server " + svr +" is unreachable")
            return False

    def exchange(self, sock, seq, svr_id) -> dict:
        print(f"[{get_time()}] Sent <{self.cid}, {svr_id}, {seq}, request>")
        data = {
                    "header": "client",
                    "client_id": self.cid,
                    "server_id": svr_id,
                    "request_num": self.seq,
                    "message": self.default_msg
                }
        try:
            sock.send(json.dumps(data).encode(FORMAT))
        except Exception:
            # print("[FAIL!] Send Fail.")
            return
        

        msg = dict()
        try:
            message = sock.recv(1024).decode(FORMAT)
            message = json.loads(message)
            msg["server_id"] = message["server_id"]
            msg["request_num"] = message["request_num"]
            msg["message"] = message["message"]
        except Exception:
            print("[FAIL!] Receive Fail.")
            return
        return msg

    def check_duplication(self, seq: int) -> bool:
        if seq in self.status:
            return True
        else:
            self.status.add(seq)
            return False

    def updating(self, msg: dict) -> None:
        sid = msg["server_id"]
        seq = msg["request_num"]

        if not self.check_duplication(seq):
            self.seq += 1
            print(f"[{get_time()}] Received <{self.cid}, {sid}, {seq}, reply>")
        else:
            print(f"[{get_time()}] request_num {seq}: Discarded duplicate reply from {sid}.")


    def disconnect(self, sock):
        sock.shutdown(socket.SHUT_RDWR)

    def initialize(self, ip, port, seq, server_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not self.connect(ip, port, sock): return
        msg = self.exchange(sock, seq, server_id)
        self.disconnect(sock)
        self.updating(msg)

    def run(self, ip, port, svr):
        while True:
            svr_1=server_list[0].split("/")[0]
            server_ip_1=server_list[0].split("/")[1].split(":")[0]
            server_port_1= int (server_list[0].split("/")[1].split(":")[1])
            t1 = threading.Thread(target=self.initialize, name='Thread_1', args = (server_ip_1, server_port_1, self.seq,svr_1))
            svr_2=server_list[1].split("/")[0]
            server_ip_2=server_list[1].split("/")[1].split(":")[0]
            server_port_2=int (server_list[1].split("/")[1].split(":")[1])
            t2 = threading.Thread(target=self.initialize, name='Thread_2', args = (server_ip_2, server_port_2, self.seq,svr_2))
            svr_3=server_list[2].split("/")[0]
            server_ip_3=server_list[2].split("/")[1].split(":")[0]
            server_port_3=int (server_list[2].split("/")[1].split(":")[1])
            t3 = threading.Thread(target=self.initialize, name='Thread_3', args = (server_ip_3, server_port_3, self.seq,svr_3))
            t1.start()
            t2.start()
            t3.start()
            # self.initialize(ip, 9999, self.seq, "S3")
            # self.initialize(ip, 7777, self.seq, "S1")
            time.sleep(5)


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='client_id', type=str, help='client_id', default = "C1")
    parser.add_argument('-s', dest='server_list', type=str, help='server_list')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = getArgs()
    c = Client(args.client_id)
    server_list = args.server_list.split(",")
    c.run(server_list)