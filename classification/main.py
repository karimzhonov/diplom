import sys
from models import Model

if __name__ == '__main__':
    _flag = sys.argv[1]
    if _flag == 'train':
        model = Model()
        model.train()
    elif _flag == 'test':
        model = Model.load_model()
        model.test()
    elif _flag == 'predict':
        model = Model.load_model()
        model.predict()
    else:
        text = """
        python main.py train: Command for training model.
        python main.py test: Command for testing model.
        python main.py predict: Command for prediction random img.
        """
        print(text)


