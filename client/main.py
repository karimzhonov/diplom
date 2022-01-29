import socket
import cv2
from utils import send

HOST = "localhost"
PORT = 5555


def main():
    video = cv2.VideoCapture(0)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    question = s.recv(4096).decode()
    print(question, end='')
    answer = input('')
    s.send(answer.encode())
    _flag = bool(s.recv(4096).decode())
    print('Password is ', _flag)
    while _flag:
        answer = send(s, video)

        

if __name__ == '__main__':
    main()