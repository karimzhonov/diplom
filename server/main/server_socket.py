import socket
from threading import Thread
from .models import Lock


HOST = 'localhost'


def get_server_socket(port) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, port))
    s.listen(10)
    return s


class Session:
    def __init__(self, port: int) -> None:
        self.port = port
        self.port_frame = port*10
        self.port_auth = port*10 + 1
        self.status = True

    def run_auth(self) -> None:
        s = get_server_socket(self.port_auth)
        connection, address = s.accept()
        lock = Lock.init(self.port, connection)
        lock.run_auth(self)

    def run_frames(self) -> None:
        s = get_server_socket(self.port_frame)
        connection, address = s.accept()
        Lock.run_frames(self, connection, self.port, show=True)

    def run(self) -> None:
        Thread(target=self.run_frames).start()
        Thread(target=self.run_auth).start()


class MultiSocket:
    PORT = 5000    
    
    def run(self) -> None:
        s = get_server_socket(self.PORT)
        print('Server started')
        while True:
            connection, address = s.accept()
            print('Client connected: ', address)
            host, port = address
            Session(port).run()


if __name__ == '__main__':
    MultiSocket().run()
    
