import socket
import json
import time
import argparse

IP = socket.gethostbyname(socket.gethostname())
#IP = "172.26.91.181"
PORT = 8888
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "q"
SERVERS = {"S1": 8888}

class Client(object):
    def __init__(self, client_id):
        self.client_id = client_id
        self.request_num = 101
        
    def connect(self, server_id):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)
        print("[CONNECTED] {} connected to {} at {}:{}".format(self.client_id, server_id, IP, SERVERS[server_id]))
        
    def sendMessage(self, server_id):
        connected = True
        while connected:
            msg = input("Please enter message>> ")
            data = {
                    "header": "client",
                    "client_id": self.client_id,
                    "server_id": server_id,
                    "request_num": str(self.request_num),
                    "message": msg
                    }
            if msg == DISCONNECT_MSG:
                connected = False
                self.client.send(json.dumps(data).encode(FORMAT))
                self.client.close()
            else:
                self.client.send(json.dumps(data).encode(FORMAT))
                print("[{}] Sent <{}, {}, {}, request>".format(self.get_time(), self.client_id, server_id, self.request_num))
                msg = self.client.recv(SIZE).decode(FORMAT)
                if not msg:
                    connected = False
                    self.client.close()
                    print("Server closed...")
                else:
                    print("[{}] Received <{}, {}, {}, reply>\n".format(self.get_time(), self.client_id, server_id, self.request_num))
                self.request_num += 1
    def get_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='client_id', type=str, help='client_id')
    parser.add_argument('-s', dest='server_id', type=str, help='server_id to send')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = getArgs()
    client_id = args.client_id
    server_id = args.server_id
    c = Client(client_id)
    c.connect(server_id)
    c.sendMessage(server_id)