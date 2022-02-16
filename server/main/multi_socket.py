import pickle
import socket
from threading import Thread

from server.settings import BASE_DIR
from .models import Lock


HOST = 'localhost'


def get_server_socket(port) -> socket.socket:
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, port))
    s.listen(10)
    return s
        

class Session:
    def __init__(self, port: int, conn: socket.socket) -> None:
        self.port = port
        self.port_frame = port*10
        self.port_auth = port*10 + 1
        self.status = True
        self.conn = conn

    def run_auth(self) -> None:
        from .data_transfer import Authentication
        try:
            s = get_server_socket(self.port_auth)
            connection, address = s.accept()
            lock = Lock.init(self.port)
            auth = Authentication(lock, connection)
            auth.run(self, s)
            print(f'Port closed: {self.port_auth}')
            connection.close()
            s.close()
        except IndexError:
            pass

    def run_frames(self) -> None:
        from .data_transfer import Frame
        try:
            s = get_server_socket(self.port_frame)
            connection, address = s.accept()
            lock = Lock.init(self.port)
            frame = Frame(lock, connection)
            frame.run(self, s)
            print(f'Port closed: {self.port_frame}')
            connection.close()
            s.close()
        except IndexError:
            pass

    def run(self) -> None:
        Thread(target=self.run_frames).start()
        Thread(target=self.run_auth).start()
        self.conn.close()


class MultiSocket:
    PORT = 5000
    filename = f'{BASE_DIR}/tmp/start.pickle'

    @classmethod
    def get_status(cls):
        with open(cls.filename, 'rb') as file:
            return pickle.load(file)

    @classmethod
    def set_status(cls, status: bool):
        with open(cls.filename, 'wb') as file:
            pickle.dump(status, file)

    def run(self) -> None:
        s = get_server_socket(self.PORT)
        print('Server started')
        while True:
            connection, address = s.accept()
            if not self.get_status():
                connection.close()
                s.close()
                break
            print('Client connected: ', address)
            host, port = address
            ses = Session(port, connection)
            Thread(target=ses.run).start()
