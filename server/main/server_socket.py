import socket
from threading import Thread
from .models import Lock


def client_accept(conn, addr):
    print('Lock connected: ', addr)
    host, port = addr
    lock = Lock.init(port, conn)
    lock.run()

def main():
    HOST = 'localhost'
    PORT = 5000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    print('Server started')
    while True:
        connection, address = s.accept()
        Thread(target=client_accept, args=(connection, address)).start()


if __name__ == '__main__':
    main()
    
