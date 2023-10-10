import socket
import json
import time
import argparse

IP = socket.gethostbyname(socket.gethostname())
PORT = 5678
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "q"
GFD_HEADER = "gfd"
SERVERS = {"S1": 8888}
HEARTBEAT_MSG = "Are you alive?"
ALIVE_MSG = " is alive"
DEAD_MSG = " is dead"
HEARTBEAT_RELPY = "Yes, I am."

class LocalFaultDetector(object):
    def __init__(self, lfd_id, heartbeat_freq, addr=ADDR):
        self.lfd_id = lfd_id

        self.heartbeat_freq = heartbeat_freq
        self.heartbeat_count = 1
        self.addr = addr
        self.to_server = None

        self.connect_server_id = "S" + self.lfd_id[-1]
        self.server_alive = False
        
        self.to_gfd = None
        self.gfd_addr = None

    # notify server changes to GFD
    def notify_gfd(self, msg):
        self.lanuch_gfd_notification_socket()
        self.to_gfd.send(msg)
        self.to_gfd.close()

    def check_server_alive(self, server_id):
        data = {
                "header": "lfd",
                "lfd_id": self.lfd_id,
                "server_id": server_id,
                "message": HEARTBEAT_MSG
            }
        while True:
            try:
                self.lfd.send(json.dumps(data).encode(FORMAT))
                print("[{self.heartbeat_count}] {self.lfd_id} sending heartbeat to {server_id}")
            except:
                continue
            
            try:
                msg = self.lfd.recv(SIZE).decode(FORMAT)
                if msg != HEARTBEAT_RELPY and self.server_alive:
                    print(f"{server_id} {DEAD_MSG}")
                    message = self.lfd_id + ": delete replica" + self.connect_server_id
                    self.notify_gfd(message)
                    self.server_alive = False
                elif msg == HEARTBEAT_RELPY and not self.server_alive:
                    self.heartbeat_count += 1
                    print(f"{server_id} {ALIVE_MSG}")
                    message = self.lfd_id + ": add replica" + self.connect_server_id
                    self.notify_gfd(message)
                    self.server_alive = True
            except Exception:
                print("\n" + server_id + DEAD_MSG)
                self.server_alive = False
                message = self.lfd_id + ": delete replica" + self.connect_server_id
                self.notify_gfd(message)

            time.sleep(self.heartbeat_freq)

    def handle_gfd(self, conn, addr):
        # print("Received " + msg + " from GFD")
        # conn.send(HEARTBEAT_RELPY.encode(FORMAT))
        # print("Reply " + HEARTBEAT_RELPY + " to " + lfd_id + "\n")
        while True:
            try:
                msg = conn.recv(SIZE).decode(FORMAT)
                print("Received " + msg + "from GFD1")
                conn.send(HEARTBEAT_RELPY.encode(FORMAT))
                print("Reply " + HEARTBEAT_RELPY + " to GFD1" + "\n")
            except Exception:
                break

    def lanuch_server_socket(self, server_id):
        self.to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[STARTING] Starting LFD on {ADDR}...\n")
        try:
            self.to_server.connect(self.addr)
            print(f"[CONNECTED] {self.lfd_id} connected to {server_id} at {IP}:{SERVERS[server_id]}")
        except Exception:
            print(f"[FAILED!] {self.lfd_id} cannot connect to {server_id} at {IP}:{SERVERS[server_id]}")

    def lanuch_gfd_socket(self, server_id):
        self.heartbeat_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.heartbeat_listener.bind(ADDR)
        self.heartbeat_listener.listen()

    def lanuch_gfd_notification_socket(self):
        self.to_gfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[STARTING] Connecting GFD\n")
        try:
            self.to_gfd.connect(self.gfd_addr)
            print(f"[CONNECTED] {self.lfd_id} connected to GFD1")
        except Exception:
            print(f"[FAILED!] {self.lfd_id} cannot connect to GFD1")

    # lanuch necessary sockets
    def init(self, server_id):
        self.lanuch_gfd_socket()
        time.sleep(1)
        self.lanuch_server_socket(server_id)



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
    l = LocalFaultDetector(lfd_id, heartbeat_freq, addr=(args.host, int(args.port)))
    l.connect(server_id)
    l.sendHeartbeat(server_id)