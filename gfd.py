import socket, argparse, time, json, threading, socket
from color import * 

PORT = 1234
IP = socket.gethostbyname(socket.gethostname())
LISTENING_INTERVAL = 3
FORMAT = 'utf-8'
SIZE = 1024
HEARTBEAT_MSG = "Are you alive?"
ALIVE_MSG = " is alive"
DEAD_MSG = " is dead"
HEARTBEAT_RELPY = "Yes, I am."
LFD_HEADER = "lfd"
HEARTBEAT_ISSUE = "heartbeat"
REPLICA_ISSUE = "replica"

class GlobalFaultDetector():
  def __init__(self, gfd_id, heartbeat_freq, ip = IP, port = PORT):
    self.heartbeat_freq = heartbeat_freq
    self.lfds_addr = {} # dic of lfd ips {str_id: addr}
    self.memberships = {}
    self.membercount = 0
    self.port = port
    self.ip = ip 
    self.gfd_id = gfd_id

    # self.heartbeat_msg = {
    #      "header": "gfd",
    #      "gfd_id": self.gfd_id,
    #      "message": HEARTBEAT_MSG
    #   } 
    self.heartbeat_msg = HEARTBEAT_MSG
    self.heartbeat_msg = self.heartbeat_msg.encode(FORMAT)

    print_color(f"[STARTING] Starting {self.gfd_id} on {self.ip}:{self.port}", COLOR_RED)
    print()
    
    self.print_memberships()

    self.gfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.gfd.bind( (self.ip, self.port) )
    self.gfd.listen()
  
  def start(self):
    while True:
      conn, addr = self.gfd.accept()
      thread = threading.Thread(target=self.handle_lfd_connection, args = (conn, addr))
      thread.daemon = True
      thread.start()

  def handle_lfd_connection(self, conn, addr):
    while True:
        try:
          msg = conn.recv(SIZE).decode(FORMAT)
          msg = json.loads(msg)
          header = msg["header"]
          if header != LFD_HEADER:
            conn.close()
            return
          issue = msg["issue"]
          lfd_id = msg["lfd_id"]
          server_id = msg["server_id"]
          message = msg["message"]
          if issue == HEARTBEAT_ISSUE:
             self.lfds_addr[lfd_id]=addr
             self.sending_heartbeat(conn, server_id, lfd_id)
          elif issue == REPLICA_ISSUE:
              self.handle_replica(message)
          else:
            conn.close()
            return
        except Exception:
            conn.close()
            break


  def sending_heartbeat(self, conn, server_id, lfd_id):
    while True:
      try:
          conn.send(self.heartbeat_msg)
          print_color(f" {self.gfd_id} sending heartbeat to {lfd_id}", COLOR_RED)
      except:
          continue
      
      try:
          msg = conn.recv(SIZE).decode(FORMAT)
          if msg != HEARTBEAT_RELPY:
              print_color(lfd_id + DEAD_MSG + "\n", COLOR_ORANGE)
              self.lfds_addr.pop(lfd_id)
              self.memberships.pop(server_id)
              self.membercount -= 1
              self.print_memberships()
          else:
              print_color(lfd_id + ALIVE_MSG + "\n", COLOR_ORANGE)
      except Exception:
          print("\n[EXCEPTION] " + lfd_id + DEAD_MSG , COLOR_ORANGE)
          self.lfds_addr.pop(lfd_id)
          self.memberships.pop(server_id)
          self.membercount -= 1
          self.print_memberships()
          conn.close()
          return

      time.sleep(self.heartbeat_freq)
  
  def handle_replica(self, message):
    # msg = json.loads(msg)
    message = message.split()
    server_id =  message[-1]
    if "add" in message:
      self.memberships[server_id] = True
      self.membercount += 1
    elif "delete" in message:
      self.memberships.pop(server_id)
      self.membercount -= 1
    else:
      example_msg = "LFD1: add replica S1" 
      print_color(f"INVALID msg: {message} ", COLOR_MAGENTA)
      print_color(f"EXPECTED: {example_msg} such format", COLOR_MAGENTA)
      print()
    self.print_memberships()

  def print_memberships(self):
    p = f"GFD: {self.membercount} members: "
    for mem in self.memberships:
      p += f"{mem}, "
    print(p.rstrip(', '))

def getArgs():
  parser = argparse.ArgumentParser()
  parser.add_argument('-hb', dest='heartbeat_freq', type=int, help='heartbeat_freq', default=2)
  parser.add_argument('-g', dest='gfd_id', type=str, help='gfd_id', default="GFD1")
  args = parser.parse_args()
  return args

def main():
  args = getArgs()
  hb = args.heartbeat_freq
  gfd_id = args.gfd_id
  gfd = GlobalFaultDetector(gfd_id, hb)
  gfd.start()

if __name__ == "__main__":
  main()