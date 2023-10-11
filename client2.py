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
SERVERS = {"S1": 8888}
SVR = "S1"


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())




class Client(object):
    def __init__(self, client_id):
        threading.Thread.__init__(self)
        self.cid = client_id
        self.seq = 101
        # self.threads=[]
        self.status = set()
        self.default_msg = "Client Hello!"
 
    def connect(self, ip, port, sock) -> bool:
        try:
            sock.connect((ip, port))
            return True
        except Exception:
            print("[FAIL!] Connection To Server Fail.")
            return False

    def exchange(self, sock, cur_seq, svr) -> (str, str):
        print(f"[{get_time()}] Sent <{self.cid}, {svr}, {cur_seq}, request>")
        data = {
                    "header": "client",
                    "client_id": self.cid,
                    "server_id": "server_id",
                    "request_num": self.seq,
                    "message": self.default_msg
                }
        try:
            sock.send(json.dumps(data).encode(FORMAT))
        except Exception:
            print("[FAIL!] Send Fail.")
            return
        try:
            message = sock.recv(1024).decode(FORMAT)
        except Exception:
            print("[FAIL!] Receive Fail.")
            return
        
        return cur_seq, data

    def check_duplication(self, cur_seq: int) -> bool:
        
        if cur_seq in self.status:
            return True
        else:
            self.status.add(cur_seq)
            return False

    def updating(self, data: str, cur_seq: str, svr: str) -> None:

        if not self.check_duplication(cur_seq):
            self.seq += 1
            print(f"[{get_time()}] Received <{self.cid}, {svr}, {cur_seq}, reply>")
        else:
            print(f"[{get_time()}] request_num {cur_seq}: Discarded duplicate reply from SERVER.")


    def disconnect(self, sock):
        sock.shutdown(socket.SHUT_RDWR)

    def initialize(self, ip, port, seq, svr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(ip, port, sock)
        cur_seq, data = self.exchange(sock, seq, svr)
        self.disconnect(sock)
        self.updating(data, cur_seq, SVR)

    def run(self, ip, port, svr):
        while True:
            t1 = threading.Thread(target=self.initialize, name='Thread_1', args = (ip, port, self.seq, svr))
            t2 = threading.Thread(target=self.initialize, name='Thread_2', args = (ip, port, self.seq, svr))
            t3 = threading.Thread(target=self.initialize, name='Thread_2', args = (ip, port, self.seq, svr))
            t1.start()
            t2.start()
            t3.start()
            # self.initialize(ip, port, self.seq, svr)
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

    # t1 = threading.Thread(target=c.run, name='Thread_2', args = (args.server_IP, args.server_port, args.server_id))
    # t1.daemon = True
    # t1.start()
    # t.join()

    # print("aaa")

    # t2 = threading.Thread(target=c.run, name='Thread_1', args = (args.server_IP, args.server_port, args.server_id))
    # t2.daemon = True
    # t2.start()
    # # t2.join()

    # while(1):
    #     time.sleep(13)
    #     continue

    

    print("bbb")

    # gfd_thread = threading.Thread(target=c.run, args = (args.server_IP, args.server_port))
    # gfd_thread.daemon = True
    # gfd_thread.start()

    # c1 = Client("C1")
    # c2 = Client("C2")
    # c3 = Client("C3")
    # c1.start()
    # c2.start()
    # c3.start()
    # c1.join()
    # c2.join()
    # c3.join()
