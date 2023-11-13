import socket
import argparse
import time
import json
import threading
import socket
from color import *

PORT = 2001
IP = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
SIZE = 1024
RM_HEADER = "rm"
CONNECT_ISSUE = "gfd to rm connect"
MEMBER_ISSUE = "membership change"


class GlobalFaultDetector():
    def __init__(self, rm_id, ip=IP, port=PORT):
        self.port = port
        self.ip = ip
        self.rm_id = rm_id

        print(f"[STARTING] Starting {self.rm_id} on {self.ip}:{self.port} \n")

        # self.print_memberships()

        self.rm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rm.bind((self.ip, self.port))
        self.rm.listen()

    def start(self):
        while True:
            conn, addr = self.rm.accept()
            thread = threading.Thread(
                target=self.handle_rm_connection, args=(conn, addr))
            thread.daemon = True
            thread.start()

    def handle_rm_connection(self, conn, addr):
        while True:
            try:
                msg = conn.recv(SIZE).decode(FORMAT)
                msg = json.loads(msg)

                header = msg["header"]
                if header != RM_HEADER:
                    conn.close()
                    return

                issue = msg["issue"]

                if issue == CONNECT_ISSUE:
                    print("gfd has connected to rm. \n")
                elif issue == MEMBER_ISSUE:
                    self.handle_membership(msg)
                else:
                    conn.close()
                    return
            except Exception:
                conn.close()
                break

    def handle_membership(self, msg):
        membercount = msg["membercount"]
        memberships = msg["memberships"]

  def print_memberships(self, membercount, memberships):
    p = f"RM: {membercount} members: "
    for mem in memberships:
      p += f"{mem}, "
    print(p.rstrip(', '))


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', dest='rm_id', type=str,
                        help='rm_id', default="RM")
    args = parser.parse_args()
    return args


def main():
    args = getArgs()
    # hb = args.heartbeat_freq
    rm_id = args.rm_id
    rm = GlobalFaultDetector(rm_id)
    rm.start()


if __name__ == "__main__":
    main()
