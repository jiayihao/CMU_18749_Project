import datetime
import socket
import signal
import sys
import threading
import time
import json
import argparse


IP = socket.gethostbyname(socket.gethostname())
PORT = 8888
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "q"
LFD_HEADER = "lfd"
CLIENT_HEADER = "client"
HEARTBEAT_RELPY = "Yes, I am."

class Server(object):
    
    connections = False
    
    '''
    i_am_ready = 0 not ready; = 1 ready
    '''
    def __init__(self, server_id, my_state, i_am_ready):
        self.server_id = server_id
        self.my_state = my_state
        self.i_am_ready = i_am_ready
        
        print("\n[STARTING] Starting server...\n")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.server.listen()
        print("\n[LISTENING] Server is listening on {}:{}...\n".format(IP, PORT))
        
    def start(self):
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_request, args = (conn, addr))
            thread.setDaemon(True)
            thread.start()
            print("\n[ACTIVE CONNECTIONS] " + str(threading.active_count() - 1) + "\n")
    
    def handle_request(self, conn, addr):
        print("\n[NEW CONNECTION] {} connected\n".format(addr))
        while True:
            try:
                msg = conn.recv(SIZE).decode(FORMAT)
                msg = json.loads(msg)
                header = msg["header"]
                if header == LFD_HEADER:
                    lfd_id = msg["lfd_id"]
                    message = msg["message"]
                    self.handle_lfd(conn, message, lfd_id)
                elif header == CLIENT_HEADER:
                    self.handle_client(conn, msg)
                else:
                    conn.close()
                    break
            except Exception:
                continue
    
    def handle_lfd(self, conn, msg, lfd_id):
        print("Received " + msg + " from " + lfd_id)
        conn.send(HEARTBEAT_RELPY.encode(FORMAT))
        print("Reply " + HEARTBEAT_RELPY + " to " + lfd_id + "\n")
            
    def handle_client(self, conn, msg):
            
        client_id = msg["client_id"]
        request_num = msg["request_num"]
        message = msg["message"]
        if message == DISCONNECT_MSG:
            print("Goodbye " + client_id + "\n")
            conn.close()
        else:
            print("Received " + message + " from " + client_id)
            print("[{}] Received <{}, {}, {}, request>".format(self.get_time(), client_id, self.server_id, request_num))
            print("[{}] my_state_{} = {} before processing <{}, {}, {}, request>\n".format(self.get_time(), self.server_id, self.my_state, client_id, self.server_id, request_num))
            reply_msg = "Msg received: " + message
            conn.send(reply_msg.encode(FORMAT))
            print("[{}] Sending <{}, {}, {}, reply>".format(self.get_time(), client_id, self.server_id, request_num))
            print("[{}] my_state_{} = {} after processing <{}, {}, {}, request>\n".format(self.get_time(), self.server_id, self.my_state, client_id, self.server_id, request_num))
        
    

    def close(self):
        self.s.close()
        sys.exit("\n" + self.get_time() + "Server close...")       
    
    def get_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='server_id', type=str, help='server_id to send')
    args = parser.parse_args()
    return args   

if __name__ == '__main__':
    args = getArgs()
    server_id = args.server_id
    s = Server(server_id, 0, 1)
    s.start()
    
    
    
    
    
    
    
    
