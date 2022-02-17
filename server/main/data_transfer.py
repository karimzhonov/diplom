import os
import cv2
import pickle
import numpy as np

from threading import Thread
from socket import socket
from server import settings
from .models import Lock, Activity, Profile


class Client:
    def __init__(self, lock: Lock, conn: socket):
        self.lock = lock
        self.conn = conn

    def main(self):
        pass

    def run(self, session, s):
        while True:
            try:
                if not session.status:
                    self.conn.close()
                    break
                
                self.main()
            except cv2.error:
                continue
            except EOFError:
                s.close()
                self.conn.close
                session.status = False
                break
            except ConnectionResetError:
                s.close()
                self.conn.close()
                session.status = False
                break
            except ConnectionAbortedError:
                s.close()
                self.conn.close()
                session.status = False
                break
        self.conn.close() 
        s.close() 
        session.status = False



class Authentication(Client):
    def save_auth(self, status):
        try:
            with open(self.lock.get_last_auth_path(), 'wb') as file:
                pickle.dump(status, file)
        except EOFError:
            self.save_auth(status)

    def get_auth(self):
        try:
            with open(self.lock.get_last_auth_path(), 'rb') as file:
                return pickle.load(file)
        except EOFError:
            return self.get_auth()

    @staticmethod
    def check_distance(frame: np.array) -> int:
        from mediapipe.python.solutions.face_mesh import FaceMesh

        def get_prefigure(lx, ly, rx, ry):
            return ((lx - rx) ** 2 + (ly - ry) ** 2) ** (1 / 2)

        def get_distance(dis_eyes):
            return settings.FOCAL_DEFAULT * settings.EYES_DISTACE_DEFAULT / dis_eyes

        def get_focal(dis_eyes: float, d: float):
            return d * dis_eyes / settings.EYES_DISTACE_DEFAULT

        status = 0
        try:
            h, w, _ = frame.shape
            coordinates = []

            detector = FaceMesh(max_num_faces=10)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            landmarks = detector.process(frame_rgb).multi_face_landmarks
            if landmarks:
                for point in landmarks:
                    left_eye = point.landmark[23]
                    right_eye = point.landmark[253]
                    lx, ly = int(left_eye.x * w), int(left_eye.y * h)
                    rx, ry = int(right_eye.x * w), int(right_eye.y * h)
                    coordinates.append(((lx, ly), (rx, ry)))
            if coordinates:
                left, right = coordinates[0]
                min_dis_eyes = get_prefigure(*left, *right)
                for (lx, ly), (rx, ry) in coordinates:
                    dis = get_prefigure(lx, ly, rx, ry)
                    if min_dis_eyes > dis:
                        min_dis_eyes = dis

                distance_to_camera = get_distance(min_dis_eyes)
                if distance_to_camera < settings.MAX_AUTH_DISTANCE:
                    status = 1
        except AttributeError:
            pass
        return status

    @staticmethod
    def compare_face(frame: np.array) -> tuple:
        import face_recognition as fr

        status = 0
        profile = []
        true_face_encs, profiles = Profile.get_profiles_encs()

        frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locs = fr.face_locations(frame)
        face_encs = fr.face_encodings(frame, face_locs)

        for enc in face_encs:
            flags = fr.compare_faces(true_face_encs, enc)

            for i, flag in enumerate(flags):
                if flag:
                    status = 1
                    profile.append(profiles[i])

        return status, profile

    @staticmethod
    def check_permission(profiles: list[Profile], lock) -> int:
        status = 0
        for profile in profiles:
            if profile.check_permissions(lock):
                status = 1
        return status

    def auth(self, frame: np.array) -> int:
        profiles = None
        status = self.check_distance(frame)

        if status:
            status, profiles = self.compare_face(frame)

        if status:
            status = self.check_permission(profiles, self.lock)

        if status:
            Thread(target=Activity.add_activity, args=(profiles, self.lock)).start()
        self.save_auth(status)

    def main(self) -> None:
        self.conn.recv(4096)
        if not os.path.exists(self.lock.get_last_frame_path()):
            answer = pickle.dumps(0)
            self.conn.send(answer)
            return
        frame = cv2.imread(self.lock.get_last_frame_path(), cv2.IMREAD_ANYCOLOR)
        save_task = Thread(target=self.auth, args=(frame,))
        save_task.start()

        if not os.path.exists(self.lock.get_last_auth_path()):
            answer = pickle.dumps(0)
            self.conn.send(answer)
            return
        answer = self.get_auth()
        answer = pickle.dumps(answer)
        self.conn.send(answer)
        save_task.join()


class Frame(Client):
    def get_frame(self) -> np.array:
        data = []
        while True:
            answer = self.conn.recv(4096)
            if answer == b'stop':
                break
            answer = pickle.loads(answer)
            data.append(answer)
            self.conn.send(b'ok')
        return np.array(data)

    def save_frame(self, frame) -> None:
        frame_path = self.lock.get_last_frame_path()
        cv2.imwrite(frame_path, frame)

    def main(self) -> None:
        try:
            frame = self.get_frame()

            Thread(target=self.save_frame, args=(frame,)).start()

            answer = pickle.dumps(b'ok')
            self.conn.send(answer)
        except OSError:
            self.conn.close()
