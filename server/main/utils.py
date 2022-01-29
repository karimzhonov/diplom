from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.conf import settings
import pickle
import os



def _wb(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

def _rb(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)


class IFieldFile(ImageFieldFile):
    def save(self, name: str, content, save: bool = ...) -> None:
        super().save(name, content, save)

        file_path = os.path.join(settings.BASE_DIR, 'temp', name)
        _wb(content, file_path)

      
        



class CustomImageField(models.ImageField):
    attr_class = IFieldFile
