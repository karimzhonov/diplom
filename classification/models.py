import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Dense, Flatten
from tensorflow.keras.utils import to_categorical

from config import Cifar10


class Model:
    def __init__(self, dataset=Cifar10):
        self.model = Sequential([
            Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=(32, 32, 3)),
            MaxPooling2D((2, 2), strides=2),
            Conv2D(64, (3, 3), padding='same', activation='relu'),
            MaxPooling2D((2, 2), strides=2),
            Flatten(),
            Dense(128, activation='relu'),
            Dropout(0.3),
            Dense(10, activation='softmax')
        ])
        self.model_name = f'model_{dataset.name}'
        self.labels = dataset.labels
        self.load_dataset = dataset.load_data
        self.model.summary()

    @staticmethod
    def load_model(name: str = f'model_{Cifar10.name}'):
        model = Model()
        model.model = load_model(name)
        return model

    def train(self, batch_size=20, epochs=30):
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy'],)

        (x_train, y_train), _ = self.load_dataset()

        y_train = to_categorical(y_train)
        history = self.model.fit(x_train, y_train, batch_size, epochs, validation_split=0.2)

        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.show()

        self.model.save(self.model_name)

    def test(self):
        (x_train, _), (x_test, y_test) = self.load_dataset()
        for i, point in enumerate(x_train[0: 10]):
            plt.imsave(f'./assets/primer/{i}.png', point)
        predict = self.model.predict(x_test)

        false_answers_counter = 0
        for p, y in zip(predict, y_test):
            p = np.argmax(p)
            false_answers_counter += 1 if not p == y[0] else 0
        print(f'[INFO] False answers count: {false_answers_counter}/{len(x_test)}')

    def predict(self, img_path=None):
        if not img_path:
            _, (x_test, y_test) = self.load_dataset()
            n = np.random.randint(0, len(y_test) - 1)
            x = np.array([x_test[n]])
        else:
            img = plt.imread(img_path)
            x = np.array([np.reshape(img, (32, 32, 3))])

        predict = self.model.predict(x)
        predict = np.argmax(predict, axis=1)[0]
        answer = self.labels[int(predict)]
        print(f'Model answer: {answer}')
        plt.imshow(x[0])
        plt.show()



