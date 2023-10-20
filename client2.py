# -*- coding: utf-8 -*-
#!/usr/bin/python3

import socket
import json
import time
import argparse
import threading,random
lock = threading.Lock()
from color import *
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

    def exchange(self, sock, cur_seq, svr) -> (str, dict):
        print_color(f"[{get_time()}] Sent <{self.cid}, {svr}, {cur_seq}, request>",COLOR_MAGENTA)
        data = {
                    "header": "client",
                    "client_id": self.cid,
                    "server_id": "server_id",
                    "request_num": cur_seq,
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
        except Exception:
            # rint("[FAIL!] Receive Fail.")
            pass
        
        return cur_seq, msg

    def check_duplication(self, cur_seq: int) -> bool:
        if cur_seq in self.status:
            return True
        else:
            self.status.add(cur_seq)
            return False

    def updating(self, cur_seq: str, svr: str, msg: dict) -> None:
        # lock.acquire()           
        try:
            sid = msg["server_id"]
            seq = msg["request_num"]

            
            if not self.check_duplication(seq):
                self.seq += 1
                print_color(f"[{get_time()}] Received <{self.cid}, {sid}, {seq}, reply>",COLOR_BLUE)
            else:
                print(f"[{get_time()}] request_num {seq}: Discarded duplicate reply from {sid}.\n\n")
        except Exception:

            # lock.release()
            pass
        finally:
            # 改完了一定要释放锁:
            # lock.release()
            pass


    def disconnect(self, sock):
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass

    def initialize(self, ip, port, seq, svr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not self.connect(ip, port, sock,svr): return
        cur_seq, msg = self.exchange(sock, seq, svr)
        self.disconnect(sock)
        self.updating(cur_seq, SVR, msg)

    def run(self,server_list):
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
            # server_ips = 
            # l = random.sample(l, 3)
            # for i in l:
            #     self.initialize(server_ip_1, server_port_1, a,svr_1)
            #     self.initialize(server_ip_2, server_port_2, a,svr_2)
            #     self.initialize(server_ip_3, server_port_3, a,svr_3)
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