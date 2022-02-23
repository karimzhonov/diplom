import pickle


def set_pickle(path, value):
    try:
        with open(path, 'wb') as file:
            pickle.dump(value, file)
    except EOFError:
        set_pickle(path, value)


def get_pickle(path):
    try:
        with open(path, 'rb') as file:
            return pickle.load(file)
    except EOFError:
        return get_pickle(path)