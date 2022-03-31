import numpy as np
import os


class Light(object):

    def __init__(self):
        # I_{a\lambda}
        self.I_a = None
        # I_{p\lambda}
        self.I_p = None
        # O_{s\lambda}
        self.O_s = None
        # L
        self.L = None
        # f_{att}
        self.f_att = None
        self.n = None
        self.is_ready = False

    def set(self, I_a, I_p, O_s, light_direction, f_att, n):
        # set
        if type(I_a) != list or len(I_a) != 3 \
                or type(I_a[0]) != int or type(I_a[0]) != float or I_a[0] < 0 or I_a[0] > 1 \
                or type(I_a[1]) != int or type(I_a[1]) != float or I_a[1] < 0 or I_a[1] > 1 \
                or type(I_a[2]) != int or type(I_a[2]) != float or I_a[2] < 0 or I_a[2] > 1:
            raise Exception('There is a type error in parameter `I_a`.')
        if type(I_p) != list or len(I_p) != 3 \
                or type(I_p[0]) != int or type(I_p[0]) != float or I_p[0] < 0 or I_p[0] > 1 \
                or type(I_p[1]) != int or type(I_p[1]) != float or I_p[1] < 0 or I_p[1] > 1 \
                or type(I_p[2]) != int or type(I_p[2]) != float or I_p[2] < 0 or I_p[2] > 1:
            raise Exception('There is a type error in parameter `I_p`.')
        if type(O_s) != list or len(O_s) != 3 \
                or type(O_s[0]) != int or type(O_s[0]) != float or O_s[0] < 0 or O_s[0] > 1 \
                or type(O_s[1]) != int or type(O_s[1]) != float or O_s[1] < 0 or O_s[1] > 1 \
                or type(O_s[2]) != int or type(O_s[2]) != float or O_s[2] < 0 or O_s[2] > 1:
            raise Exception('There is a type error in parameter `O_s`.')
        if type(light_direction) != list or len(light_direction) != 3 \
                or type(light_direction[0]) != int or type(light_direction[0]) != float \
                or type(light_direction[0]) != int or type(light_direction[1]) != float \
                or type(light_direction[0]) != int or type(light_direction[2]) != float:
            raise Exception('There is a type error in parameter `light_direction`.')
        if type(f_att) != int or type(f_att) != float or f_att < 0 or f_att > 1:
            raise Exception('Parameter `f_att` must be a number in [0,1].')
        if type(n) != int or type(n) != float:
            raise Exception('Parameter `n` must be a number.')
        self.I_a = np.ndarray(I_a)
        self.I_p = np.ndarray(I_p)
        self.O_s = np.ndarray(O_s)
        temp = -np.array(light_direction)
        self.L = temp / np.linalg.norm(temp, 2)
        self.f_att = float(f_att)
        self.n = float(n)
        self.is_ready = True

    def set_by_file(self, file_path):
        # read file
        with open(os.path.split(os.path.realpath(__file__))[0] + os.sep + file_path) as file:
            line_list = file.readlines()
        for line in line_list:
            line_split = line.split()
            if len(line_split) <= 0:
                continue
            elif line_split[0] == "I_{a\\lambda}":
                self.I_a = np.array([float(line_split[1]), float(line_split[2]), float(line_split[3])])
            elif line_split[0] == "I_{p\\lambda}":
                self.I_p = np.array([float(line_split[1]), float(line_split[2]), float(line_split[3])])
            elif line_split[0] == "O_{s\\lambda}":
                self.O_s = np.array([float(line_split[1]), float(line_split[2]), float(line_split[3])])
            elif line_split[0] == "light_direction":
                temp = -np.array([float(line_split[1]), float(line_split[2]), float(line_split[3])])
                self.L = temp / np.linalg.norm(temp, 2)
            elif line_split[0] == "f_{att}":
                self.f_att = float(line_split[1])
            elif line_split[0] == "n":
                self.n = float(line_split[1])
        self.is_ready = True
