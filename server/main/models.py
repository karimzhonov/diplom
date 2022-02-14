import face_recognition as fr
from datetime import datetime
from django.db import models
from server import settings


class Permission(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    bio = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешении'
        ordering = ['pk']

    def __str__(self) -> str:
        return f'{self.name}'


class Profile(models.Model):
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    bio = models.TextField(blank=True, verbose_name='Дополнительные данные')
    img = models.ImageField(upload_to='profiles/', blank=True, verbose_name='Фото')
    permissions = models.ManyToManyField(Permission, verbose_name='Разрешено')
    is_active = models.BooleanField(default=True, verbose_name='Астивный пользователь')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['is_active', 'pk']

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def check_permissions(self, lock):
        status = 0
        for per in self.permissions.all():
            if per.pk == lock.permission.pk:
                status = 1
        return status

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


class Lock(models.Model):
    port = models.IntegerField(verbose_name='Порт соединение', unique=True)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, blank=True, verbose_name='Разрешено')
    bio = models.TextField(blank=True, verbose_name='Дополнительные данные')

    class Meta:
        verbose_name = 'Замок'
        verbose_name_plural = 'Замки'
        ordering = ['port']

    def __str__(self) -> str:
        return f'{self.port}'

    @classmethod
    def init(cls, port):
        locks = cls.objects.filter(port=port)
        if not len(locks):
            lock = cls.objects.create(port=port, permission_id=1)
        else:
            lock = locks[0]
        return lock

    def get_last_frame_path(self):
        return f'{settings.BASE_DIR}/tmp/{self.port}_frame.png'


class Activity(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Пользователь')
    lock = models.ForeignKey(Lock, on_delete=models.CASCADE, verbose_name='Замок')
    date_time = models.DateTimeField(auto_now=True, verbose_name='Дата и время')

    class Meta:
        verbose_name = 'Активность'
        verbose_name_plural = 'Активности'
        ordering = ['-date_time']

    def __str__(self) -> str:
        return f'{self.profile}'

    def as_console(self) -> None:
        print(f'[INFO] Person: {self.profile}, Lock: {self.lock}. '
              f'Date: {self.date_time.date()}, Time: {self.date_time.time()}')

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
