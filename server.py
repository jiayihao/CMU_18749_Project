import datetime 
from typing import List
import socket
import signal
import sys
import threading
import time
import json
import argparse, typing
import random

from dataclasses import dataclass

from color import *


IP = socket.gethostbyname("")
#IP="127.0.0.1"
# PORT = 7777
# ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "q"
LFD_HEADER = "lfd"
CLIENT_HEADER = "client"
CHECKPOINT_HEADER = "checkpoint"
HEARTBEAT_RELPY = "Yes, I am."
WAITING = "Waiting..."
lock = threading.Lock()

@dataclass
class ServerType:
    id: str
    ip: str
    port: int
PASSIVE_SERVERS: List[ServerType] = [
    {
        id: 'S2',
        ip: '127.0.0.1',
        port: '8888',
    },
    {
        id: 'S3',
        ip: '127.0.0.1',
        port: '9999',
    }
]

class Server(object):
    def __init__(self, server_id, port, primary: False, passive_servers: List[ServerType]= PASSIVE_SERVERS):
        self.server_id = server_id
        self.port = port
        self.my_state = WAITING
        self.response_num = 0
        self.active_connect = 0
        self.checkpoint_num = 0
        #self.queue[i] = addr
        self.queue = []
        
        private_ip = socket.gethostbyname(socket.gethostname())
        print_color(f"[STARTING] Starting server on {private_ip}:{self.port}", COLOR_MAGENTA)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, self.port))
        self.server.listen()

        self.primary = primary
        self.passive_servers: List[ServerType] = passive_servers if primary else []
        # self.checkpoint = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def start(self):
        if self.primary:
            # set up passive servers initilzation
            t = threading.Thread(target=self.setup_passive_servers)
            t.start()
        else:
            t = threading.Thread(target=self.handle_checkpoint)
            t.start()
            time.sleep(0.5)
        
        while True:
            conn, addr = self.server.accept()
            self.active_connect += 1
            thread = threading.Thread(target=self.handle_request, args = (conn, addr))
            thread.setDaemon(True)
            thread.start()
            # print("\n[ACTIVE CONNECTIONS] " + str(self.active_connect) + "\n")
            # print_color("\n[ACTIVE CONNECTIONS] " + str(threading.active_count() - 1) + "\n", COLOR_MAGENTA)
                
    
    def handle_request(self, conn, addr):
        # print_color("\n[NEW CONNECTION] {} connected\n".format(addr), COLOR_BLUE)
        while True:
            try:
                msg = conn.recv(SIZE).decode(FORMAT)
                msg = json.loads(msg)
                header = msg["header"]
                if header == LFD_HEADER:
                    lfd_id = msg["lfd_id"]
                    message = msg["message"]
                    heartbeat_count = msg["heartbeat_count"]
                    self.handle_lfd(conn, message, lfd_id, heartbeat_count)
                elif header == CLIENT_HEADER:
                    self.handle_client(conn, msg, addr)
                elif header == CHECKPOINT_HEADER:
                    self.handle_checkpoint(msg)
                else:
                    conn.close()
                    break
            except Exception:
                # print_color(str(addr) + " is disconnected...\n", COLOR_BLUE)
                #移除对应的client
                # if header == CLIENT_HEADER:
                #     self.queue.remove(addr)
                self.my_state = WAITING
                self.active_connect -= 1
                break
    
    def handle_lfd(self, conn, msg, lfd_id, heartbeat_count):
        print_color(f"[{heartbeat_count}] Received {msg} from {lfd_id}", COLOR_ORANGE)
        conn.send(HEARTBEAT_RELPY.encode(FORMAT))
        print_color(f"[{heartbeat_count}] Reply {HEARTBEAT_RELPY} to {lfd_id} \n", COLOR_MAGENTA)
            
    def handle_client(self, conn, msg, addr):
       
        client_id = msg["client_id"]
        request_num = msg["request_num"]
        message = msg["message"]
        print_color("Received " + message + " from " + client_id, COLOR_BLUE)
        print_color("[{}] Received <{}, {}, {}, request>".format(self.get_time(), client_id, self.server_id, request_num), COLOR_BLUE)
        print_color("[{}] my_state_{} = {} before processing <{}, {}, {}, request>".format(self.get_time(), self.server_id, self.response_num, client_id, self.server_id, request_num), COLOR_MAGENTA)
        #print("Total response number is", self.response_num, "\n")
        self.queue.append(addr)
        while self.my_state != WAITING or addr != self.queue[0]:
            continue
        #print("My_state_{} = {}. I am ready...\n".format(self.server_id, WAITING))
        self.my_state = client_id
        if message == DISCONNECT_MSG:
            self.my_state = WAITING
            self.queue.pop(0)
            print_color("Goodbye " + client_id + "\n", COLOR_MAGENTA)
            conn.close()
        else:
            # # reply_msg = "Msg received: " + message
            # reply_msg = json.dumps(msg)
            reply_msg = {
                "header": "server",
                "client_id": msg["client_id"],
                "server_id": self.server_id,
                "request_num": msg["request_num"],
                "message": msg["message"]
            }
            reply_msg = json.dumps(reply_msg)
            # time.sleep(random.randint(1,3))
            self.response_num += 1
            self.my_state = WAITING
            self.queue.pop(0)
            conn.send(reply_msg.encode(FORMAT))
            print_color("[{}] Sending <{}, {}, {}, reply>".format(self.get_time(), client_id, self.server_id, request_num), COLOR_MAGENTA)
            print_color("[{}] my_state_{} = {} after processing <{}, {}, {}, request>".format(self.get_time(), self.server_id, self.response_num, client_id, self.server_id, request_num), COLOR_MAGENTA)
    
    def setup_passive_servers(self):
        while True:
            threads = [] 
            for passive_server in self.passive_servers:
                threads.append(threading.Thread(target = self.sent_checkpoint, \
                                                name = f'Thread for server {passive_server.id}', \
                                                args = (passive_server, self.checkpoint_num, \
                                                self.response_num)))

            for t in threads:
                t.start()
            self.checkpoint_num += 1
            time.sleep(5)
    
    def sent_checkpoint(self, server: ServerType, response_num: int, checkpoint_num: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not self.connect(server, sock):
            return
        self.exchange(sock, server, response_num, checkpoint_num)
        sock.shutdown()
        
    def exchange(self, sock, server: ServerType, response_num: int, checkpoint_num: int) -> dict:
        # print(f"[{get_time()}] Sent <{self.cid}, {svr_id}, {seq}, request>")
        data = {
            "header": CHECKPOINT_HEADER,
            "checkpoint_num": checkpoint_num,
            "server_id": server.id,
            "state": response_num
        }
        try:
            sock.send(json.dumps(data).encode(FORMAT))
            print(f"[{self.get_time()}] Checkpoint Sent: {self.checkpoint_num}, Status Sent: {self.response_num}")
        except Exception:
            print("[FAIL!] Send Fail.")

    def connect(self, server: ServerType, sock) -> bool:
        try:
            sock.connect((server.ip, server.port))
            return True
        except Exception:
            return False

    def handle_checkpoint(self, msg):
        self.response_num = msg["state"]
        self.checkpoint_num = msg["checkpoint_num"]
        print(f"[{self.get_time()}] Checkpoint Received: {self.checkpoint_num}, Status Received: {self.response_num}")


    def get_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='server_id', type=str, help='server_id to send')
    parser.add_argument('-p', dest='port', type=int, help='port')
    # true = primary, 0 = backup
    parser.add_argument('--primary', dest='primary', action='store_true', required=False, default=False)
    args = parser.parse_args()
    return args   

if __name__ == '__main__':
    args = getArgs()
    server_id = args.server_id
    port = args.port
    primary = args.primary
    s = Server(server_id, port, primary, PASSIVE_SERVERS)
    s.start()