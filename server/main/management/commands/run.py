from threading import Thread
from django.core.management.base import BaseCommand
from main.multi_socket import MultiSocket
import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        MultiSocket.set_status(True)
        Thread(target=os.system, args=('python manage.py runserver',)).start()
        Thread(target=os.system, args=('python manage.py runsocket',)).start()
        Thread(target=os.system, args=('python manage.py runapp',)).start()
    
