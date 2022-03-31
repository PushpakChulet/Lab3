import numpy as np


class Lay(object):
    def __init__(self):
        self.__m = self.m_world = None
        self.__r = self.m_world = None
        self.__s = self.m_world = None
        self.m_world = None
        self.m_world_inv = None
        self.is_ready = False

    def set(self, move=np.eye(4), rotate=np.eye(4), scale=np.eye(4)):
        if type(move) != np.ndarray or move.shape != (4, 4):
            raise Exception('Parameter `move` must be 4x4 numpy.ndarray')
        if type(rotate) != np.ndarray or rotate.shape != (4, 4):
            raise Exception('Parameter `rotate` must be 4x4 numpy.ndarray.')
        if type(scale) != np.ndarray or scale.shape != (4, 4):
            raise Exception('Parameter `scale` must or 4x4 numpy.ndarray')
        self.__m = move
        self.__r = rotate
        self.__s = scale
        self.__calculate()

    def __calculate(self):
        self.m_world = np.dot(np.dot(self.__m, self.__r), self.__s)
        self.m_world_inv = np.linalg.inv(self.m_world)
        self.is_ready = True
