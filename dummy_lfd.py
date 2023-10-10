import socket
import json
import time
import argparse

PORT = 8888

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='ip', type=str, help='gfd ip', default='S1')
    parser.add_argument('-p', dest='port', type=str, help='port', default=PORT)
    args = parser.parse_args()
    return args
          
def test(addr):
  addr = (socket.gethostbyname(''), 8889)
  lfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  lfd.bind(addr)
  lfd.listen()
  print(f"[STARTING] Starting server on {addr}...\n")


  lfd.connect(addr)
  conn, addr = lfd.accept()
  msg = conn.recv(1024).decode('utf-8')
  print(f'msg is {msg}')

          
if __name__ == '__main__':
  args = getArgs()
  addr = (args.ip, int(args.port))
  test(addr)