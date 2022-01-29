from django.db import models
from .utils import CustomImageField


class Profile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    available_locks = models.ManyToManyField('Lock', blank=True)
    is_guest = models.BooleanField(default=True)
    img = CustomImageField(upload_to='profiles/', blank=True)


class Lock(models.Model):
    is_room = models.BooleanField(default=False)
    is_checkpoint = models.BooleanField(default=False)

