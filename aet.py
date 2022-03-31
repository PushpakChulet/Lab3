import copy


class AET(object):
    def __init__(self):
        self.__space_vertex_list_coordinate = None
        self.__edge_list_vertex_index = None
        self.__vertex_list_sorted_y = None
        self.offset_y = 0
        self.__new_edge_table = None
        self.active_edge_table = None

    def set(self, space_vertex_list_coordinate, polygon_vertex_index, polygon_edge_list_vertex_index):
        self.__space_vertex_list_coordinate = [[]]
        for i in range(1, len(space_vertex_list_coordinate)):
            self.__space_vertex_list_coordinate.append([
                [int(space_vertex_list_coordinate[i][0][0])],
                [int(space_vertex_list_coordinate[i][1][0])],
                [float(space_vertex_list_coordinate[i][2][0])],
                [float(space_vertex_list_coordinate[i][3][0])]
            ])
        self.__edge_list_vertex_index = polygon_edge_list_vertex_index
        temp = []
        for i in range(0, len(polygon_vertex_index)):
            temp.append([self.__space_vertex_list_coordinate[polygon_vertex_index[i]][1][0], polygon_vertex_index[i]])
        self.__vertex_list_sorted_y = sorted(temp)  # item: [y coordinate, index]
        self.offset_y = self.__vertex_list_sorted_y[0][0]
        self.__new_edge_table = [None] * (self.__vertex_list_sorted_y[-1][0] - self.offset_y + 1)
        self.active_edge_table = [None] * (self.__vertex_list_sorted_y[-1][0] - self.offset_y + 1)
        self.__calculate()

    def __calculate(self):
        # NET (new edge table)
        edge_list = copy.deepcopy(self.__edge_list_vertex_index)
        # iterate each vertex which has been sorted A-Z by coordinate y
        for i in range(0, len(self.__vertex_list_sorted_y)):
            # iterate each edge
            j = 0
            while j < len(edge_list):
                if self.__vertex_list_sorted_y[i][1] == edge_list[j][0] \
                        or self.__vertex_list_sorted_y[i][1] == edge_list[j][1]:
                    # get coordinate of endpoints of each edge
                    if self.__vertex_list_sorted_y[i][1] == edge_list[j][0]:
                        vertex_bottom = self.__space_vertex_list_coordinate[edge_list[j][0]]
                        vertex_top = self.__space_vertex_list_coordinate[edge_list[j][1]]
                    else:
                        vertex_bottom = self.__space_vertex_list_coordinate[edge_list[j][1]]
                        vertex_top = self.__space_vertex_list_coordinate[edge_list[j][0]]
                    if vertex_bottom[1][0] != vertex_top[1][0]:
                        # record edge which is not parallel to x-axis
                        index = self.__vertex_list_sorted_y[i][0] - self.offset_y
                        if self.__new_edge_table[index] is None:
                            self.__new_edge_table[index] = []
                        self.__new_edge_table[index].append(
                            Edge(
                                vertex_top[1][0],
                                vertex_bottom[0][0],
                                (vertex_top[0][0] - vertex_bottom[0][0]) / (vertex_top[1][0] - vertex_bottom[1][0])
                            )
                        )
                    # remove solved edge and modify counter
                    edge_list.pop(j)
                    j -= 1
                j += 1
        # AET (active edge table)
        #
        # iterate each edge in NET
        for i in range(0, len(self.__new_edge_table)):
            if self.__new_edge_table[i] is not None:
                for j in range(0, len(self.__new_edge_table[i])):
                    e = self.__new_edge_table[i][j]
                    for k in range(i, e.top_vertex_y - self.offset_y):
                        # copy edge and modify coordinate x
                        e_prime = copy.deepcopy(e)
                        e_prime.bottom_vertex_x = float(e.bottom_vertex_x + (k - i) * e.dx_dy)
                        # add to AET
                        if self.active_edge_table[k] is None:
                            self.active_edge_table[k] = [e_prime]
                        else:
                            self.active_edge_table[k].append(e_prime)
                            self.active_edge_table[k].sort(key=lambda edge: edge.bottom_vertex_x)


class Edge(object):
    def __init__(self, top_vertex_y, bottom_vertex_x, dx_dy):
        self.top_vertex_y = top_vertex_y
        self.bottom_vertex_x = bottom_vertex_x
        self.dx_dy = dx_dy
