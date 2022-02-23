import socket
from threading import Thread

from .models import Lock
from .utils import set_pickle, get_pickle

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
            lock = Lock.objects.get_or_create(port=self.port)[0]
            auth = Authentication(lock, connection)
            auth.run(self)
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
            lock = Lock.objects.get_or_create(port=self.port)[0]
            frame = Frame(lock, connection)
            frame.run(self)
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
    from server.settings import BASE_DIR

    PORT = 5000
    filename = f'{BASE_DIR}/tmp/start.pickle'
    active_ports = f'{BASE_DIR}/tmp/active.pickle'

    @classmethod
    def _set_active_ports(cls, value):
        set_pickle(cls.active_ports, value)

    @classmethod
    def get_active_ports(cls):
        try:
            return get_pickle(cls.active_ports)
        except FileNotFoundError:
            cls._set_active_ports([])
            return []

    @classmethod
    def add_active_ports(cls, port: int):
        ports = cls.get_active_ports()
        ports.append(port)
        cls._set_active_ports(ports)

    @classmethod
    def remove_active_ports(cls, port: int):
        try:
            ports = cls.get_active_ports()
            index = ports.index(port)
            ports.pop(index)
            cls._set_active_ports(ports)
        except ValueError:
            pass

    @classmethod
    def get_status(cls):
        return get_pickle(cls.filename)

    @classmethod
    def set_status(cls, status: bool):
        set_pickle(cls.filename, status)

    def run(self) -> None:
        s = get_server_socket(self.PORT)
        print('Server started')
        while True:
            connection, address = s.accept()
            if not self.get_status():
                connection.close()
                s.close()
                self._set_active_ports([])
                break
            print('Client connected: ', address)
            host, port = address
            # Active Ports Set
            self.add_active_ports(port)

            ses = Session(port, connection)
            Thread(target=ses.run).start()
