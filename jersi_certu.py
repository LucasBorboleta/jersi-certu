#!/usr/bin/en python3

"""Jersi-certu is a Python3 program for playing the jersi abstract game."""

# -*- coding: utf-8 -*-

import copy
import os
import re
import random
import string


_COPYRIGHT_AND_LICENSE = """
JERSI-CERTU (the program) implements JERSI (the rules), an abstract board game.

Copyright (C) 2019 Lucas Borboleta (lucas.borboleta@free.fr).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""

class JersiError(Exception):
    """Customized exception dedicated to all classes of JERSI"""

    def __init__(self, message):
        """JERSI exception records an explaining text message"""
        Exception.__init__(self)
        self.message = message


def jersi_assert(condition, message):
    """If condition fails (is False) then raise a JERSI exception
    together with the explaining message"""
    if not condition:
        raise JersiError(message)


class Hexagon:

    """
       The Hexagon class captures geometrical knowledge and printing capacity
       about an hexagon meshed with a grid of regular triangles.

       Nodes of the hexagon are described using points that are located
       using an oblique and centered coordinates system :
           - C is the hexagon center;
           - e_u is horizontal unit vector pointing right ;
           - e_v is diagonal unit vector pointing up ;
           - A node P is represented as CP = u*e_u + v*e_v ;

       A frame made of cells is used for printing textual rows and columns :
           - O is at the left upper corner ;
           - e_x is horizontal vector pointing right ;
           - e_y is vectical vector pointing down ;
           - A cell P is represented as OP = x*e_x + y*e_y ;

      The relationship bewteen the the (u, v) and (x, y) coordinates systems
      are as follows :
          - e_u  = 2*e_x
          - e_v = e_x - e_y
          - OC = n*e_y + n*e_u

      Example of a frame for an instance Hexagon(5) with a few cells
      filled up with one or two letters:

        i1          .k  cr  .n  kr  .c          i5
        h1        .c  .r  .k  .c  .r  .k        h6
        g1      ..  ..  ..  ..  ..  ..  ..      g7
        f1    ..  ..  ..  ..  ..  ..  ..  ..    f8
        e1  ..  ..  ..  ..  ..  ..  ..  ..  ..  e9
        d1    ..  ..  ..  ..  ..  ..  ..  ..    d8
        c1      ..  ..  ..  ..  ..  ..  ..      c7
        b1        .K  .R  .C  .K  .R  .C        b6
        a1          .C  KR  .N  CR  .K          a5

   """


    __SPACE = " "
    __FILLER = "."

    def __init__(self, nodes_per_hexagon_side):
        """Initialize an hexagon parametrized by
        the number of nodes per hexagon side"""

        self.__nodes_per_hexagon_side = nodes_per_hexagon_side
        self.__n = self.__nodes_per_hexagon_side - 1

        # Many information are computed once and memorized in attributes
        # in order to accelerate next "get...." queries.
        self.__init_point_directions()
        self.__init_point_coordinates()
        self.__init_point_in_hexagon()
        self.__init_frame()
        self.__init_row_labels()
        self.__init_count_labels()
        self.__init_left_labels()
        self.__init_right_labels()
        self.__init_labels_to_points()
        self.__init_labels_from_points()


    def __init_point_directions(self):
        """Initialize all possible traveling directions from a point."""

        self.__point_directions = list()
        self.__point_directions.append((1, 0)) # e_u
        self.__point_directions.append((0, 1)) # e_v
        self.__point_directions.append((-1, 1)) # e_v - e_u
        self.__point_directions.append((-1, 0)) # -e_u
        self.__point_directions.append((0, -1)) # -e_v
        self.__point_directions.append((1, -1)) # e_u - e_v


    def __init_point_coordinates(self):
        """Initialize the possile point coordinates."""

        (u_min, u_max) = (-self.__n, self.__n)
        (v_min, v_max) = (-self.__n, self.__n)
        self.__u_list = list(range(u_min, u_max + 1))
        self.__v_list = list(range(v_min, v_max + 1))


    def __init_point_in_hexagon(self):
        """Initialize the results of the predicate "has_node_at_point". """

        self.__point_in_hexagon = dict()

        for point_u in self.__u_list:
            for point_v in self.__v_list:
                point = (point_u, point_v)

                ne_rule = (self.__n - point_u - point_v >= 0)
                se_rule = (self.__n - point_u >= 0)
                nw_rule = (self.__n + point_u >= 0)
                sw_rule = (self.__n + point_u + point_v >= 0)

                point_is_inside = nw_rule and ne_rule and sw_rule and se_rule

                self.__point_in_hexagon[point] = point_is_inside


    def __init_frame(self):
        """Initialize the frame with neutral content in each cell."""

        self.__frame = dict()
        self.__nx = 4*self.__n
        self.__ny = 2*self.__n
        self.__xy_cell_size = 2

        for cell_x in range(self.__nx + 1):
            for cell_y in range(self.__ny + 1):
                cell = (cell_x, cell_y)
                self.__frame[cell] = Hexagon.__SPACE*self.__xy_cell_size

        for point_v in self.__v_list:
            for point_u in self.__u_list:
                point = (point_u, point_v)
                if self.__point_in_hexagon[point]:
                    cell = self.__point_to_cell(point)
                    self.__frame[cell] = Hexagon.__FILLER*self.__xy_cell_size


    def __init_row_labels(self):
        """Initialize labels refering rows of the frame."""

        self.__row_labels = list(string.ascii_lowercase)
        self.__row_labels.sort()
        assert 2*self.__n + 1 <= len(self.__row_labels)
        self.__row_labels = self.__row_labels[0:2*self.__n + 1]
        self.__row_labels.reverse()


    def __init_count_labels(self):
        """Initialize labels for counting hexagon nodes in a row."""

        self.__count_labels = list(string.digits)
        self.__count_labels.remove("0")
        self.__count_labels.sort()
        assert 2*self.__n + 1 <= len(self.__count_labels)
        self.__count_labels = self.__count_labels[0: 2*self.__n + 1]


    def __init_left_labels(self):
        """Initialize left side labels."""

        self.__left_labels = [None for cell_y in range(self.__ny + 1)]

        for point_v in self.__v_list:
            for point_u in self.__u_list:
                point = (point_u, point_v)
                if self.__point_in_hexagon[point]:
                    (_, cell_y) = self.__point_to_cell(point)
            self.__left_labels[cell_y] = ""
            self.__left_labels[cell_y] += self.__row_labels[cell_y]
            self.__left_labels[cell_y] += self.__count_labels[0]


    def __init_right_labels(self):
        """Initialize right side labels."""

        self.__right_labels = [None for cell_y in range(self.__ny + 1)]

        for point_v in self.__v_list:
            node_count = 0
            for point_u in self.__u_list:
                point = (point_u, point_v)
                if self.__point_in_hexagon[point]:
                    (_, cell_y) = self.__point_to_cell(point)
                    node_count += 1
            self.__right_labels[cell_y] = ""
            self.__right_labels[cell_y] += self.__row_labels[cell_y]
            self.__right_labels[cell_y] += self.__count_labels[node_count - 1]


    def __init_labels_to_points(self):
        """Initialize the mapping of a label to a point."""

        self.__labels_to_points = dict()

        for point_v in self.__v_list:
            node_count = 0
            for point_u in self.__u_list:
                point = (point_u, point_v)
                if self.__point_in_hexagon[point]:
                    (_, cell_y) = self.__point_to_cell(point)
                    node_count += 1
                    label = ""
                    label += self.__row_labels[cell_y]
                    label += self.__count_labels[node_count - 1]
                    self.__labels_to_points[label] = point


    def __init_labels_from_points(self):
        """Initialize the mapping of a point to a label."""

        self.__labels_from_points = dict()

        for (label, point) in self.__labels_to_points.items():
            self.__labels_from_points[point] = label


    def __point_to_cell(self, point):
        """Convert a point to a cell."""

        (point_u, point_v) = point
        cell = (2*self.__n + 2*point_u + point_v, self.__n - point_v)
        return cell


    def clear_cells(self):
        """Clear all cells of the frame."""

        for label in self.__labels_to_points:
            self.clear_cell_at_label(label)


    def clear_cell_at_label(self, label):
        """Clear the cell at a given label."""
        self.set_cell_at_label(label, "")


    def clear_cell_at_point(self, point):
        """Clear the cell at a given point."""
        self.set_cell_at_point(point, "")


    def get_first_adjacent_labels(self, label):
        """Return the labels of nodes at one segment of a given node
        referenced by a label"""

        point = self.__labels_to_points[label]
        (point_u, point_v) = point

        first_nodes = list()

        for (delta_u, delta_v) in self.__point_directions:
            point_shifted = (point_u + delta_u, point_v + delta_v)
            if self.has_node_at_point(point_shifted):
                first_nodes.append(self.__labels_from_points[point_shifted])
            else:
                first_nodes.append(None)

        return first_nodes


    def get_second_adjacent_labels(self, label):
        """Return the labels of nodes at two straight segments of a given node
        referenced by a label."""

        point = self.__labels_to_points[label]
        (point_u, point_v) = point

        second_nodes = list()

        for (delta_u, delta_v) in self.__point_directions:
            point_shifted = (point_u + 2*delta_u, point_v + 2*delta_v)
            if self.has_node_at_point(point_shifted):
                second_nodes.append(self.__labels_from_points[point_shifted])
            else:
                second_nodes.append(None)

        return second_nodes


    def get_labels(self):
        """Return the labels of all the nodes inside the hexagon."""
        return self.__labels_to_points.keys()


    def get_point(self, label):
        """Return the point at a given label."""
        return self.__labels_to_points[label]


    def get_placement_labels(self):
        """Return the labels of valid placement nodes.
        TODO: reformulate the role fo the method, because Hexagon should
        not know about JERSI rules."""

        placement_node_labels = dict()

        placement_node_labels[0] = list()
        placement_node_labels[1] = list()

        for point_v in self.__v_list[:2]:
            for point_u in self.__u_list:
                point = (point_u, point_v)
                if self.__point_in_hexagon[point]:
                    label = self.__labels_from_points[point]
                    placement_node_labels[0].append(label)

        for point_v in self.__v_list[-2:]:
            for point_u in self.__u_list:
                point = (point_u, point_v)
                if self.__point_in_hexagon[point]:
                    label = self.__labels_from_points[point]
                    placement_node_labels[1].append(label)

        return placement_node_labels


    def has_node_at_point(self, point):
        """Is there an hexagon node at a given point?"""

        has_node = False

        (point_u, point_v) = point

        if (point_u in self.__u_list) and (point_v in self.__v_list):
            has_node = self.__point_in_hexagon[point]

        return has_node


    def print_frame(self):
        """Print the frame."""

        for cell_y in range(self.__ny + 1):
            line = self.__left_labels[cell_y] + Hexagon.__SPACE*self.__xy_cell_size
            for cell_x in range(self.__nx + 1):
                cell = (cell_x, cell_y)
                line += self.__frame[cell]
            line += Hexagon.__SPACE*self.__xy_cell_size + self.__right_labels[cell_y]
            print(line)


    def set_cell_at_label(self, label, cell_text):
        """Set the cell text at a given label."""

        point = self.__labels_to_points[label]
        self.set_cell_at_point(point, cell_text)


    def set_cell_at_point(self, point, cell_text):
        """Set the cell text at a given point."""

        assert len(cell_text) <= self.__xy_cell_size
        cell = self.__point_to_cell(point)
        self.__frame[cell] = cell_text.rjust(self.__xy_cell_size, Hexagon.__FILLER)


class Sort:
    """Capture the knowloedge about the sort of JERSI forms."""

    __names = ["N", "K", "R", "C"]
    __max_count = [1, 4, 4, 4]
    __long_names = ["kunti", "cukla", "kurfa", "kuctai"]
    __indices = list(range(len(__names)))
    assert len(__long_names) == len(__names)
    assert len(__max_count) == len(__names)

    kunti = __long_names.index("kunti")
    cukla = __long_names.index("cukla")
    kurfa = __long_names.index("kurfa")
    kuctai = __long_names.index("kuctai")

    __beat_cases = list()

    # kunti rule
    for (fst_name, snd_name) in [("K", "N"), ("R", "N"), ("C", "N")]:
        fst_index = __names.index(fst_name)
        snd_index = __names.index(snd_name)
        __beat_cases.append((fst_index, snd_index))

    # cukla-kurfa-kuctai rule
    for (fst_name, snd_name) in [("C", "R"), ("R", "K"), ("K", "C")]:
        fst_index = __names.index(fst_name)
        snd_index = __names.index(snd_name)
        __beat_cases.append((fst_index, snd_index))


    @staticmethod
    def beats(fst_index, snd_index):
        """Does sort fst_index beat sort snd_index?"""

        assert fst_index in Sort.__indices
        assert snd_index in Sort.__indices
        return (fst_index, snd_index) in Sort.__beat_cases


    @staticmethod
    def beats_by_long_names(fst_long_name, snd_long_name):
        """Does sort fst_long_name beat sort snd_long_name?"""

        fst_index = Sort.__long_names.index(fst_long_name)
        snd_index = Sort.__long_names.index(snd_long_name)
        return Sort.beats(fst_index, snd_index)


    @staticmethod
    def beats_by_names(fst_name, snd_name):
        """Does sort fst_name beat sort snd_name?"""

        (fst_index, j) = (Sort.__names.index(fst_name), Sort.__names.index(snd_name))
        return Sort.beats(fst_index, j)


    @staticmethod
    def get_index(name):
        """Return the sort index for its name or long name."""

        name_uppered = name.upper()
        name_lowered = name.lower()

        index = None

        if name in Sort.__names:
            index = Sort.__names.index(name)

        elif name in Sort.__long_names:
            index = Sort.__long_names.index(name)

        elif name_uppered in Sort.__names:
            index = Sort.__names.index(name_uppered)

        elif name_lowered in Sort.__long_names:
            index = Sort.__long_names.index(name_lowered)

        assert index is not None

        return index


    @staticmethod
    def get_indices():
        """Return all the sort indices."""
        return Sort.__indices


    @staticmethod
    def get_long_name(index):
        """Return the long name associated to a given sort index."""
        return Sort.__long_names[index]


    @staticmethod
    def get_max_occurrences(index):
        """Return the maximum occurences of a given sort."""
        return Sort.__max_count[index]


    @staticmethod
    def get_name(index):
        """Return the name associated to a sort index."""
        return Sort.__names[index]


class Color:
    """Capture the knowlege about colors in JERSI."""

    __names = ["blue", "red"]
    __indices = list(range(len(__names)))
    __transformers = [str.upper, str.lower]
    assert len(__indices) == 2
    assert len(__transformers) == len(__indices)

    blue = __names.index("blue")
    red = __names.index("red")


    @staticmethod
    def get_count():
        """Return the number of colors."""
        return len(Color.__indices)


    @staticmethod
    def get_index(name):
        """Return the color index from its name."""

        index = None

        if name in Color.__names:
            index = Color.__names.index(name)

        else:
            assert name != ""
            for (color, transformer) in enumerate(Color.__transformers):
                if name == transformer(name):
                    index = color
                    break

        assert index is not None

        return index


    @staticmethod
    def get_indices():
        """Return all the color indices."""
        return Color.__indices


    @staticmethod
    def get_name(i):
        """Return the name associated to a given color index."""
        return Color.__names[i]


    @staticmethod
    def get_transformer(i):
        """Return the transforer function associated to a given color."""
        return Color.__transformers[i]


class Form:
    """Capture knowlege about form in JERSI."""

    def __init__(self, sort, color):
        """Initialize a form of a given sort and color,
        but not yet assigned to a node."""

        assert sort in Sort.get_indices()
        assert color in Color.get_indices()
        self.sort = sort
        self.color = color
        self.node = None


    def get_name(self):
        """Return the name of a form."""

        name = Sort.get_name(self.sort)
        name_transformed = Color.get_transformer(self.color)(name)
        return name_transformed


    @staticmethod
    def make(sort_name, color_name):
        """Return a new form from a given sort and color names."""

        sort = Sort.get_index(sort_name)
        color = Color.get_index(color_name)
        form = Form(sort, color)
        return form


    @staticmethod
    def parse_sort_and_color(name):
        """Return the pair of indices (sort, color) form the given name."""

        sort = Sort.get_index(name)
        color = Color.get_index(name)
        return (sort, color)


class Node:
    """Capture knowledge about node in JERSI."""


    def __init__(self, label, grid):
        """Initialize a node at a given label for the given grid."""

        self.label = label
        self.grid = grid
        self.forms = [None, None]
        self.first_adjacent_labels = None
        self.second_adjacent_labels = None


    def __deepcopy__(self, memo):
        """Customized deepcopy of a node: only the grid and forms
        attributes are deep copied."""

        new_one = Node(self.label, None)

        memo[id(self)] = new_one

        new_one.grid = copy.deepcopy(self.grid, memo)
        new_one.forms = copy.deepcopy(self.forms, memo)

        new_one.first_adjacent_labels = self.first_adjacent_labels
        new_one.second_adjacent_labels = self.second_adjacent_labels

        return new_one


    def get_top(self):
        """Return the top of the form stack at this node."""

        if self.forms[1] is not None:
            top = self.forms[1]

        elif self.forms[0] is not None:
            top = self.forms[0]

        else:
            top = None

        return top


    def get_top_color(self):
        """Return the color of the top of the form stack at this node."""

        if self.forms[1] is not None:
            color = self.forms[1].color

        elif self.forms[0] is not None:
            color = self.forms[0].color

        else:
            color = None

        return color


    def get_top_sort(self):
        """Return the sort of the top of the form stack at this node."""

        if self.forms[1] is not None:
            sort = self.forms[1].sort

        elif self.forms[0] is not None:
            sort = self.forms[0].sort

        else:
            sort = None

        return sort


    def has_one_or_two_forms(self):
        """Does this node have either one or two forms?"""
        return self.forms[0] is not None


    def has_two_forms(self):
        """Does this node have two forms?"""
        return self.forms[1] is not None


    def has_zero_form(self):
        """Does this node have no form?"""
        return self.forms[0] is None


    def has_zero_or_one_form(self):
        """Does this node have either zero or one form?"""
        return self.forms[1] is None


    def move_one_form(self, dst_node):
        """Move one form (its top) from this node to a destinaiton node."""

        form_captured = False
        kunti_captured = False

        assert dst_node is not None
        jersi_assert(dst_node.label in self.first_adjacent_labels,
                     "destination should stay at one segment from source")

        jersi_assert(self.has_one_or_two_forms(),
                     "source should have one or two forms")

        top = self.get_top()

        if dst_node.has_zero_form():
            self.unset_form(top)
            dst_node.set_form(top)

        elif dst_node.get_top_color() == self.get_top_color():
            jersi_assert(dst_node.has_zero_or_one_form(),
                         "source should have zero or one form")

            self.unset_form(top)
            dst_node.set_form(top)

        else:
            jersi_assert(Sort.beats(self.get_top_sort(), dst_node.get_top_sort()),
                         "source should beats destination")

            form_captured = True

            if dst_node.forms[1] is not None:
                if dst_node.forms[1].sort == Sort.kunti:
                    kunti_captured = True

            if dst_node.forms[0] is not None:
                if dst_node.forms[0].sort == Sort.kunti:
                    kunti_captured = True

            dst_node.unset_forms()
            self.unset_form(top)
            dst_node.set_form(top)

        return (form_captured, kunti_captured)


    def move_two_forms(self, dst_node):
        """Move two forms from this node to a destinaiton node."""

        form_captured = False
        kunti_captured = False

        jersi_assert(self.has_two_forms(), "source should have two forms")
        assert dst_node is not None

        stepping_one_segment = dst_node.label in self.first_adjacent_labels
        stepping_two_segments = dst_node.label in self.second_adjacent_labels

        jersi_assert(stepping_one_segment or stepping_two_segments,
                     "destination should stay at one or two segments from source")

        if stepping_two_segments:
            dst_direction = self.second_adjacent_labels.index(dst_node.label)
            int_label = self.first_adjacent_labels[dst_direction]
            int_node = self.grid.nodes[int_label]
            jersi_assert(int_node.has_zero_form(),
                         "path from source to destination should be free")

        if dst_node.has_zero_form():
            pass

        else:
            jersi_assert(dst_node.get_top_color() != self.get_top_color(),
                         "source and destination colors should be different")

            jersi_assert(Sort.beats(self.get_top_sort(), dst_node.get_top_sort()),
                         "source should beat destination")

            form_captured = True

            if dst_node.forms[1] is not None:
                if dst_node.forms[1].sort == Sort.kunti:
                    kunti_captured = True

            if dst_node.forms[0] is not None:
                if dst_node.forms[0].sort == Sort.kunti:
                    kunti_captured = True

            dst_node.unset_forms()

        top = self.get_top()
        self.unset_form(top)

        bottom = self.get_top()
        self.unset_form(bottom)

        dst_node.set_form(bottom)
        dst_node.set_form(top)

        return (form_captured, kunti_captured)


    def set_form(self, form):
        """Set a free form to this node."""

        assert self.has_zero_or_one_form()

        if self.forms[0] is None:
            self.forms[0] = form
            form.node = self

        else:
            jersi_assert(self.forms[0].color == form.color,
                         "stacked forms should have same color")

            jersi_assert(self.forms[0].sort != Sort.kunti,
                         "no form should be stacked above kunti")

            self.forms[1] = form
            form.node = self


    def unset_form(self, form):
        """Remove a given form from this node."""

        assert self == form.node

        if self.forms[1] == form:
            self.forms[1] = None

        elif self.forms[0] == form:
            self.forms[0] = None

        form.node = None


    def unset_forms(self):
        """Remove all forms from this node."""

        if self.forms[1] is not None:
            self.forms[1].node = None
            self.forms[1] = None

        if self.forms[0] is not None:
            self.forms[0].node = None
            self.forms[0] = None


class Grid:


    def __init__(self, hexagon):

        self.hexagon = hexagon
        self.placement_node_labels = self.hexagon.get_placement_labels()

        self.nodes = None
        self.forms = None

        self.__init_nodes()
        self.__init_forms()


    def __deepcopy__(self, memo):

        cls = self.__class__
        new_one = cls.__new__(cls)
        memo[id(self)] = new_one

        new_one.hexagon = self.hexagon
        new_one.placement_node_labels = self.placement_node_labels

        new_one.nodes = copy.deepcopy(self.nodes, memo)
        new_one.forms = copy.deepcopy(self.forms, memo)

        return new_one


    def __init_nodes(self):

        self.nodes = dict()

        for label in self.hexagon.get_labels():
            node = Node(label, self)
            node.first_adjacent_labels = self.hexagon.get_first_adjacent_labels(node.label)
            node.second_adjacent_labels = self.hexagon.get_second_adjacent_labels(node.label)
            self.nodes[label] = node


    def __init_forms(self):

        self.forms = dict()
        for color in Color.get_indices():
            self.forms[color] = dict()
            for sort in Sort.get_indices():
                self.forms[color][sort] = list()
                sort_count = Sort.get_max_occurrences(sort)
                for _ in range(sort_count):
                    form = Form(sort, color)
                    self.forms[color][sort].append(form)


    def count_forms_by_colors_and_sorts(self):

        count = dict()

        for color in Color.get_indices():
            count[color] = dict()
            for sort in Sort.get_indices():
                count[color][sort] = 0
                for form in self.forms[color][sort]:
                    if form.node is not None:
                        count[color][sort] += 1
        return count


    def count_kuntis_by_colors(self):

        count = dict()

        for color in Color.get_indices():
            count[color] = 0
            for form in self.forms[color][Sort.kunti]:
                if form.node is not None:
                    count[color] += 1

        return count


    def export_positions(self):

        positions = dict()

        for color in Color.get_indices():
            for sort in Sort.get_indices():
                for form in self.forms[color][sort]:
                    if form.node is not None:
                        node = form.node
                        node_label = node.label
                        if node_label not in positions:
                            positions[node_label] = list()

                            if node.forms[0] is not None:
                                positions[node_label].append(node.forms[0].get_name())

                            if node.forms[1] is not None:
                                positions[node_label].append(node.forms[1].get_name())

        return positions


    def import_placement(self, positions):
        self.import_positions(positions, check_placement=True)


    def import_positions(self, positions, check_placement=False):

        count = dict()
        for color in Color.get_indices():
            count[color] = dict()
            for sort in Sort.get_indices():
                count[color][sort] = 0

        for (node_label, form_names) in positions.items():
            for form_name in form_names:
                (sort, color) = Form.parse_sort_and_color(form_name)
                instance = count[color][sort]
                form = self.forms[color][sort][instance]

                if check_placement:
                    self.place_form(form, node_label)
                else:
                    self.set_form(form, node_label)

                count[color][sort] += 1


    def move_one_form(self, src_label, dst_label):
        src_node = self.nodes[src_label]
        dst_node = self.nodes[dst_label]
        return src_node.move_one_form(dst_node)


    def move_two_forms(self, src_label, dst_label):
        src_node = self.nodes[src_label]
        dst_node = self.nodes[dst_label]
        return src_node.move_two_forms(dst_node)


    def print_grid(self):
        self.set_cells()
        self.hexagon.print_frame()


    def set_cells(self):

        self.hexagon.clear_cells()

        for node in self.nodes.values():
            cell_text = ""

            if node.forms[0] is not None:
                cell_text = node.forms[0].get_name() + cell_text

            if node.forms[1] is not None:
                cell_text = node.forms[1].get_name() + cell_text

            self.hexagon.set_cell_at_label(node.label, cell_text)


    def place_form(self, form, dst_label):

        jersi_assert(dst_label in self.placement_node_labels[form.color],
                     "%s is not a placement position for the %s color" %
                     (dst_label, Color.get_name(form.color)))

        self.set_form(form, dst_label)


    def set_form(self, form, dst_label):
        dst_node = self.nodes[dst_label]
        dst_node.set_form(form)


    def set_forms_at_random_positions(self):

        self.unset_forms()

        blue = Color.blue
        red = Color.red
        kunti = Sort.kunti

        blue_forms_wo_kunti = list()
        blue_kunti = None
        for sort in Sort.get_indices():
            if sort != kunti:
                blue_forms_wo_kunti.extend(self.forms[blue][sort])
            else:
                blue_kunti = self.forms[blue][sort][0]

        red_forms_wo_kunti = list()
        red_kunti = None
        for sort in Sort.get_indices():
            if sort != kunti:
                red_forms_wo_kunti.extend(self.forms[red][sort])
            else:
                red_kunti = self.forms[red][sort][0]

        random.shuffle(blue_forms_wo_kunti)
        random.shuffle(red_forms_wo_kunti)

        # set blue forms

        self.place_form(blue_forms_wo_kunti[0], "b1")
        self.place_form(blue_forms_wo_kunti[1], "b2")
        self.place_form(blue_forms_wo_kunti[2], "b3")
        self.place_form(blue_forms_wo_kunti[3], "b4")
        self.place_form(blue_forms_wo_kunti[4], "b5")
        self.place_form(blue_forms_wo_kunti[5], "b6")

        self.place_form(blue_forms_wo_kunti[6], "a1")

        self.place_form(blue_forms_wo_kunti[7], "a2")
        self.place_form(blue_forms_wo_kunti[8], "a2")

        self.place_form(blue_kunti, "a3")

        self.place_form(blue_forms_wo_kunti[9], "a4")
        self.place_form(blue_forms_wo_kunti[10], "a4")

        self.place_form(blue_forms_wo_kunti[11], "a5")

        # set red forms

        self.place_form(red_forms_wo_kunti[0], "h6")
        self.place_form(red_forms_wo_kunti[1], "h5")
        self.place_form(red_forms_wo_kunti[2], "h4")
        self.place_form(red_forms_wo_kunti[3], "h3")
        self.place_form(red_forms_wo_kunti[4], "h2")
        self.place_form(red_forms_wo_kunti[5], "h1")

        self.place_form(red_forms_wo_kunti[6], "i5")

        self.place_form(red_forms_wo_kunti[7], "i4")
        self.place_form(red_forms_wo_kunti[8], "i4")

        self.place_form(red_kunti, "i3")

        self.place_form(red_forms_wo_kunti[9], "i2")
        self.place_form(red_forms_wo_kunti[10], "i2")

        self.place_form(red_forms_wo_kunti[11], "i1")


    def set_forms_at_standard_positions(self):

        self.unset_forms()

        blue = Color.blue
        red = Color.red

        kunti = Sort.kunti
        cukla = Sort.cukla
        kurfa = Sort.kurfa
        kuctai = Sort.kuctai

        # set blue forms

        self.place_form(self.forms[blue][cukla][0], "b1")
        self.place_form(self.forms[blue][kurfa][0], "b2")
        self.place_form(self.forms[blue][kuctai][0], "b3")
        self.place_form(self.forms[blue][cukla][1], "b4")
        self.place_form(self.forms[blue][kurfa][1], "b5")
        self.place_form(self.forms[blue][kuctai][1], "b6")

        self.place_form(self.forms[blue][kuctai][2], "a1")

        self.place_form(self.forms[blue][kurfa][2], "a2")
        self.place_form(self.forms[blue][cukla][2], "a2")

        self.place_form(self.forms[blue][kunti][0], "a3")

        self.place_form(self.forms[blue][kurfa][3], "a4")
        self.place_form(self.forms[blue][kuctai][3], "a4")

        self.place_form(self.forms[blue][cukla][3], "a5")

        # set red forms

        self.place_form(self.forms[red][cukla][0], "h6")
        self.place_form(self.forms[red][kurfa][0], "h5")
        self.place_form(self.forms[red][kuctai][0], "h4")
        self.place_form(self.forms[red][cukla][1], "h3")
        self.place_form(self.forms[red][kurfa][1], "h2")
        self.place_form(self.forms[red][kuctai][1], "h1")

        self.place_form(self.forms[red][kuctai][2], "i5")

        self.place_form(self.forms[red][kurfa][2], "i4")
        self.place_form(self.forms[red][cukla][2], "i4")

        self.place_form(self.forms[red][kunti][0], "i3")

        self.place_form(self.forms[red][kurfa][3], "i2")
        self.place_form(self.forms[red][kuctai][3], "i2")

        self.place_form(self.forms[red][cukla][3], "i1")


    def unset_forms(self):
        for node in self.nodes.values():
            node.unset_forms()


class Game:


    def __init__(self):

        self.grid = None
        self.placement = dict()
        self.history = list()
        self.game_over = False
        self.placement_over = False
        self.last_count = None
        self.move_count = 1

        hexagon = Hexagon(5)
        self.grid = Grid(hexagon)
        self.new_standard_game()


    def __deepcopy__(self, memo):

        cls = self.__class__
        new_one = cls.__new__(cls)
        memo[id(self)] = new_one

        new_one.grid = copy.deepcopy(self.grid, memo)

        new_one.placement = copy.copy(self.placement)
        new_one.history = copy.copy(self.history)

        new_one.game_over = self.game_over
        new_one.placement_over = self.placement_over
        new_one.last_count = self.last_count
        new_one.move_count = self.move_count

        return new_one


    def new_free_game(self):
        self.reset_game()

        print()
        print("new free game")
        self.grid.print_grid()
        self.print_status()


    def new_random_game(self):
        self.reset_game()
        self.grid.set_forms_at_random_positions()
        self.placement = self.grid.export_positions()
        self.placement_over = True

        print()
        print("new random game")
        self.grid.print_grid()
        self.print_status()


    def new_standard_game(self):
        self.reset_game()
        self.grid.set_forms_at_standard_positions()
        self.placement = self.grid.export_positions()
        self.placement_over = True

        print()
        print("new standard game")
        self.grid.print_grid()
        self.print_status()


    def parse_and_play_instruction(self, instruction):

        instruction_validated = False

        positions = dict()
        moves = list()

        parsing_validated = Game.parse_instruction(instruction, positions, moves)

        if parsing_validated:

            saved_game = self.save_game()

            assert len(positions) == 1 or len(moves) == 1

            if len(positions) == 1:
                playing_validated = self.play_placement(positions)

            elif len(moves) == 1:
                playing_validated = self.play_moves(moves)

            if playing_validated:
                instruction_validated = True
            else:
                self.restore_game(saved_game)

        return instruction_validated


    @staticmethod
    def parse_instruction(instruction, positions, moves):

        instruction_validated = True

        rule_set_form = re.compile(
            r"^(?P<node_label>\w{2}):(?P<form_name>\w)$")

        rule_move_one_form = re.compile(
            r"^(?P<src_label>\w{2})-(?P<dst_label>\w{2})!{0,2}$")

        rule_move_two_forms = re.compile(
            r"^(?P<src_label>\w{2})=(?P<dst_label>\w{2})!{0,2}$")

        rule_move_one_then_two_forms = re.compile(
            r"^(?P<src_label>\w{2})-(?P<int_label>\w{2})!{0,1}=(?P<dst_label>\w{2})!{0,2}$")

        rule_move_two_then_one_forms = re.compile(
            r"^(?P<src_label>\w{2})=(?P<int_label>\w{2})!{0,1}-(?P<dst_label>\w{2})!{0,2}$")

        match_set_form = rule_set_form.match(instruction)
        match_move_one_form = rule_move_one_form.match(instruction)
        match_move_two_forms = rule_move_two_forms.match(instruction)
        match_move_one_then_two_forms = rule_move_one_then_two_forms.match(instruction)
        match_move_two_then_one_forms = rule_move_two_then_one_forms.match(instruction)

        if match_set_form:
            node_label = match_set_form.group("node_label")
            form_name = match_set_form.group("form_name")
            if node_label not in positions:
                positions[node_label] = list()
            positions[node_label].append(form_name)

        elif match_move_one_form:
            src_label = match_move_one_form.group("src_label")
            dst_label = match_move_one_form.group("dst_label")
            moves.append([(1, src_label, dst_label)])

        elif match_move_two_forms:
            src_label = match_move_two_forms.group("src_label")
            dst_label = match_move_two_forms.group("dst_label")
            moves.append([(2, src_label, dst_label)])

        elif match_move_one_then_two_forms:
            src_label = match_move_one_then_two_forms.group("src_label")
            int_label = match_move_one_then_two_forms.group("int_label")
            dst_label = match_move_one_then_two_forms.group("dst_label")
            moves.append([(1, src_label, int_label), (2, int_label, dst_label)])

        elif match_move_two_then_one_forms:
            src_label = match_move_two_then_one_forms.group("src_label")
            int_label = match_move_two_then_one_forms.group("int_label")
            dst_label = match_move_two_then_one_forms.group("dst_label")
            moves.append([(2, src_label, int_label), (1, int_label, dst_label)])

        else:
            print("syntax error in instruction '%s'" % instruction)
            instruction_validated = False

        return instruction_validated


    def play_moves(self, moves):

        play_validated = True

        try:
            for move_steps in moves:

                jersi_assert(not self.game_over, "game should be not over")
                jersi_assert(self.placement_over, "placement should be over")

                move_color = (self.move_count - 1) % Color.get_count()
                step_count = 1
                annotated_steps = list()

                for (form_count, src_label, dst_label) in move_steps:

                    jersi_assert(src_label in self.grid.nodes.keys(),
                                 "source label should be valid")

                    jersi_assert(dst_label in self.grid.nodes.keys(),
                                 "destination label should be valid")

                    src_node = self.grid.nodes[src_label]

                    jersi_assert(src_node.has_one_or_two_forms(),
                                 "source should have one or two forms")

                    jersi_assert(src_node.get_top_color() == move_color,
                                 "moved color should be valid")

                    if form_count == 1:
                        (form_captured,
                         kunti_captured) = self.grid.move_one_form(src_label, dst_label)

                    elif form_count == 2:
                        (form_captured,
                         kunti_captured) = self.grid.move_two_forms(src_label, dst_label)

                    else:
                        assert False

                    annotated_steps.append((form_count, src_label, dst_label,
                                            form_captured, kunti_captured))
                    step_count += 1

                self.history.append(annotated_steps)
                self.move_count += 1
                print("move %s OK" % Game.stringify_move(annotated_steps))

                self.update_end_conditions()

        except(JersiError) as jersi_assertion_error:
            print("assertion failed: %s !!!" % jersi_assertion_error.message)
            print("move %s KO !!!" % Game.stringify_move(move_steps))
            play_validated = False

        return play_validated


    def play_placement(self, positions):

        play_validated = True

        try:
            assert len(positions) == 1
            [(node_label, form_names)] = positions.items()

            assert len(form_names) == 1
            form_name = form_names[0]

            jersi_assert(not self.game_over, "game should be not over")
            jersi_assert(not self.placement_over, "placement should be not over")

            (sort, color) = Form.parse_sort_and_color(form_name)

            move_color = (self.move_count - 1) % Color.get_count()
            jersi_assert(color == move_color, "moved color should be valid")

            form_count = self.grid.count_forms_by_colors_and_sorts()
            instance = form_count[color][sort]
            jersi_assert(instance < Sort.get_max_occurrences(sort), "sort should be available")

            form = self.grid.forms[color][sort][instance]
            self.grid.place_form(form, node_label)

            self.move_count += 1

            has_available_form = False
            for color in form_count.keys():
                for sort in form_count[color].keys():
                    if form_count[color][sort] < Sort.get_max_occurrences(sort):
                        has_available_form = True
                        break

            if not has_available_form:
                self.placement_over = False

            if self.placement_over:
                self.placement = self.grid.export_positions()

        except(JersiError) as jersi_assertion_error:
            print("assertion failed: %s !!!" % jersi_assertion_error.message)
            play_validated = False

        return play_validated


    @staticmethod
    def print_help():
        print()
        print("commands:")
        print("    a1-b1=d1 | a1=c1-d1 | a1-b1 | a1=c1 : examples of move in one or two steps")
        print("                          a1:K  | h1:c  : examples of placement")
        print("      h: help")
        print("      q: quit")
        print("     ns: new game with standard positions")
        print("     nr: new game with random positions")
        print("     nf: new game with free positions")
        print("     ph: print game history (only moves; not placement)")
        print("   rg f: read the game from the given file 'f'")
        print("   rp f: read the positions from the given file 'f'")
        print("   wg f: write the game into the given file 'f'")
        print("   wp f: write the positions into the given file 'f'")


    def print_history(self):

        print()
        print("move history:")
        for line in Game.textify_history(self.history):
            print(line)


    def print_status(self):

        form_count = self.grid.count_forms_by_colors_and_sorts()

        if self.game_over:
            text = "game over"

            for color in sorted(form_count.keys()):
                text += " / %s %d" % (Color.get_name(color), form_count[color][Sort.kunti])

        else:
            move_color = (self.move_count - 1) % Color.get_count()
            move_color_name = Color.get_name(move_color)
            text = "%s turn" % move_color_name

            text += " / move %d" % self.move_count

            if self.last_count is not None:
                text += " / last %d moves" % self.last_count

        for color in sorted(form_count.keys()):
            text += " / " + Color.get_name(color)
            color_transformer = Color.get_transformer(color)
            for sort in sorted(form_count[color].keys()):
                text += " %s=%d" % (color_transformer(Sort.get_name(sort)), form_count[color][sort])

        print()
        print(text)


    def read_game(self, file_path):

        positions = dict()
        moves = list()
        parsing_validated = True

        file_stream = open(os.path.join(os.curdir, file_path), 'r')

        for line in file_stream:

            if re.match(r"^s*$", line):
                continue

            elif re.match(r"^s*#.*$", line):
                continue

            else:
                instructions = line.split()
                for instruction in instructions:
                    instruction_validated = Game.parse_instruction(instruction, positions, moves)
                    if not instruction_validated:
                        parsing_validated = False

        file_stream.close()

        if parsing_validated:

            saved_game = self.save_game()
            self.reset_game()

            playing_validated = True

            try:
                self.grid.import_placement(positions)
                self.placement_over = True

                play_moves_validated = self.play_moves(moves)
                if not play_moves_validated:
                    playing_validated = False

            except(JersiError) as jersi_assertion_error:
                print("assertion failed: %s !!!" % jersi_assertion_error.message)
                playing_validated = False

            if playing_validated:
                print()
                print("game from file '%s'" % file_path)
                self.grid.print_grid()
                self.print_status()

            else:
                self.restore_game(saved_game)


    def read_positions(self, file_path):

        positions = dict()
        moves = list()
        parsing_validated = True

        file_stream = open(os.path.join(os.curdir, file_path), 'r')

        for line in file_stream:
            if re.match(r"^s*$", line):
                continue
            elif re.match(r"^s*#.*$", line):
                continue
            else:
                instructions = line.split()
                for instruction in instructions:
                    instruction_validated = Game.parse_instruction(instruction, positions, moves)
                    if not instruction_validated:
                        parsing_validated = False

        file_stream.close()

        if parsing_validated:

            saved_game = self.save_game()
            self.reset_game()

            importing_validated = True
            try:
                jersi_assert(len(moves) == 0, "file should not have moves")

                self.grid.import_positions(positions)
                self.placement_over = True
                self.placement = self.grid.export_positions()

            except(JersiError) as jersi_assertion_error:
                print("assertion failed: %s !!!" % jersi_assertion_error.message)
                importing_validated = False

            if importing_validated:
                print()
                print("positions from file '%s'" % file_path)
                self.grid.print_grid()
                self.print_status()

            else:
                self.restore_game(saved_game)


    def reset_game(self):

        self.grid.unset_forms()
        self.placement = dict()
        self.history = list()
        self.game_over = False
        self.placement_over = False
        self.last_count = None
        self.move_count = 1


    def restore_game(self, saved_game):

        self.grid = saved_game.grid
        self.placement = saved_game.placement
        self.history = saved_game.history
        self.game_over = saved_game.game_over
        self.placement_over = saved_game.placement_over
        self.last_count = saved_game.last_count
        self.move_count = saved_game.move_count


    def run(self):

        continue_running = True

        while continue_running:

            command_line = input("command? ")
            command_args = command_line.split()

            if len(command_args) < 1:
                print("turn syntax error !!!")

            elif command_args[0] == "h":
                Game.print_help()

            elif command_args[0] == "nf":
                self.new_free_game()

            elif command_args[0] == "nr":
                self.new_random_game()

            elif command_args[0] == "ns":
                self.new_standard_game()

            elif command_args[0] == "ph":
                self.print_history()

            elif command_args[0] == "q":
                continue_running = False

            elif command_args[0] == "rg":

                if len(command_args) == 2:
                    file_path = command_args[1]
                    self.read_game(file_path)
                else:
                    print("turn syntax error !!!")

            elif command_args[0] == "rp":

                if len(command_args) == 2:
                    file_path = command_args[1]
                    self.read_positions(file_path)
                else:
                    print("turn syntax error !!!")

            elif command_args[0] == "wg":

                if len(command_args) == 2:
                    file_path = command_args[1]
                    self.write_game(file_path)
                else:
                    print("turn syntax error !!!")

            elif command_args[0] == "wp":

                if len(command_args) == 2:
                    file_path = command_args[1]
                    self.write_positions(file_path)
                else:
                    print("turn syntax error !!!")

            else:
                if len(command_args) == 1:
                    instruction = command_args[0]
                    instruction_validated = self.parse_and_play_instruction(instruction)

                    if instruction_validated:
                        self.grid.print_grid()
                        self.print_status()
                else:
                    print("turn syntax error !!!")


    def save_game(self):

        saved_game = copy.deepcopy(self)
        return saved_game


    @staticmethod
    def stringify_move(move_steps):

        move_text = ""

        for (step_index, step) in enumerate(move_steps):

            if len(step) == 5:
                (form_count, src_label, dst_label,
                 form_captured, kunti_captured) = step

            elif len(step) == 3:
                (form_count, src_label, dst_label,
                 form_captured, kunti_captured) = (*step, False, False)

            else:
                assert False

            step_text = ""

            if step_index == 0:
                step_text += src_label

            if form_count == 1:
                step_text += "-"

            elif form_count == 2:
                step_text += "="

            step_text += dst_label

            if form_captured:
                step_text += "!"

            if kunti_captured:
                step_text += "!"

            move_text += step_text

        return move_text


    @staticmethod
    def textify_history(history):

        lines = list()

        for (move_index, move_steps) in enumerate(history):

            move_text = Game.stringify_move(move_steps)

            if move_index % 2 == 0:
                lines.append(move_text)
            else:
                lines[-1] += " "*4 + move_text

        return lines


    @staticmethod
    def textify_positions(positions):

        lines = list()

        start_index = 0

        for (node_label, form_names) in  sorted(positions.items()):

            for form_name in form_names:

                form_text = "%s:%s" % (node_label, form_name)

                if start_index % 2 == 0:
                    lines.append(form_text)
                else:
                    lines[-1] += " "*4 + form_text

                start_index += 1

        return lines


    def update_end_conditions(self):

        form_count = self.grid.count_forms_by_colors_and_sorts()

        for color in form_count.keys():
            if form_count[color][Sort.kunti] == 0:
                self.game_over = True

        if not self.game_over:
            if self.last_count is None:
                for color in form_count.keys():
                    for sort in form_count[color].keys():
                        if form_count[color][sort] == 0:
                            self.last_count = 20
            else:
                self.last_count -= 1
                if self.last_count == 0:
                    self.game_over = True


    def write_game(self, file_path):

        file_stream = open(os.path.join(os.curdir, file_path), 'w')

        for line in Game.textify_positions(self.placement):
            file_stream.write("%s\n" % line)

        file_stream.write("\n")

        for line in Game.textify_history(self.history):
            file_stream.write("%s\n" % line)

        file_stream.close()

        print("saving game in file '%s' done" % file_path)


    def write_positions(self, file_path):

        file_stream = open(os.path.join(os.curdir, file_path), 'w')

        for line in Game.textify_positions(self.grid.export_positions()):
            file_stream.write("%s\n" % line)

        file_stream.close()

        print("saving positions in file '%s' done" % file_path)


def main():
    print(_COPYRIGHT_AND_LICENSE)
    my_game = Game()
    my_game.run()


if __name__ == "__main__":
    main()