import socket

tcpclient=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcpclient.connect(("127.0.0.1",9011))
while True:
    while True:
        data=input('>>').strip()
        print("client request message:(" + data + ") sent")
        tcpclient.send(data.encode('utf-8'))
        ret=tcpclient.recv(1024)
        print(ret.decode('utf-8'))
