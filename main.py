import copy
import datetime

from camera import Camera
from display import Display
from illumination import Illumination
from light import Light
from material import Material
from space import Space
from transform import *
from window import Window


def main():
    start = datetime.datetime.now()
    data_source_name = 'better-ball.d'
    #   0 - no shading (framework)
    #   1 - constant shading
    #   2 - Gouraud shading
    #   3 - Phong shading
    shading = 0

    world_space = Space()
    world_space.append_by_file(data_source_name + '.txt')  

    camera = Camera()
    camera.set_by_file(data_source_name + '.camera.txt')  

    light = Light()
    light.set_by_file(data_source_name + '.light.txt')  

    material = Material()
    material.set_by_file(data_source_name + '.material.txt')  
    illumination = Illumination()
    illumination.set(camera, light, material, shading)

    display = Display()
    display.set(800)
    
    view_space = copy.deepcopy(world_space)
    view_space.transform(world_to_view, camera)

    screen_space = copy.deepcopy(view_space)
    screen_space.transform(view_to_screen, camera)

    device_space = copy.deepcopy(screen_space)
    device_space.transform(screen_to_device, display)

    window = Window()
    window.set(world_space, device_space, illumination, display)

    window.show()


if __name__ == '__main__':
    main()
