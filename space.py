from inspect import isfunction
import numpy as np
import os

from camera import Camera
from display import Display
from lay import Lay
from transform import *


class Space(object):

    def __init__(self):
        self.vertex_number = 0
        self.vertex_list_coordinate = [np.array([])]
        self.vertex_list_normal_vector = [np.array([])]
        self.vertex_list_polygon_list = [[]]
        self.polygon_number = 0
        self.polygon_list_vertex_list = [[]]
        self.polygon_list_normal_vector = [np.array([])]
        self.polygon_list_edge_list_vertex_index = [[[]]]

    def append_by_file(self, file_path):
        vertex_index_offset = self.vertex_number
        # read file
        with open(os.path.split(os.path.realpath(__file__))[0] + os.sep + file_path) as file:
            line_list = file.readlines()
        # get number of vertex and polygon
        line = line_list[0].split()
        self.vertex_number = int(line[1])
        self.polygon_number = int(line[2])
        vertex_total_number = self.vertex_number + vertex_index_offset
        # vertex
        for i in range(1, 1 + self.vertex_number):
            try:
                line = line_list[i].split()
                # append `vertex_list_coordinate`
                self.vertex_list_coordinate.append(np.array([float(line[0]), float(line[1]), float(line[2])]))
                # append `vertex_list_polygon_list`
                self.vertex_list_polygon_list.append([])
            except Exception as e:
                print('An error occurs at line ' + str(i + 1) + ' in file "' + file_path + '".')
                raise e
        # polygon
        for i in range(1 + self.vertex_number, 1 + self.vertex_number + self.polygon_number):
            try:
                line = line_list[i].split()
                # append `polygon_list_vertex_list`
                polygon_vertex_index = []
                for j in range(1, len(line)):
                    vertex_index = int(line[j]) + vertex_index_offset
                    if vertex_index <= vertex_index_offset or vertex_index > vertex_total_number:
                        raise Exception('The index of vertex is out of range.')
                    polygon_vertex_index.append(vertex_index)
                    # set corresponding item in `vertex_list_polygon_list`
                    self.vertex_list_polygon_list[vertex_index].append(len(self.polygon_list_vertex_list))
                self.polygon_list_vertex_list.append(polygon_vertex_index)
                # append `polygon_list_edge_list_vertex_index`
                polygon_edge_list_vertex_index = []
                for j in range(0, len(polygon_vertex_index)):
                    polygon_edge_list_vertex_index.append([polygon_vertex_index[j - 1], polygon_vertex_index[j]])
                self.polygon_list_edge_list_vertex_index.append(polygon_edge_list_vertex_index)
                # append `polygon_list_normal_vector`
                if len(polygon_vertex_index) < 3:
                    raise Exception('A polygon must contain at least 3 vertices.')
                #
                # Data description (of ".d" file) says:
                #
                # "polygons given by: number of points in the polygon followed by vertex number in clockwise order
                # (when looking from outside the object)"
                #
                # It means that:
                #
                # If using (p0->p1) x (p1->p2) to calculate the normal vector N of the polygon,
                # N will points to the INSIDE of the geometry.
                #
                # However, N should point to the OUTSIDE in this graphic system.
                # As a result, using (p1->p2) x (p0->p1) to calculate the normal vector N.
                #
                p0p1 = self.vertex_list_coordinate[self.polygon_list_vertex_list[-1][1]] \
                       - self.vertex_list_coordinate[self.polygon_list_vertex_list[-1][0]]
                p1p2 = self.vertex_list_coordinate[self.polygon_list_vertex_list[-1][2]] \
                       - self.vertex_list_coordinate[self.polygon_list_vertex_list[-1][1]]
                self.polygon_list_normal_vector.append(np.cross(p1p2, p0p1))
            except Exception as e:
                print('An error occurs at line ' + str(i + 1) + ' in file "' + file_path + '".')
                raise e
        # vertex: normal vector
        for i in range(1, len(self.vertex_list_polygon_list)):
            vertex_normal_vector = np.array([0.0, 0.0, 0.0])
            for j in range(0, len(self.vertex_list_polygon_list[i])):
                vertex_normal_vector += self.polygon_list_normal_vector[self.vertex_list_polygon_list[i][j]]
            self.vertex_list_normal_vector.append(vertex_normal_vector)
        # convert all coordinates and vectors from 'v3' to 'mr4c1'
        for i in range(1, len(self.vertex_list_coordinate)):
            self.vertex_list_coordinate[i] = v3_to_mr4c1(self.vertex_list_coordinate[i])
            self.vertex_list_normal_vector[i] = v3_to_mr4c1(self.vertex_list_normal_vector[i], True)
        for i in range(1, len(self.polygon_list_normal_vector)):
            self.polygon_list_normal_vector[i] = v3_to_mr4c1(self.polygon_list_normal_vector[i], True)

    def append_by_space(self, space):
        if not isinstance(space, Space):
            raise Exception('There is a type error in parameter `space`.')
        # append `vertex_list_coordinate`
        self.vertex_list_coordinate += space.vertex_list_coordinate[1:]
        # append `vertex_list_normal_vector`
        self.vertex_list_normal_vector += space.vertex_list_normal_vector[1:]
        # append `vertex_list_polygon_list`
        for i in range(1, len(space.vertex_list_polygon_list)):
            vector_polygon_list = []
            for j in range(0, len(space.vertex_list_polygon_list[i])):
                vector_polygon_list.append(space.vertex_list_polygon_list[i][j] + self.polygon_number)
            self.vertex_list_polygon_list.append(vector_polygon_list)
        # append `polygon_list_normal_vector`
        self.polygon_list_normal_vector += space.polygon_list_normal_vector[1:]
        # append `polygon_list_vertex_list`
        for i in range(1, len(space.polygon_list_vertex_list)):
            vector_polygon_list = []
            for j in range(0, len(space.polygon_list_vertex_list[i])):
                vector_polygon_list.append(space.polygon_list_vertex_list[i][j] + self.vertex_number)
            self.polygon_list_vertex_list.append(vector_polygon_list)
        # append `polygon_list_edge_list_vertex_index`
        for i in range(1, len(space.polygon_list_edge_list_vertex_index)):
            polygon_edge_list_vertex_index = []
            for j in range(0, len(space.polygon_list_edge_list_vertex_index[i])):
                edge = []
                for k in range(0, len(space.polygon_list_edge_list_vertex_index[i][j])):
                    vertex_index = space.polygon_list_edge_list_vertex_index[i][j][k] + self.vertex_number
                    edge.append(vertex_index)
                polygon_edge_list_vertex_index.append(edge)
            self.polygon_list_edge_list_vertex_index.append(polygon_edge_list_vertex_index)
        # update `self.vertex_number` and `polygon_number`
        self.vertex_number = len(self.vertex_list_coordinate) - 1
        self.polygon_number = len(self.polygon_list_normal_vector) - 1

    def transform(self, trans_func, trans_func_2nd_param):
        if not isfunction(trans_func):
            raise Exception('Parameter `trans_func` must be a function.')
        if not (isinstance(trans_func_2nd_param, Lay)
                or isinstance(trans_func_2nd_param, Camera)
                or isinstance(trans_func_2nd_param, Display)):
            raise Exception('There is a type error in parameter `trans_func_2nd_param`.')
        for i in range(1, len(self.vertex_list_coordinate)):
            self.vertex_list_coordinate[i] = \
                trans_func(self.vertex_list_coordinate[i], trans_func_2nd_param)
            self.vertex_list_normal_vector[i] = \
                trans_func(self.vertex_list_normal_vector[i], trans_func_2nd_param, True)
        for i in range(1, len(self.polygon_list_normal_vector)):
            self.polygon_list_normal_vector[i] = \
                trans_func(self.polygon_list_normal_vector[i], trans_func_2nd_param, True)
