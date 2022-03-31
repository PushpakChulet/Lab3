import numpy as np

from camera import Camera
from display import Display
from lay import Lay


# coordinate/vector conversion
#
# | name  | shape             | type                                     |
# | ----- | ----------------- | ---------------------------------------- |
# | v3    | [x,y,z]           | numpy.ndarray - vector (3)               |
# | mr4c1 | [[x],[y],[z],[w]] | numpy.ndarray - matrix (row 4, column 1) |


def v3_to_mr4c1(v3, normal_vector=False):
    if normal_vector:
        return np.array([np.append(v3, 0)]).T
    else:
        return np.array([np.append(v3, 1)]).T


def mr4c1_to_v3(mr4c1):
    return mr4c1.T[0][:3].copy()


# space transform

# 3D Local Space <===> 3D World Space

def local_to_world(mr4c1, lay, normal_vector=False):
    if not isinstance(lay, Lay) or not lay.is_ready:
        raise Exception('Lay is not ready.')
    if normal_vector:
        # NOTE: the transform of normal vector is DIFFERENT from which of vertex!
        #
        # vertex = M · vertex0 ==> normal = (M ^ -1) ^ T · normal0
        #
        # (the same below)
        return np.dot(lay.m_world_inv.T, mr4c1)
    else:
        return np.dot(lay.m_world, mr4c1)


def world_to_local(mr4c1, lay, normal_vector=False):
    if not isinstance(lay, Lay) or not lay.is_ready:
        raise Exception('Lay is not ready.')
    if normal_vector:
        return np.dot(lay.m_world.T, mr4c1)
    else:
        return np.dot(lay.m_world_inv, mr4c1)


# 3D World Space <===> 3D View/Camera/Eye Space

def world_to_view(mr4c1, camera, normal_vector=False):
    if not isinstance(camera, Camera) or not camera.is_ready:
        raise Exception('Camera is not ready.')
    if normal_vector:
        return np.dot(camera.m_view_inv.T, mr4c1)
    else:
        return np.dot(camera.m_view, mr4c1)


def view_to_world(mr4c1, camera, normal_vector=False):
    if not isinstance(camera, Camera) or not camera.is_ready:
        raise Exception('Camera is not ready.')
    if normal_vector:
        return np.dot(camera.m_view.T, mr4c1)
    else:
        return np.dot(camera.m_view_inv, mr4c1)


# 3D View/Camera/Eye Space <===> 3D Screen Space

def view_to_screen(mr4c1, camera, normal_vector=False):
    if not isinstance(camera, Camera) or not camera.is_ready:
        raise Exception('Camera is not ready.')
    if normal_vector:
        return np.dot(camera.m_pers_inv.T, mr4c1)
    else:
        temp_1 = np.dot(camera.m_pers, mr4c1)
        w = temp_1[3][0]
        temp_2 = temp_1 / w
        temp_2[3][0] = w
        return temp_2


def screen_to_view(mr4c1, camera, normal_vector=False):
    if not isinstance(camera, Camera) or not camera.is_ready:
        raise Exception('Camera is not ready.')
    if normal_vector:
        return np.dot(camera.m_pers.T, mr4c1)
    else:
        w = mr4c1[3][0]
        temp = mr4c1 * w
        temp[3][0] = w
        return np.dot(camera.m_pers_inv, temp)


# 3D Screen Space <===> 2D Device Space

def screen_to_device(mr4c1, display, normal_vector=False):
    if not isinstance(display, Display) or not display.is_ready:
        raise Exception('Display is not ready.')
    if normal_vector:
        return mr4c1
    else:
        w = mr4c1[3][0]
        half_pixel_number = display.pixel_number // 2
        temp = half_pixel_number * mr4c1 + half_pixel_number
        temp[3][0] = w
        return temp


def device_to_screen(mr4c1, display, normal_vector=False):
    if not isinstance(display, Display) or not display.is_ready:
        raise Exception('Display is not ready.')
    if normal_vector:
        return mr4c1
    else:
        w = mr4c1[3][0]
        half_pixel_number = display.pixel_number // 2
        temp = (mr4c1 - half_pixel_number) / half_pixel_number
        temp[3][0] = w
        return temp
