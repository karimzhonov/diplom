from sympy import im


import socket
import cv2
import pickle
import face_recognition as fr

def send(s: socket.socket, cap: cv2.VideoCapture):
    s.send(take_frame(cap))
    return s.recv(4096).decode()


def take_frame(cap: cv2.VideoCapture):
    _, frame = cap.read()
    frame_enc = fr.face_encodings(frame)
    return pickle.dumps(frame_enc, protocol=pickle.HIGHEST_PROTOCOL)
