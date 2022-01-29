from config import BASE_DIR, DB_DIR
from utils import get_pk, _wb, _rb
import pickle
import os

class Profile:
    db_path = os.path.join(DB_DIR, 'dataset', f'{__name__.lower()}.pickle')

    def __init__(self, first_name: str, last_name: str, 
    bio: str=None, available_locks: list=None, is_guest: bool=None, img: str=None, pk: int=None,is_active: bool=None) -> None:
        self.pk = get_pk(self)
        self.is_active = is_active
        self.first_name = first_name
        self.last_name = last_name
        self.bio= bio
        self.available_locks= available_locks
        self.is_guest = is_guest
        self.img = img
        self.img_enc = None


    def save_new(self):
        data = _rb(self.db_path)
        data.append(self.__dict__)
        _wb(data)

    def 



class Lock:
    is_room = None
    is_checkpoint = None

p = Profile('Husniddin', 'Karimzhonov')
p.save()
