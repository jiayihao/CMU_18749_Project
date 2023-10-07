import socket, argparse, time, json, threading, socket

PORT = 8888
IP = socket.gethostbyname(socket.gethostname())
LISTENING_INTERVAL = 3
FORMAT = 'utf-8'
SIZE = 1024
HEARTBEAT_MSG = "Are you alive?"
ALIVE_MSG = " is alive"
DEAD_MSG = " is dead"
HEARTBEAT_RELPY = "Yes, I am."

class GlobalFaultDetector():
  def __init__(self, heartbeat_freq, ip = IP, port = PORT):
    self.heartbeat_freq = heartbeat_freq
    self.heartbeat_count = 0
    self.lfds_addr = {} # dic of lfd ips {str_id: addr}
    self.live_lfds = set()
    self.memberships = {}
    self.membercount = 0
    self.port = port
    self.ip = ip 

    print(f"[STARTING] Starting server on {self.ip}:{self.port}")
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server.bind( (self.ip, self.port) )
    self.server.listen()
  
  def start(self):
    thread_heartbeats = threading.Thread(target=self.sending_heartbeats,args=())
    thread_listening = threading.Thread(target=self.listening_conn, args=())
    thread_heartbeats.start()
    thread_listening.start()

  def sending_heartbeats(self):
    print('start sending heartbeat')
    threads = []
    while(True):
      time.sleep(LISTENING_INTERVAL)
      for lfd_id, lfd_addr  in self.lfds_addr.items():
        if lfd_id not in self.live_lfds:
          thread = threading.Thread(target=self.sending_heartbeat, args=(lfd_id, lfd_addr)) 
          thread.start()
          threads.append(thread)
          self.live_lfds.add(lfd_id)


  def sending_heartbeat(self, lfd_id, lfd_addr):
    gfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gfd.connect( lfd_addr )
    # print self ip        
    print(f"[STARTING] Starting server on { (self.ip, self.port) }...\n")
    print("[CONNECTED] {} connected to {} at {}".format(self.gfd, lfd_id, lfd_addr))

    while True:
      time.sleep(self.heartbeat_freq)
      data = {
         "header": "gfd",
         "message": HEARTBEAT_MSG
      } 
      try:
          gfd.send(json.dumps(data).encode(FORMAT))
          print("[{}] {} sending heartbeat to {}".format(self.heartbeat_count, self.lfd_id, lfd_id))
      except:
          continue
      
      try:
          msg = gfd.recv(SIZE).decode(FORMAT)
          if msg != HEARTBEAT_RELPY:
              print(lfd_id + DEAD_MSG)
          else:
              print(lfd_id + ALIVE_MSG + "\n")
              self.heartbeat_count += 1
      except Exception:
          print("\n" + lfd_id + DEAD_MSG)

  def listening_conn(self):
    print('start listening conn')
    while True:
      conn, addr = self.server.accept()
      thread = threading.Thread(target=self.handle_lfd, args = (conn, addr))
      thread.start()
      print(f"\n[ACTIVE CONNECTIONS] {str(len(self.lfds_addr))}\n")
  
  def handle_lfd(self, conn, addr):
    print("\n[NEW CONNECTION] {} connected\n".format(addr))
    while True:
      try:
        msg = conn.recv(SIZE).decode(FORMAT)
        msg = json.loads(msg)
        lfd_id = msg["lfd_id"]
        message = msg["message"]
        server_id =  message[:-2]
        if lfd_id not in self.lfds_addr.keys():
           self.lfds_addr[lfd_id]=addr
        if "add" in message:
           self.memberships[server_id] = True
           self.membercount += 1
        elif "delete" in message:
           self.membership[server_id] = False
           self.membercount -= 1
           
        else:
          example_msg = "LFD1: add replica S1" 
          print(f"INVALID msg: {message} ")
          print(f"EXPECTED: {example_msg} such format")

      except Exception:
        print(str(addr) + " is disconnected...\n")
        break

def getArgs():
  parser = argparse.ArgumentParser()
  parser.add_argument('-hb', dest='heartbeat_freq', type=int, help='heartbeat_freq', default=2)
  args = parser.parse_args()
  return args

def main():
  args = getArgs()
  hb = args.heartbeat_freq
  gfd = GlobalFaultDetector(hb)
  gfd.start()

if __name__ == "__main__":
  main()