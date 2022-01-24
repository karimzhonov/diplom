import pickle


def _wb(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)


def _rb(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file, encoding='bytes')
