import os
import cv2
import pickle
import numpy as np
import face_recognition as fr
from datetime import datetime

from threading import Thread
from django.db import models
from django.conf import settings


class Permission(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    class Meta:
        pass

    def __str__(self) -> str:
        return f'{self.name}'

    @staticmethod
    def check_permission(profiles, lock) -> int:
        status = 0

        for profile in profiles:
            for per in profile.permissions.all():
                if per.pk == lock.permission.pk:
                    status = 1

        return status


class Profile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    img = models.ImageField(upload_to='profiles/', blank=True)
    permissions = models.ManyToManyField(Permission)
    is_active = models.BooleanField(default=True)

    class Meta:
        pass

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @classmethod
    def get_profiles_encs(cls) -> tuple:
        profiles = cls.objects.filter(is_active=True)
        data = []
        profiles_list = []
        for point in profiles:
            img_path = f'{settings.BASE_DIR}{point.img.url}'
            img = fr.load_image_file(img_path)
            img_enc = fr.face_encodings(img)[0]
            data.append(img_enc)
            profiles_list.append(point)
        return data, profiles_list

    @classmethod
    def compare_face(cls, frame: np.array) -> tuple:
        status = 0
        profile = []
        true_face_encs, profiles = cls.get_profiles_encs()

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


class Lock(models.Model):
    port = models.IntegerField()
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        pass

    def __str__(self) -> str:
        return f'{self.port}'

    @classmethod
    def init(cls, port, conn):
        locks = cls.objects.filter(port=port)
        if not len(locks):
            lock = cls.objects.create(port=port, permission_id=1)
        else:
            lock = locks[0]
        lock.conn = conn
        lock.dir_path = f'{settings.BASE_DIR}/tmp/{port}'
        lock.frame_path = f'{lock.dir_path}/frame.png'
        return lock

    def get_frame(conn) -> np.array:
        data = []
        while True:
            answer = conn.recv(4096)
            if answer == b'stop':
                break
            answer = pickle.loads(answer)
            data.append(answer)
            conn.send(b'ok')
        return np.array(data)

    @staticmethod
    def save_frame(port, frame) -> None:
        dir_path = f'{settings.BASE_DIR}/tmp/{port}'
        frame_path = f'{dir_path}/frame.png'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        cv2.imwrite(frame_path, frame)

    @staticmethod
    def check_distance(frame: np.array) -> int:
        from mediapipe.python.solutions.face_mesh import FaceMesh
        
        def get_pifagure(lx, ly, rx, ry):
            return ((lx-rx)**2 + (ly-ry)**2)**(1/2)

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
                min_dis_eyes = get_pifagure(*left, *right)
                for (lx, ly), (rx, ry) in coordinates:
                    dis = get_pifagure(lx, ly, rx, ry)
                    if min_dis_eyes > dis:
                        min_dis_eyes = dis
                
                distance_to_camera = get_distance(min_dis_eyes)
                if distance_to_camera < settings.MAX_AUTH_DISTANCE:
                    status = 1
        except AttributeError:
            pass
        return status  

    def auth(self, frame: np.array) -> int:
        profiles = None
        status = self.check_distance(frame)

        if status:
            status, profiles = Profile.compare_face(frame)

        if status:
            status = Permission.check_permission(profiles, self)
  
        if status:
            Thread(target=Activity.add_activity, args=(profiles, self)).start()

        return status

    @classmethod
    def run_frames(cls, session, conn, port) -> None:
        while True:
            try:
                if not session.status:
                    break

                frame = cls.get_frame(conn)

                cls.save_frame(port, frame)

                cv2.imshow(f'{port}', frame)
                if cv2.waitKey(1) == ord('q'):
                    session.status = False
                    break

                answer = pickle.dumps(b'ok')
                conn.send(answer)
            except ConnectionResetError:
                break
            except EOFError:
                break
        conn.close() 

    def run_auth(self, session) -> None:
        while True:
            try:
                if not session.status:
                    break
                question = self.conn.recv(4096)
                 
                frame = cv2.imread(self.frame_path, cv2.IMREAD_ANYCOLOR)
                answer = self.auth(frame)
                answer = pickle.dumps(answer)
                self.conn.send(answer)
            except cv2.error:
                continue
            except ConnectionResetError:
                break
            except EOFError:
                break


class Activity(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    lock = models.ForeignKey(Lock, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now=True)

    class Meta:
        pass

    def __str__(self) -> str:
        return f'{self.profile}'

    def as_console(self) -> None:
        print(f'[INFO] Person: {self.profile}, Lock: {self.lock}. Date: {self.date_time.date()}, Time: {self.date_time.time()}')

    @classmethod
    def add_activity(cls, profiles: list[Profile], lock: Lock) -> None:
        for profile in profiles:
            acts = cls.objects.filter(profile__pk=profile.pk, lock__pk=lock.pk).order_by('-date_time')
            if not acts:
                cls.objects.create(profile_id=profile.pk, lock_id=lock.pk).as_console()
            else:
                last_act = acts[0]
                now = datetime.now()
                date_format = "%Y-%m-%d %H:%M:%S"
                a = datetime.strptime(str(now).split('.')[0], date_format)
                b = datetime.strptime(str(last_act.date_time).split('.')[0], date_format)
                delta = a - b
                if delta.total_seconds() > settings.NOT_AUTHING_TIME:
                    cls.objects.create(profile_id=profile.pk, lock_id=lock.pk).as_console()

