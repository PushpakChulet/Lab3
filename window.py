from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from scipy.interpolate import *
import datetime
import numpy as np

from aet import AET
from display import Display
from illumination import Illumination
from space import Space
from transform import *


class Window(object):

    def __init__(self):
        # input
        self.__world_space = None
        self.__device_space = None
        self.__illumination = None
        self.__display = None
        # calculate
        self.__polygon_list_back_face = None
        self.__polygon_list_color = None
        self.__polygon_list_aet = None
        self.__vertex_list_back_face = None
        self.__vertex_list_color = None
        self.__z_buffer = None  # coordinate z of the pixel
        self.__p_buffer = None  # the polygon which the pixel belongs to
        self.__i_buffer = None  # the color (RGB) of the pixel
        # ready
        self.__is_ready = False

    def set(self, world_space, device_space, illumination, display):
        if not isinstance(world_space, Space):
            raise Exception('There is a type error in parameter `device_space`.')
        if not isinstance(device_space, Space):
            raise Exception('There is a type error in parameter `device_space`.')
        if not isinstance(illumination, Illumination) or not illumination.is_ready:
            raise Exception('Illumination is not ready.')
        if not isinstance(display, Display) or not display.is_ready:
            raise Exception('Display is not ready.')
        self.__world_space = world_space
        self.__device_space = device_space
        self.__illumination = illumination
        self.__display = display
        self.__calculate()

    def __calculate(self):
        # polygon
        print('Calculating: polygon ...')
        start = datetime.datetime.now()
        len_polygon = len(self.__device_space.polygon_list_vertex_list)
        self.__polygon_list_back_face = [False] * len_polygon
        self.__polygon_list_color = [None] * len_polygon
        self.__polygon_list_aet = [None] * len_polygon
        for i in range(1, len_polygon):
            # back-face culling
            if self.__device_space.polygon_list_normal_vector[i][2][0] >= 0:
                # ignore back-face polygon
                self.__polygon_list_back_face[i] = True
                continue
            if self.__illumination.shading != 0:
                if self.__illumination.shading == 1:
                    # generate color (RGB) => for constant shading
                    self.__polygon_list_color[i] = self.__illumination.calculate(
                        mr4c1_to_v3(self.__world_space.polygon_list_normal_vector[i])
                    )
                # generate active edge table (AET)
                self.__polygon_list_aet[i] = AET()
                self.__polygon_list_aet[i].set(
                    self.__device_space.vertex_list_coordinate,
                    self.__device_space.polygon_list_vertex_list[i],
                    self.__device_space.polygon_list_edge_list_vertex_index[i]
                )
        cost = datetime.datetime.now() - start
        print('Finish. (cost = ' + str(cost) + ')\n')
        if self.__illumination.shading == 2:
            # vertex
            print('Calculating: vertex ...')
            start = datetime.datetime.now()
            len_vertex = len(self.__device_space.vertex_list_coordinate)
            self.__vertex_list_back_face = [True] * len_vertex
            self.__vertex_list_color = [None] * len_vertex
            for i in range(1, len_vertex):
                # back-face culling
                #
                # consider a vertex "back-faced" if ALL polygons which the vertex belongs to are back-face
                for j in range(0, len(self.__device_space.vertex_list_polygon_list[i])):
                    if self.__polygon_list_back_face[self.__device_space.vertex_list_polygon_list[i][j]] == False:
                        self.__vertex_list_back_face[i] = False
                        break
            for i in range(1, len_vertex):
                if self.__vertex_list_back_face[i]:
                    # ignore back-face vertex
                    continue
                # generate color (RGB) => for Gouraud shading
                self.__vertex_list_color[i] = self.__illumination.calculate(
                    mr4c1_to_v3(self.__world_space.vertex_list_normal_vector[i])
                )
            cost = datetime.datetime.now() - start
            print('Finish. (cost = ' + str(cost) + ')\n')
        if self.__illumination.shading != 0:
            # pixel
            print('Calculating: pixel ...')
            start = datetime.datetime.now()
            self.__z_buffer = []
            self.__p_buffer = []
            self.__i_buffer = []
            for i in range(0, self.__display.pixel_number + 1):
                self.__z_buffer.append([])
                self.__p_buffer.append([])
                self.__i_buffer.append([])
                for j in range(0, self.__display.pixel_number + 1):
                    self.__z_buffer[-1].append(float('Inf'))
                    self.__p_buffer[-1].append(0)
                    self.__i_buffer[-1].append([0, 0, 0])
            # iterate each polygon
            for i in range(1, len(self.__polygon_list_aet)):
                if self.__polygon_list_back_face[i]:
                    # ignore back-face polygon
                    continue
                # set parameter of interpolator
                source_x = []
                source_y = []
                object_z = []
                object_color_r = []
                object_color_g = []
                object_color_b = []
                object_normal_x = []
                object_normal_y = []
                object_normal_z = []
                for j in range(0, len(self.__device_space.polygon_list_vertex_list[i])):
                    coordinate_mr4c1 = self.__device_space.vertex_list_coordinate[
                        self.__device_space.polygon_list_vertex_list[i][j]
                    ]
                    source_x.append(coordinate_mr4c1[0][0])
                    source_y.append(coordinate_mr4c1[1][0])
                    object_z.append(coordinate_mr4c1[2][0])
                    if self.__illumination.shading == 2:
                        color_v3 = self.__vertex_list_color[
                            self.__device_space.polygon_list_vertex_list[i][j]
                        ]
                        object_color_r.append(color_v3[0])
                        object_color_g.append(color_v3[1])
                        object_color_b.append(color_v3[2])
                    elif self.__illumination.shading == 3:
                        normal_mr4c1 = self.__world_space.vertex_list_normal_vector[
                            self.__device_space.polygon_list_vertex_list[i][j]
                        ]
                        object_normal_x.append(normal_mr4c1[0][0])
                        object_normal_y.append(normal_mr4c1[1][0])
                        object_normal_z.append(normal_mr4c1[2][0])
                # Each list should contain at least 4 elements, or function `interp2d` will throw error.
                if len(source_x) < 4:
                    source_x.append(source_x[-1])
                    source_y.append(source_y[-1])
                    object_z.append(object_z[-1])
                    if self.__illumination.shading == 2:
                        object_color_r.append(object_color_g[-1])
                        object_color_g.append(object_color_g[-1])
                        object_color_b.append(object_color_b[-1])
                    elif self.__illumination.shading == 3:
                        object_normal_x.append(object_normal_x[-1])
                        object_normal_y.append(object_normal_y[-1])
                        object_normal_z.append(object_normal_z[-1])
                # generate interpolator
                try:
                    get_z = interp2d(source_x, source_y, object_z)
                    get_color_r = None
                    get_color_g = None
                    get_color_b = None
                    get_normal_x = None
                    get_normal_y = None
                    get_normal_z = None
                    if self.__illumination.shading == 2:
                        get_color_r = interp2d(source_x, source_y, object_color_r)
                        get_color_g = interp2d(source_x, source_y, object_color_g)
                        get_color_b = interp2d(source_x, source_y, object_color_b)
                    elif self.__illumination.shading == 3:
                        get_normal_x = interp2d(source_x, source_y, object_normal_x)
                        get_normal_y = interp2d(source_x, source_y, object_normal_y)
                        get_normal_z = interp2d(source_x, source_y, object_normal_z)
                except:
                    get_z = None
                # iterate each scan line
                for j in range(0, len(self.__polygon_list_aet[i].active_edge_table)):
                    if self.__polygon_list_aet[i].active_edge_table[j] is not None:
                        scan_line = self.__polygon_list_aet[i].active_edge_table[j]
                        len_scan_line = len(scan_line)
                        if len_scan_line % 2 != 0:
                            # ignore the wrong situation (each scan line should contain even edges)
                            len_scan_line -= 1
                        for k in range(0, len_scan_line, 2):
                            for l in range(int(scan_line[k].bottom_vertex_x), int(scan_line[k + 1].bottom_vertex_x)):
                                x = l
                                y = j + self.__polygon_list_aet[i].offset_y
                                if 0 <= x <= self.__display.pixel_number and 0 <= y <= self.__display.pixel_number:
                                    if get_z is not None:
                                        z = get_z(x, y)[0]
                                    else:
                                        z = float('Inf')
                                    if z < self.__z_buffer[x][y]:
                                        self.__z_buffer[x][y] = z
                                        self.__p_buffer[x][y] = i
                                        #
                                        if self.__illumination.shading == 1:
                                            # constant shading
                                            self.__i_buffer[x][y] = self.__polygon_list_color[i]
                                        elif self.__illumination.shading == 2:
                                            # Gouraud shading
                                            self.__i_buffer[x][y] = [
                                                get_color_r(x, y)[0], get_color_g(x, y)[0], get_color_b(x, y)[0]
                                            ]
                                        elif self.__illumination.shading == 3:
                                            # Phone shading
                                            self.__i_buffer[x][y] = self.__illumination.calculate([
                                                get_normal_x(x, y)[0], get_normal_y(x, y)[0], get_normal_z(x, y)[0]
                                            ])
            cost = datetime.datetime.now() - start
            print('Finish. (cost = ' + str(cost) + ')\n')
        # ready
        self.is_ready = True

    def __draw(self):
        print('Rendering ...')
        start = datetime.datetime.now()
        glClear(GL_COLOR_BUFFER_BIT)
        if self.__illumination.shading == 0:
            # no shading (framework)
            for i in range(1, len(self.__device_space.polygon_list_vertex_list)):
                if not self.__polygon_list_back_face[i]:
                    # draw line
                    glBegin(GL_LINE_LOOP)
                    for vertex_index in self.__device_space.polygon_list_vertex_list[i]:
                        # draw point
                        glVertex2f(
                            self.__device_space.vertex_list_coordinate[vertex_index][0][0],
                            self.__device_space.vertex_list_coordinate[vertex_index][1][0]
                        )
                    glEnd()
        else:
            # constant shading / Gouraud shading / Phone shading
            glBegin(GL_POINTS)
            for i in range(0, self.__display.pixel_number + 1):
                for j in range(0, self.__display.pixel_number + 1):
                    if self.__p_buffer[i][j] == 0:
                        # accelerate: ignore "non-polygon" pixels
                        continue
                    glColor3fv(self.__i_buffer[i][j])
                    glVertex2i(i, j)
            glEnd()
        glFlush()
        render_cost = datetime.datetime.now() - start
        print('Finish. (cost = ' + str(render_cost) + ')\n')

    def show(self):
        if not self.is_ready:
            raise Exception('Window is not ready.')
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
        glutInitWindowSize(self.__display.pixel_number, self.__display.pixel_number)
        glutCreateWindow("")
        gluOrtho2D(0, self.__display.pixel_number, 0, self.__display.pixel_number)
        glutDisplayFunc(self.__draw)
        glutMainLoop()
