import socket
import json
import time
import argparse
import threading
from color import *

IP = socket.gethostbyname(socket.gethostname())
GFD_PORT = 1234
PORT = 5678
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "q"
GFD_HEADER = "gfd"
SERVERS = {"S1": 7777, "S2": 8888, "S3": 9999}
HEARTBEAT_MSG = "Are you alive?"
ALIVE_MSG = " is alive"
DEAD_MSG = " is dead"
HEARTBEAT_RELPY = "Yes, I am."
HEARTBEAT_ISSUE = "heartbeat"
REPLICA_ISSUE = "replica"

class LocalFaultDetector(object):
    def __init__(self, lfd_id, heartbeat_freq):
        self.lfd_id = lfd_id

        self.heartbeat_freq = heartbeat_freq
        self.heartbeat_count = 1

        self.connect_server_id = "S" + self.lfd_id[-1]
        self.server_alive = False
        self.gfd_alive = False

        self.notify_alive = False
        self.notify_dead = False
        

    def start(self):
        server_thread = threading.Thread(target=self.lanuch_server_socket, args = ())
        server_thread.daemon = True
        server_thread.start()

        gfd_thread = threading.Thread(target=self.lanuch_gfd_socket, args = ())
        gfd_thread.daemon = True
        gfd_thread.start()

        # 主线程
        while(1):
            time.sleep(5)
            continue


    # notify server changes to GFD
    def notify_gfd(self,message):
        to_gfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        to_gfd.connect(self.gfd_addr)
        to_gfd_msg = {
            "header": "lfd",
            "lfd_id": self.lfd_id,
            "server_id": self.connect_server_id
        }
        to_gfd_msg["issue"] = REPLICA_ISSUE
        to_gfd_msg["message"] = message
        to_gfd_msg = json.dumps(to_gfd_msg).encode(FORMAT)
        to_gfd.send(to_gfd_msg)
        
        # recv_msg = self.to_gfd.recv(SIZE).decode(FORMAT)
        to_gfd.close()
    
    def reply_gfd_heartbeat(self):
        while True:
            try:
                msg = self.to_gfd.recv(SIZE).decode(FORMAT)
                print_color("Received " + msg + "from GFD1", COLOR_RED)
                self.to_gfd.send(HEARTBEAT_RELPY.encode(FORMAT))
                print_color("Reply " + HEARTBEAT_RELPY + " to GFD1" + "\n", COLOR_ORANGE)
            except Exception:
                break

    def check_server_alive(self):
        while self.server_alive:
            data = {
                    "header": "lfd",
                    "lfd_id": self.lfd_id,
                    "server_id": server_id,
                    "message": HEARTBEAT_MSG,
                    "heartbeat_count": self.heartbeat_count
                    }
            try:
                self.to_server.send(json.dumps(data).encode(FORMAT))
                print_color(f"[{self.heartbeat_count}] {self.lfd_id} sending heartbeat to {self.connect_server_id}", COLOR_ORANGE)
            except:
                continue
            
            try:
                msg = self.to_server.recv(SIZE).decode(FORMAT)
                if msg != HEARTBEAT_RELPY:
                    print_color(f"{self.connect_server_id} {DEAD_MSG}", COLOR_MAGENTA)
                    self.server_alive = False
                    if self.gfd_alive and not self.notify_dead:
                        message = self.lfd_id + ": delete replica " + self.connect_server_id
                        self.notify_gfd(message)
                        self.notify_dead = True
                        self.notify_alive = False
                elif msg == HEARTBEAT_RELPY:
                    self.heartbeat_count += 1
                    print_color(f"{self.connect_server_id} {ALIVE_MSG}", COLOR_MAGENTA)
                    self.server_alive = True
                    if self.gfd_alive and not self.notify_alive:
                        message = self.lfd_id + ": add replica " + self.connect_server_id
                        self.notify_gfd(message)
                        self.notify_alive = True
                        self.notify_dead = False
            except Exception:
                print_color("\n[EXCEPTION] " + self.connect_server_id + DEAD_MSG, COLOR_MAGENTA)
                self.server_alive = False
                if self.gfd_alive and not self.notify_dead:
                    message = self.lfd_id + ": delete replica " + self.connect_server_id
                    self.notify_gfd(message)
                    self.notify_dead = True
                    self.notify_alive = False

            time.sleep(self.heartbeat_freq)


    def lanuch_server_socket(self):
        self.server_addr = (IP, SERVERS[self.connect_server_id])
        print_color(f"[STARTING] Starting LFD on {ADDR}...\n", COLOR_ORANGE)
        while not self.server_alive:
            try:
                self.to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.to_server.connect(self.server_addr)
                print_color(f"[CONNECTED] {self.lfd_id} connected to {self.connect_server_id} at {IP}:{SERVERS[self.connect_server_id]}", COLOR_ORANGE)
                self.server_alive = True
                self.check_server_alive()
            except Exception:
                print_color(f"[FAILED!] Waiting for {self.connect_server_id}", COLOR_ORANGE)
                self.server_alive = False
                time.sleep(5)
                continue

    def lanuch_gfd_socket(self):
        self.gfd_addr = (IP, GFD_PORT)
        print_color(f"[STARTING] {self.lfd_id} connecting GFD1\n", COLOR_ORANGE)
        while not self.gfd_alive:
            try:
                self.to_gfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.to_gfd.connect(self.gfd_addr)
                print_color(f"[CONNECTED] {self.lfd_id} connected to GFD1 at {IP}:1234", COLOR_ORANGE)
                
                data = {
                    "header": "lfd",
                    "lfd_id": self.lfd_id,
                    "server_id": server_id,
                    "message": HEARTBEAT_MSG,
                    "issue": HEARTBEAT_ISSUE
                }
                data = json.dumps(data).encode(FORMAT)
                self.to_gfd.send(data)
                self.gfd_alive = True
                self.reply_gfd_heartbeat()
            except Exception:
                print_color(f"[FAILED!] Waiting for GFD1", COLOR_ORANGE)
                time.sleep(5)
                continue




# arguments includes:
# 1. lfd_id -l
# 2. server_id -s
# 3. heartbeat_freq -hb
# 4. host -host
# 5. port -p
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', dest='lfd_id', type=str, help='lfd_id')
    parser.add_argument('-s', dest='server_id', type=str, help='server_id to send', default='S1')
    parser.add_argument('-hb', dest='heartbeat_freq', type=int, help='heartbeat_freq', default=2)
    parser.add_argument('-host', dest='host', type=str, help='host', default=IP)
    parser.add_argument('-p', dest='port', type=str, help='port', default=PORT)
    args = parser.parse_args()
    return args
          
if __name__ == '__main__':
    args = getArgs()
    lfd_id = args.lfd_id
    server_id = args.server_id
    heartbeat_freq = args.heartbeat_freq
    l = LocalFaultDetector(lfd_id, heartbeat_freq)
    l.start()