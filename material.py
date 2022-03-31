import numpy as np
import os


class Material(object):

    def __init__(self):
        # O{d\lambda }
        self.O_d = None
        # k_{a}
        self.k_a = None
        # k_{d}
        self.k_d = None
        # k_{s}
        self.k_s = None
        # ready
        self.is_ready = False

    def set(self, O_d, k_a, k_d, k_s):
        # set
        if type(O_d) != list or len(O_d) != 3 \
                or type(O_d[0]) != int or type(O_d[0]) != float or O_d[0] < 0 or O_d[0] > 1 \
                or type(O_d[1]) != int or type(O_d[1]) != float or O_d[1] < 0 or O_d[1] > 1 \
                or type(O_d[2]) != int or type(O_d[2]) != float or O_d[2] < 0 or O_d[2] > 1:
            raise Exception('There is a type error in parameter `O_d`.')
        if type(k_a) != int or type(k_a) != float or k_a < 0 or k_a > 1:
            raise Exception('Parameter `k_a` must be a number in [0,1].')
        if type(k_d) != int or type(k_d) != float or k_d < 0 or k_d > 1:
            raise Exception('Parameter `k_d` must be a number in [0,1].')
        if type(k_s) != int or type(k_s) != float or k_s < 0 or k_s > 1:
            raise Exception('Parameter `k_s` must be a number in [0,1].')
        self.O_d = np.array(O_d)
        self.k_a = k_a
        self.k_d = k_d
        self.k_s = k_s
        self.is_ready = True

    def set_by_file(self, file_path):
        # read file
        with open(os.path.split(os.path.realpath(__file__))[0] + os.sep + file_path) as file:
            line_list = file.readlines()
        for line in line_list:
            line_split = line.split()
            if len(line_split) <= 0:
                continue
            if line_split[0] == "O_{d\\lambda}":
                self.O_d = np.array([float(line_split[1]), float(line_split[2]), float(line_split[3])])
            elif line_split[0] == "k_{a}":
                self.k_a = float(line_split[1])
            elif line_split[0] == "k_{d}":
                self.k_d = float(line_split[1])
            elif line_split[0] == "k_{s}":
                self.k_s = float(line_split[1])
        self.is_ready = True
