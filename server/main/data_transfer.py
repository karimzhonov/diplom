from time import time
import cv2
import pickle
import numpy as np

from threading import Thread
from socket import socket
from server import settings
from .models import Lock, Activity, Profile
from .multi_socket import MultiSocket
from .utils import get_pickle, set_pickle
from app.utils import get_emergency_control_status

class Client:
    def __init__(self, lock: Lock, conn: socket = None):
        self.lock = lock
        self.conn = conn

    def main(self):
        pass

    def _out_while_errors(self):
        pass

    def run(self, session):
        while True:
            try:
                if not session.status or not MultiSocket.get_status():
                    break

                self.main()
            except cv2.error:
                continue
            except ConnectionResetError:
                break
            except ConnectionAbortedError:
                break
            except EOFError:
                break
        try:
            self._out_while_errors()
        except AttributeError:
            pass
        self.conn.close()
        session.status = False
        MultiSocket.remove_active_ports(self.lock.port)


class Authentication(Client):
    def _out_while_errors(self):
        self.save_auth((0, 0))

    def save_auth(self, status):
        set_pickle(self.lock.get_last_auth_path(), status)

    def get_auth(self):
        try:
            return get_pickle(self.lock.get_last_auth_path())
        except FileNotFoundError:
            self.save_auth((0, 0))
            return 0, 0

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

    def auth(self, frame: np.array):
        profiles = None
        status = self.check_distance(frame)

        if status:
            status, profiles = self.compare_face(frame)

        if status:
            status = self.check_permission(profiles, self.lock)

        if status:
            Thread(target=Activity.add_activity, args=(profiles, self.lock)).start()
        _, app_status = self.get_auth()
        self.save_auth((status, app_status))

    def main(self) -> None:
        status, app_control = self.get_auth()
        emergency_control_status = get_emergency_control_status()

        if emergency_control_status:
            self.conn.recv(4096)
            answer = pickle.dumps(emergency_control_status)
            self.conn.send(answer)
        elif status or app_control:
            t0 = time()
            while time() - t0 < 5:
                self.conn.recv(4096)
                answer = pickle.dumps(1)
                self.conn.send(answer)
            self.save_auth((0, 0))
        else:
            self.conn.recv(4096)
            answer = pickle.dumps(status)
            self.conn.send(answer)

            frame = cv2.imread(self.lock.get_last_frame_path(), cv2.IMREAD_ANYCOLOR)
            self.auth(frame)


class Frame(Client):
    def __init__(self, lock, conn):
        super().__init__(lock, conn)
        self.frame_size = (480, 640)
        print(self.lock.get_last_video_path())
        self.video_writer = cv2.VideoWriter(self.lock.get_last_video_path(),
                                            cv2.VideoWriter_fourcc(*'MJPG'), 5, self.frame_size)

    def _out_while_errors(self):
        self.video_writer.release()

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
        frame = self.get_frame()
        self.save_frame(frame)
        frame = cv2.resize(frame, self.frame_size).astype('uint8')
        self.video_writer.write(frame)

        answer = pickle.dumps(b'ok')
        self.conn.send(answer)
