import socket
from threading import Thread
from .models import Lock
from .data_transfer import Authentication, Frame


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
        lock = Lock.init(self.port)
        auth = Authentication(lock, connection)
        auth.run(self)

    def run_frames(self) -> None:
        s = get_server_socket(self.port_frame)
        connection, address = s.accept()
        lock = Lock.init(self.port)
        frame = Frame(lock, connection)
        frame.run(self)

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
            ses = Session(port)
            Thread(target=ses.run).start()
    
