from django.core.management.base import BaseCommand
from main.server_socket import MultiSocket


class Command(BaseCommand):

    def handle(self, *args, **options):
        MultiSocket().run()
