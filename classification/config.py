from tensorflow.keras.datasets import cifar10, cifar100


class Cifar10:
    name = 'cifar10'
    labels = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    load_data = cifar10.load_data


class Cifar100(Cifar10):
    name = 'cofar100'
    load_data = cifar100.load_data

