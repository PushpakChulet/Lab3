import numpy as np

from camera import Camera
from light import Light
from material import Material


class Illumination(object):

    def __init__(self):
        # shading: 0 - no, 1 - constant, 2 - Gouraud, 3 - Phong
        self.shading = None
        # I_{a\lambda}
        self.I_a = None
        # k_{a}
        self.k_a = None
        # O{d\lambda}
        self.O_d = None
        # f_{att}
        self.f_att = None
        # I_{p\lambda}
        self.I_p = None
        # k_{d}
        self.k_d = None
        # L
        self.L = None
        # k_{s}
        self.k_s = None
        # O_{s\lambda}
        self.O_s = None
        # V
        self.V = None
        # n
        self.n = None
        # pre-computation
        self.__H = None
        self.__part_1 = None
        self.__part_2 = None
        self.__part_3 = None
        self.__part_4 = None
        # ready
        self.is_ready = False

    def set(self, camera, light, material, shading):
        if not isinstance(camera, Camera) or not camera.is_ready:
            raise Exception('Camera is not ready.')
        if not isinstance(light, Light) or not light.is_ready:
            raise Exception('Light is not ready.')
        if not isinstance(material, Material) or not material.is_ready:
            raise Exception('Material is not ready.')
        if type(shading) != int:
            raise Exception('Parameter `shading` must be a integer.')
        if shading == 1 or shading == 2 or shading == 3:
            self.shading = shading
        else:
            self.shading = 0
        self.I_a = light.I_a
        self.k_a = material.k_a
        self.O_d = material.O_d
        self.f_att = light.f_att
        self.I_p = light.I_p
        self.k_d = material.k_d
        self.L = light.L
        self.k_s = material.k_s
        self.O_s = light.O_s
        # `V` should point to camera.
        self.V = -camera.N
        self.n = light.n
        self.__H = self.L + self.V
        self.__H = self.__H / np.linalg.norm(self.__H, 2)
        self.__part_1 = self.I_a * self.k_a * self.O_d
        self.__part_2 = self.f_att * self.I_p
        self.__part_3 = self.k_d * self.O_d
        self.__part_4 = self.k_s * self.O_s
        self.is_ready = True

    # N should be:
    #
    # | name  | shape             | type                                     |
    # | ----- | ----------------- | ---------------------------------------- |
    # | v3    | [x,y,z]           | numpy.ndarray - vector (3)               |
    def calculate(self, N):
        if not self.is_ready:
            raise Exception('Illumination is not ready.')
        # normalize
        N = N / np.linalg.norm(N, 2)
        # halfway vector
        return self.__part_1 + self.__part_2 * (
                self.__part_3 * np.dot(N, self.L) + self.__part_4 * (np.dot(N, self.__H) ** self.n)
        )
