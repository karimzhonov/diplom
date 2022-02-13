from django.core.management.base import BaseCommand
from app.main import App


class Command(BaseCommand):

    def handle(self, *args, **options):
        App().run()
