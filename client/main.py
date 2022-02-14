import sys
import socket
import cv2
import pickle
from time import sleep

from threading import Thread
from lock_control import Control

HOST = "localhost"
PORT = 5000
LOCK_PORT = 5001


def get_client_socket(port_clent: int, port_server: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, port_clent))
    s.connect((HOST, port_server))
    return s


class Client:
    def __init__(self, port) -> None:
        self.status = True
        self.port = port
        self.port_server_frame = port*10
        self.port_server_auth = port*10 + 1
        self.port_frame = port*10 + 2
        self.port_auth = port*10 + 3

    def send_frame(self, s: socket.socket, cap: cv2.VideoCapture) -> None:
        try:
            _, frame = cap.read()
            for point in frame:
                point = pickle.dumps(point)
                s.send(point)
                s.recv(4096)
            s.send(b'stop')
        except ConnectionAbortedError:
            self.status = False
            s.close()
        except ConnectionResetError:
            self.status = False
            s.close()

    def run(self) -> None:
        while True:
            try:
                sleep(1)
                s = get_client_socket(self.port, PORT)
                sleep(0.5)
                task1 = Thread(target=self.run_frame_socket)
                task1.start()
                sleep(3)
                task2 = Thread(target=self.run_auth_socket)
                task2.start()
                sleep(1)
                task1.join()
                task2.join()
                s.close()
            except OSError:
                continue

    def run_frame_socket(self) -> None:
        video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        s = get_client_socket(self.port_frame, self.port_server_frame)

        while True:
            try:
                self.send_frame(s, video)
                answer = s.recv(4096)
            except ConnectionAbortedError:
                s.close()
                break
            except OSError:
                s.close
                break
    
    def run_auth_socket(self) -> None:
        lock_controller = Control(is_door_locked=True)
        s = get_client_socket(self.port_auth, self.port_server_auth)

        while True:
            try:
                s.send(b'Get')
                answer = s.recv(4096)
                answer = pickle.loads(answer)
                lock_controller.control(bool(int(answer)))
            except ConnectionAbortedError:
                s.close()
                break
            except OSError:
                s.close()
                break

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = LOCK_PORT
    except ValueError:
        raise ValueError('port must be integer')
    Client(port).run()
    
