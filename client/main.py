import socket
import cv2
import pickle

HOST = "localhost"
PORT = 5000
LOCK_PORT = 5001


def send_frame(s: socket.socket, cap: cv2.VideoCapture):
    _, frame = cap.read()
    for point in frame:
        point = pickle.dumps(point)
        s.send(point)
        s.recv(4096)
    s.send(b'stop')


def main():
    video = cv2.VideoCapture(0)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, LOCK_PORT))
    s.connect((HOST, PORT))
    
    while True:
        send_frame(s, video)
        answer = s.recv(4096)
        answer = pickle.loads(answer)
        print(answer)
        

if __name__ == '__main__':
    main()