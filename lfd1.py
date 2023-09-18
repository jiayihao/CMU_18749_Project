import socket
import time

tcpclient=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcpclient.connect(("127.0.0.1",9011))
def heartbeat():
    while True:
        while True:
            time.sleep(2)
            checkmessage="Are you alive"
            try:
                tcpclient.send(checkmessage.encode('utf-8'))
            except:
                continue
            try:
                if tcpclient.recv(1024) != ("I am alive".encode('utf-8')):
                    print("Server Died")
                else:
                    print("server alive")
            except Exception:
                print("Server Died")

if __name__ == '__main__':
    heartbeat()
 #           ret=tcpclient.recv(1024)
 #           print(ret.decode('utf-8'))
