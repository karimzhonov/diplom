import pickle
import os
from config import DB_DIR, BASE_DIR


def _wb(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

def _rb(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)


def get_dataset_path(self):
    label = self.__class__.__name__.lower()
    path = os.path.join(BASE_DIR, 'dataset', f'{label}')
    _wb([] ,path)


def get_or_set_dataset(callback):
    with open(DB_PICKLE, 'wb+') as file:
        return callback(file)


def get_value(data, key):
    try:
        return data[key]
    except KeyError:
        data[key] = []
        return data[key]


def get_pk(self):
    label = f'{self.__class__.__name__.lower()}.pickle'
    dataset = _rb(os.path.join(DB_DIR, label))
    if not dataset:
        return 0
    else:
        return dataset[-1].pk + 1

class Model:
    def save(self):
        pass
