import socket
import threading

def handle(conn,port):
    while True:
        try:
            data=conn.recv(1024)
            if data == "Are you alive".encode('utf-8'):
                ret_data="I am alive".encode('utf-8')
                conn.send(ret_data)
            elif data:
                print("Client",port, "requested message: " + data.decode("utf-8"))
                ret_data="Server received the message: " + data.decode("utf-8")
                print("My state is alive")
                conn.send(ret_data.encode('utf-8'))
                print("Have replied to the client", port)
            else:
                 conn.close()
                 break
        except Exception:
                continue


#            s.send(data)

if __name__ == '__main__':
    tcpserver=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcpserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    tcpserver.bind(("",9011))
    tcpserver.listen(20)

    while True:
        conn,addr=tcpserver.accept()
        t=threading.Thread(target=handle,args=(conn,addr))
        t.setDaemon(True)
        t.start()