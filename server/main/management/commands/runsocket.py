from django.core.management.base import BaseCommand
from main.multi_socket import MultiSocket


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            MultiSocket.set_status(True)
            MultiSocket().run()
        except OSError:
            pass
