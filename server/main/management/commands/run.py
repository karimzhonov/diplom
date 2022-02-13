from threading import Thread
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):

    def handle(self, *args, **options):
        Thread(target=os.system, args=('python manage.py runserver',)).start()
        Thread(target=os.system, args=('python manage.py runsocket',)).start()
        Thread(target=os.system, args=('python manage.py runapp',)).start()
