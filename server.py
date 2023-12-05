from typing import List
import socket
import threading
import time
import json
import argparse 
from utilities import *


IP = socket.gethostbyname("")
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "q"
LFD_HEADER = "lfd"
CLIENT_HEADER = "client"
CHECKPOINT_HEADER = "checkpoint"
PRIMARY_HEADER="primary change"
NEW_MEMBER_HEADER="new member"
HEARTBEAT_RELPY = "Yes, I am."
WAITING = "Waiting..."
lock = threading.Lock()


class Server(object):
    # def __init__(self, server_id, port, primary: False, checkpoint_freq: int, other_servers: List[InstanceType], recover = False, is_active = True):
    def __init__(self, server_id, port, checkpoint_freq: int, other_servers: List[InstanceType], recover = False, is_active = True):
        self.server_id = server_id
        self.port = port
        self.my_state = WAITING
        self.response_num = 0
        self.active_connect = 0
        self.checkpoint_num = 0
        #self.queue[i] = addr
        self.queue = []
        self.checkpoint_freq = checkpoint_freq
        self.recover = recover

        self.is_active = is_active
        
        private_ip = socket.gethostbyname(socket.gethostname())
        print_color(f"[STARTING] Starting server on {private_ip}:{self.port}", COLOR_MAGENTA)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, self.port))
        self.server.listen()

        self.primary = is_active
        self.passive_servers = other_servers
        # self.passive_servers: List[InstanceType] = other_servers if primary else []
        # self.checkpoint = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def start(self):
        if not self.is_active:
            # set up passive servers initilzation
            t = threading.Thread(target=self.setup_other_servers)
            t.daemon = True
            t.start()
        
        while True:
            conn, addr = self.server.accept()
            self.active_connect += 1
            thread = threading.Thread(target=self.handle_request, args = (conn, addr))
            thread.daemon = True
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
                # yichen
                elif header == CLIENT_HEADER and not self.recover and ((not self.is_active and self.primary) or self.is_active):
                    self.handle_client(conn, msg, addr)
                elif header == CHECKPOINT_HEADER:
                    self.handle_checkpoint(msg)
                    self.recover = False
                elif header == PRIMARY_HEADER:
                    self.primary_change(conn, addr, msg)
                elif header == NEW_MEMBER_HEADER:
                    self.new_membersip(conn, addr, msg)
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
    
    def primary_change(self, conn, addr, msg):
        if msg["primary"] == self.server_id:
            self.primary = True

    def new_membersip(self, conn, addr, msg):
        #给那个server发
        if self.primary:
            for passive_server in self.passive_servers:
                if passive_server.id == msg["primary"]:
                    self.sent_checkpoint([passive_server], self.response_num, self.checkpoint_num)
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
    
    def setup_other_servers(self):
            while True:
                if self.primary and not self.is_active:
                    threads = []
                    for passive_server in self.passive_servers:
                        self.sent_checkpoint(passive_server, self.response_num, \
                                                                self.checkpoint_num)
                        threads.append(threading.Thread(target = self.sent_checkpoint, \
                                                        name = f'Thread for server {passive_server.id}', \
                                                        args = (passive_server, self.response_num, \
                                                                self.checkpoint_num)))
                    for t in threads:
                        t.start()
                    time.sleep(self.checkpoint_freq)
            
    
    def sent_checkpoint(self, server: InstanceType, response_num: int, checkpoint_num: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not self.connect(server, sock):
            return
        self.exchange(sock, server, response_num, checkpoint_num)
        sock.shutdown(socket.SHUT_RDWR)
        
    def exchange(self, sock, server: InstanceType, response_num: int, checkpoint_num: int) -> dict:
        # print(f"[{get_time()}] Sent <{self.cid}, {svr_id}, {seq}, request>")
        data = {
            "header": CHECKPOINT_HEADER,
            "checkpoint_num": checkpoint_num,
            "to": server.id,
            "state": response_num,
            "from": self.server_id
        }

        try:
            sock.send(json.dumps(data).encode(FORMAT))
            print(f"[{self.get_time()}] To Server: {server.id}, Checkpoint Sent: {self.checkpoint_num}, Status Sent: {self.response_num}")
        except Exception:
            print("[FAIL!] Send Fail.")

    def connect(self, server: InstanceType, sock) -> bool:
        try:
            sock.connect((server.ip, server.port))
            return True
        except Exception:
            return False

    def handle_checkpoint(self, msg):
        if msg["state"] > self.response_num:
            self.response_num = msg["state"]
            self.checkpoint_num = msg["checkpoint_num"]
        server_id = msg["from"]
        print(f"[{self.get_time()}] From Server: {server_id}, Checkpoint Received: {self.checkpoint_num}, Status Received: {self.response_num}")


    def get_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='server_id', type=str, help='server_id to send')
    parser.add_argument('-p', dest='port', type=int, help='port')
    parser.add_argument('-cf', dest='checkpoint_freq', type=int, help='checkpoint freqency', default=10)
    # true = primary, 0 = backup
    # parser.add_argument('--primary', dest='primary', action='store_true', required=False, default=False)
    parser.add_argument('--recover', dest='recover', action='store_true', required=False, default=False)

    parser.add_argument('--active', dest='active', action='store_true', required=False, default=False)
    args = parser.parse_args()
    return args   


if __name__ == '__main__':
    args = getArgs()
    server_id = args.server_id
    port = args.port
    # primary = args.primary
    checkpoint_freq = args.checkpoint_freq
    servers = load_config("servers")
    other_servers = [server for server in servers if server.id != server_id]
    # s = Server(server_id, port, primary, checkpoint_freq, other_servers, args.recover, args.active)
    s = Server(server_id, port, checkpoint_freq, other_servers, args.recover, args.active)
    s.start()
    