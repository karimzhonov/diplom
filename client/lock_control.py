from time import time
import pickle

OPENED_DELAY = 5


class Control:
    def __init__(self, is_door_locked):
        self.is_door_locked = is_door_locked
        self.status = False

    def wait_close(self):
        """Waiting for close door"""
        print('[INFO] Waiting for close the door')
        while True:
            if not self.is_door_opened():
                self.close()
                break

    def control(self, status: bool):
        self.status = True
        if status:
            self.open()
        else:
            self.close()

    def close(self):
        if not self.is_door_locked:
            self.close_lock()
        self.status = False

    def open(self):
        self.open_lock()
        t0 = time()
        print('[INFO] Waiting for open the door')
        while time() - t0 < OPENED_DELAY:
            if self.is_door_opened():
                self.wait_close()
        self.close()

    def open_lock(self):
        """Function for opening the lock"""
        self.is_door_locked = False
        print('[INFO] Lock opened')

    def close_lock(self):
        """Function for closing the lock"""
        self.is_door_locked = True
        print('[INFO] Lock closed')

    @staticmethod
    def is_door_opened() -> bool:
        """if door opened, return True else False"""
        while True:
            try:
                with open('sensor.pickle', 'rb') as file:
                    status = pickle.load(file)
                    break
            except EOFError:
                continue
        return status


def sensor_simulator():
    while True:
        status = bool(int(input(' > ')))
        with open('sensor.pickle', 'wb') as file:
            pickle.dump(status, file)


if __name__ == '__main__':
    sensor_simulator()
