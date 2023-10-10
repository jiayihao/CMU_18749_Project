import socket

IP = socket.gethostbyname("")
PORT = 8888
ADDR = (IP, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()