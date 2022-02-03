from os import name
from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
]
