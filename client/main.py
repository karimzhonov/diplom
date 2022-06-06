import sys
import socket
import cv2
import pickle
from time import sleep
from threading import Thread

import pygame
from config import *
from app import App
from utils import set_running_status, get_running_status
from lock_control import LockControl

# capture = 'http://admin:admin@192.168.1.28:8081'
capture = 0

def get_client_socket(port_clent: int, port_server: int) -> socket.socket or None:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, port_clent))
        s.connect((HOST, port_server))
        return s
    except ConnectionRefusedError:
        return None


class Client:
    def __init__(self, port) -> None:
        self.status = True
        self.port = port
        self.port_server_frame = port*10
        self.port_server_auth = port*10 + 1
        self.port_frame = port*10 + 2
        self.port_auth = port*10 + 3

    def send_frame(self, s: socket.socket, cap: cv2.VideoCapture):
        status, frame = cap.read()
        if frame is None:
            sleep(1)
            return self.send_frame(s, cap)
        for point in frame:
            point = pickle.dumps(point)
            s.send(point)
            s.recv(4096)
        s.send(b'stop')
        s.recv(4096)
        return frame

    def run(self) -> None:
        set_running_status(True)
        s = get_client_socket(self.port, PORT)
        if s:
            task1 = Thread(target=self.run_frame_socket)
            task1.start()
            sleep(3)
            task2 = Thread(target=self.run_auth_socket)
            task2.start()
            sleep(1)
            task1.join()
            task2.join()
            s.close()
            
        pygame.quit()
        sys.exit()

    def run_frame_socket(self) -> None:
        s = get_client_socket(self.port_frame, self.port_server_frame)
        if s:
            app = App(title=f'Lock: {self.port}')
            if isinstance(capture, int):
                video = cv2.VideoCapture(capture, cv2.CAP_DSHOW)
            else:
                video = cv2.VideoCapture(capture)
            while True:
                try:
                    if not get_running_status():
                        break
                    
                    # App
                    app.events_list = []
                    answer = app.lock_control.get_lock_status()
                    if answer:
                        # if door opened, waiting close the door
                        while app.lock_control.get_sensor_status():
                            frame = self.send_frame(s, video)
                            app.view(frame, answer)
                        
                    frame = self.send_frame(s, video)
                    app.view(frame, answer)
                except ConnectionResetError:
                    break
                except ConnectionAbortedError:
                    break
    
            set_running_status(False)
            s.close()
    
    def run_auth_socket(self) -> None:
        lc = LockControl()
        s = get_client_socket(self.port_auth, self.port_server_auth)
        if s:
            while True:
                try:
                    if not get_running_status():
                        break

                    s.send(b'Get')
                    answer = s.recv(4096)
                    answer = pickle.loads(answer)
                    lc.set_lock_status(answer)
                except ConnectionResetError:
                    break
                except ConnectionAbortedError:
                    break
            set_running_status(False)
            s.close()


if __name__ == '__main__':
    try:
        p = int(sys.argv[1])
    except IndexError:
        p = LOCK_PORT
    except ValueError:
        raise ValueError('port must be integer')
    Client(p).run()
