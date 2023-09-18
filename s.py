from flask import Flask
import time
import json
import argparse

IP = "localhost"
PORT = 8888

class Server(object):
    def __init__(self, server_id, my_state, i_am_ready):
        self.server_id = server_id
        self.my_state = my_state
        self.i_am_ready = i_am_ready
        self.server = Flask(__name__)
        self.server.route('/S1')(self.start)
    
    def start(self):
        self.server.run(port = PORT)
        print("[STARTING] Starting server...\n")
        print("[LISTENING] Server is waiting for connections on {}:{}...\n".format(IP, PORT))
 
    
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


