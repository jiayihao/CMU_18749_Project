import socket
import json
import time
import argparse

#IP = "172.26.91.181"
IP = socket.gethostbyname(socket.gethostname())
PORT = 8888
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "q"
SERVERS = {"S1": 8888}
HEARTBEAT_MSG = "Are you alive?"
ALIVE_MSG = " is alive"
DEAD_MSG = " is dead"
HEARTBEAT_RELPY = "Yes, I am."

class LocalFaultDetector(object):
    def __init__(self, lfd_id, heartbeat_freq):
        self.lfd_id = lfd_id
        self.heartbeat_freq = heartbeat_freq
        self.heartbeat_count = 1
        
    def connect(self, server_id):
        self.lfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lfd.connect(ADDR)
        print("[CONNECTED] {} connected to {} at {}:{}".format(self.lfd_id, server_id, IP, SERVERS[server_id]))
    
    def sendHeartbeat(self, server_id):
        while True:
            time.sleep(self.heartbeat_freq)
            data = {
                    "header": "lfd",
                    "lfd_id": self.lfd_id,
                    "server_id": server_id,
                    "message": HEARTBEAT_MSG
                    }
            try:
                self.lfd.send(json.dumps(data).encode(FORMAT))
                print("[{}] {} sending heartbeat to {}".format(self.heartbeat_count, self.lfd_id, server_id))
            except:
                continue
            
            try:
                msg = self.lfd.recv(SIZE).decode(FORMAT)
                if msg != HEARTBEAT_RELPY:
                    print(server_id + DEAD_MSG)
                else:
                    print(server_id + ALIVE_MSG + "\n")
                    self.heartbeat_count += 1
            except Exception:
                print("\n" + server_id + DEAD_MSG)
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', dest='lfd_id', type=str, help='lfd_id')
    parser.add_argument('-s', dest='server_id', type=str, help='server_id to send')
    parser.add_argument('-hb', dest='heartbeat_freq', type=int, help='heartbeat_freq')
    args = parser.parse_args()
    return args
          
if __name__ == '__main__':
    args = getArgs()
    lfd_id = args.lfd_id
    server_id = args.server_id
    heartbeat_freq = args.heartbeat_freq
    l = LocalFaultDetector(lfd_id, heartbeat_freq)
    l.connect(server_id)
    l.sendHeartbeat(server_id)