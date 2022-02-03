from django.core.management.base import BaseCommand
from main.server_socket import main as socket_start


class Command(BaseCommand):

    def handle(self, *args, **options):
        socket_start()