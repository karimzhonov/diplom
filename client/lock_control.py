from utils import get_pickle, set_pickle


class LockControl:
    def __init__(self) -> None:
        from config import SENSOR_PATH, ANSWER_PATH
        self.spath = SENSOR_PATH
        self.apath = ANSWER_PATH

    def get_sensor_status(self):
        return get_pickle(self.spath)

    def get_lock_status(self):
        return get_pickle(self.apath)

    def set_sensor_status(self, status):
        set_pickle(self.spath, status)
    
    def set_lock_status(self, status):
        set_pickle(self.apath, status)

