import socket, argparse, time, json, threading, socket
from utilities import * 

PORT = 5555
IP = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
SIZE = 1024
RM_HEADER = "rm"
CONNECT_ISSUE = "gfd to rm connect"
MEMBER_ISSUE = "membership change"

class ProjectManager():
  def __init__(self, rm_id, rm_active, ip = IP, port = PORT):
    self.port = port
    self.ip = ip 
    self.rm_id = rm_id
    self.rm_active = rm_active
    # when rm_active = True, it is active. When rm_active = False, it is passive.
    self.primary = ""
    self.old_membership = {}
    self.servers = load_config("servers")
    print(f"[STARTING] Starting {self.rm_id} on {self.ip}:{self.port} \n")
    
    # self.print_memberships()

    self.rm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.rm.bind( (self.ip, self.port) )
    self.rm.listen()
  
  def start(self):
    while True:
      conn, addr = self.rm.accept()
      thread = threading.Thread(target=self.handle_rm_connection, args = (conn, addr))
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
    
    if (self.rm_active == False):
      if ((self.primary == "") or (self.primary not in memberships.keys())): # only passive need to consider primary change
        self.primary = next(iter(memberships.keys()))
        for server in self.servers:
          try:
            self.notify_primary_change(self.primary, (server.ip, server.port))
          except Exception:
            pass  

    # member++
    for mem in memberships:
      if mem not in self.old_membership.keys():
        for server in self.servers:
          try:
            self.notify_new_membersip(mem, (server.ip, server.port))
          except Exception:
            pass 
        
      
    self.print_memberships(membercount, memberships)
    self.old_membership = memberships
    print("444444444")


  def print_memberships(self, membercount, memberships):
    p = f"RM: {membercount} members: "
    for mem in memberships:
      p += f"{mem}, "
    print(p.rstrip(', '))

  
  def notify_primary_change(self, prim_id, server_addr):
    to_server_prim = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    to_server_prim.connect(server_addr)
    to_server_prim_msg = {
        "header": "primary change",
        "primary": prim_id
    }
    to_server_prim_msg = json.dumps(to_server_prim_msg).encode(FORMAT)
    to_server_prim.send(to_server_prim_msg)
    to_server_prim.close()

  def notify_new_membersip(self, new_id, server_addr):
    to_server_new = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    to_server_new.connect(server_addr)
    to_server_new_msg = {
        "header": "new member",
        "primary": new_id
    }
    to_server_new_msg = json.dumps(to_server_new_msg).encode(FORMAT)
    to_server_new.send(to_server_new_msg)
    to_server_new.close()
  

def getArgs():
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', dest='rm_id', type=str, help='rm_id', default="RM")
  parser.add_argument('--active', dest='active', action='store_true', required=False, default=False)
  args = parser.parse_args()
  return args

def main():
  args = getArgs()
  # hb = args.heartbeat_freq
  rm_id = args.rm_id
  rm_active = args.active
  rm = ProjectManager(rm_id,rm_active)
  rm.start()

if __name__ == "__main__":
  main()