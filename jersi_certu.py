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


class Hexmap:

    """
    Captures the geometrical knowledge about the Hexmap of JERSI.

    An hexmap is made of nodes. Each node can be set with a text.
    For printing the hexmap, a table is used, which is made of cells
    distributed in rows and columns.

    Example of a table for an hexmap with 5 nodes per side.
    A few cells filled up with one or two letters.
    The left and right columns of labels are not part of the table,
    but they are printed together with the table:

        i1          .k  cr  .n  kr  .c          i5
        h1        .c  .r  .k  .c  .r  .k        h6
        g1      ..  ..  ..  ..  ..  ..  ..      g7
        f1    ..  ..  ..  ..  ..  ..  ..  ..    f8
        e1  ..  ..  ..  ..  ..  ..  ..  ..  ..  e9
        d1    ..  ..  ..  ..  ..  ..  ..  ..    d8
        c1      ..  ..  ..  ..  ..  ..  ..      c7
        b1        .K  .R  .C  .K  .R  .C        b6
        a1          .C  KR  .N  CR  .K          a5

    The nodes of the hexmap are described using an oblique coordinates system :
        - C is the hexmap center;
        - e_u is horizontal unit vector pointing right ;
        - e_v is diagonal unit vector pointing up ;
        - a node P is represented by its center as CP = u*e_u + v*e_v.

    The cells of the table are described using an
    orthogonal coordinates system :
        - O is at the left upper corner ;
        - e_x is horizontal vector pointing right ;
        - e_y is vectical vector pointing down ;
        - a cell P is represented as OP = x*e_x + y*e_y ;
        - x is a column index ; y is a row index.

    The relationship bewteen the (u, v) and (x, y) coordinates systems
    are as follows :
        - e_u  = 2*e_x
        - e_v = e_x - e_y
        - OC = n*e_y + n*e_u
   """


    __SPACE = " "
    __FILLER = "."
    __CELL_SIZE = 2
    __CELL_SPACE = __SPACE * __CELL_SIZE
    __CELL_FILLER = __FILLER * __CELL_SIZE


    def __init__(self, nodes_per_side):
        """Initialize an hexmap parametrized by
        the number of nodes per hexmap side"""

        self.__nodes_per_side = nodes_per_side
        self.__n = self.__nodes_per_side - 1

        # Many information are computed once and memorized in attributes
        # in order to accelerate public queries.
        self.__init_node_coordinates()
        self.__init_node_directions()
        self.__init_has_node_values()
        self.__init_table()
        self.__init_count_labels()
        self.__init_row_labels()
        self.__init_left_labels()
        self.__init_right_labels()
        self.__init_labels_to_nodes()
        self.__init_labels_from_nodes()


    def __init_count_labels(self):
        """Initialize labels for counting nodes in a row."""

        self.__count_labels = list(string.digits)
        self.__count_labels.remove("0")
        self.__count_labels.sort()
        assert 2*self.__n + 1 <= len(self.__count_labels)
        self.__count_labels = self.__count_labels[0: 2*self.__n + 1]


    def __init_has_node_values(self):
        """Initialize the values of the predicate "__has_node"."""

        self.__has_node_values = dict()

        for node_u in self.__u_list:
            for node_v in self.__v_list:
                node = (node_u, node_v)

                ne_rule = (self.__n - node_u - node_v >= 0)
                se_rule = (self.__n - node_u >= 0)
                nw_rule = (self.__n + node_u >= 0)
                sw_rule = (self.__n + node_u + node_v >= 0)

                is_inside = nw_rule and ne_rule and sw_rule and se_rule

                self.__has_node_values[node] = is_inside


    def __init_labels_from_nodes(self):
        """Initialize the mapping of a node to a label."""

        self.__labels_from_nodes = dict()

        for (label, node) in self.__labels_to_nodes.items():
            self.__labels_from_nodes[node] = label


    def __init_labels_to_nodes(self):
        """Initialize the mapping of a label to a node."""

        self.__labels_to_nodes = dict()

        for node_v in self.__v_list:
            node_count = 0
            for node_u in self.__u_list:
                node = (node_u, node_v)
                if self.__has_node_values[node]:
                    (_, cell_y) = self.__node_to_cell(node)
                    node_count += 1
                    label = ""
                    label += self.__row_labels[cell_y]
                    label += self.__count_labels[node_count - 1]
                    self.__labels_to_nodes[label] = node


    def __init_left_labels(self):
        """Initialize left side labels."""

        self.__left_labels = [None for cell_y in range(self.__ny + 1)]

        for node_v in self.__v_list:
            for node_u in self.__u_list:
                node = (node_u, node_v)
                if self.__has_node_values[node]:
                    (_, cell_y) = self.__node_to_cell(node)
            self.__left_labels[cell_y] = ""
            self.__left_labels[cell_y] += self.__row_labels[cell_y]
            self.__left_labels[cell_y] += self.__count_labels[0]


    def __init_node_coordinates(self):
        """Initialize the possible node coordinates."""

        (u_min, u_max) = (-self.__n, self.__n)
        (v_min, v_max) = (-self.__n, self.__n)
        self.__u_list = list(range(u_min, u_max + 1))
        self.__v_list = list(range(v_min, v_max + 1))


    def __init_node_directions(self):
        """Initialize all possible traveling directions from a node."""

        self.__node_directions = list()
        self.__node_directions.append((1, 0)) # e_u
        self.__node_directions.append((0, 1)) # e_v
        self.__node_directions.append((-1, 1)) # e_v - e_u
        self.__node_directions.append((-1, 0)) # -e_u
        self.__node_directions.append((0, -1)) # -e_v
        self.__node_directions.append((1, -1)) # e_u - e_v


    def __init_right_labels(self):
        """Initialize right side labels."""

        self.__right_labels = [None for cell_y in range(self.__ny + 1)]

        for node_v in self.__v_list:
            node_count = 0
            for node_u in self.__u_list:
                node = (node_u, node_v)
                if self.__has_node_values[node]:
                    (_, cell_y) = self.__node_to_cell(node)
                    node_count += 1
            self.__right_labels[cell_y] = ""
            self.__right_labels[cell_y] += self.__row_labels[cell_y]
            self.__right_labels[cell_y] += self.__count_labels[node_count - 1]


    def __init_row_labels(self):
        """Initialize labels indexing rows."""

        self.__row_labels = list(string.ascii_lowercase)
        self.__row_labels.sort()
        assert 2*self.__n + 1 <= len(self.__row_labels)
        self.__row_labels = self.__row_labels[0:2*self.__n + 1]
        self.__row_labels.reverse()


    def __init_table(self):
        """Initialize the table with neutral content in each cell."""

        self.__table = dict()
        self.__nx = 4*self.__n
        self.__ny = 2*self.__n

        for cell_x in range(self.__nx + 1):
            for cell_y in range(self.__ny + 1):
                cell = (cell_x, cell_y)
                self.__table[cell] = Hexmap.__CELL_SPACE

        for node_v in self.__v_list:
            for node_u in self.__u_list:
                node = (node_u, node_v)
                if self.__has_node_values[node]:
                    cell = self.__node_to_cell(node)
                    self.__table[cell] = Hexmap.__CELL_FILLER


    def __clear_node(self, node):
        """Clear the text at the given node."""
        self.__set_node(node, "")


    def clear_nodes(self):
        """Clear all nodes."""

        for label in self.__labels_to_nodes:
            self.clear_node_at_label(label)


    def clear_node_at_label(self, label):
        """Clear node text at the given label."""
        self.set_node_at_label(label, "")


    def get_first_adjacent_labels(self, label):
        """Return the labels of adjacent nodes
        to the node at the given label."""

        node = self.__labels_to_nodes[label]
        (node_u, node_v) = node

        first_nodes = list()

        for (delta_u, delta_v) in self.__node_directions:
            node_translated = (node_u + delta_u, node_v + delta_v)
            if self.__has_node(node_translated):
                first_nodes.append(self.__labels_from_nodes[node_translated])
            else:
                first_nodes.append(None)

        return first_nodes


    def get_labels(self):
        """Return the labels of all the hexmap nodes."""
        return self.__labels_to_nodes.keys()


    def get_node_labels_at_row(self, row_label):
        """Return the labels of all the hexmap nodes at a given row."""

        assert row_label in self.__row_labels
        row_index = self.__row_labels.index(row_label)
        node_v = self.__v_list[row_index]

        labels_at_row = list()

        for node_u in self.__u_list:
            node = (node_u, node_v)
            if self.__has_node_values[node]:
                label = self.__labels_from_nodes[node]
                labels_at_row.append(label)

        return labels_at_row


    def __get_node_at_label(self, label):
        """Return the node at the given label."""
        return self.__labels_to_nodes[label]


    def get_row_labels(self):
        """Return the row labels."""
        return self.__row_labels


    def get_second_adjacent_labels(self, label):
        """Return the labels of adjacent to adjacent nodes, in straight line,
        to the node at the given label."""

        node = self.__labels_to_nodes[label]
        (node_u, node_v) = node

        second_nodes = list()

        for (delta_u, delta_v) in self.__node_directions:
            node_translated = (node_u + 2*delta_u, node_v + 2*delta_v)
            if self.__has_node(node_translated):
                second_nodes.append(self.__labels_from_nodes[node_translated])
            else:
                second_nodes.append(None)

        return second_nodes


    def __has_node(self, node):
        """Is the given node inside this hexmap?"""

        self_has_node = False

        (node_u, node_v) = node

        if (node_u in self.__u_list) and (node_v in self.__v_list):
            self_has_node = self.__has_node_values[node]

        return self_has_node


    def print(self):
        """Print the hexmap using the table representation."""

        for cell_y in range(self.__ny + 1):
            line = self.__left_labels[cell_y] + Hexmap.__CELL_SPACE
            for cell_x in range(self.__nx + 1):
                cell = (cell_x, cell_y)
                line += self.__table[cell]
            line += Hexmap.__CELL_SPACE + self.__right_labels[cell_y]
            print(line)


    def __node_to_cell(self, node):
        """Convert a node of hexmap to a cell of table."""

        (node_u, node_v) = node
        cell = (2*self.__n + 2*node_u + node_v, self.__n - node_v)
        return cell


    def set_node_at_label(self, label, text):
        """Set the text of the node at the given label."""

        node = self.__labels_to_nodes[label]
        self.__set_node(node, text)


    def __set_node(self, node, text):
        """Set the text of the given node."""

        assert len(text) <= Hexmap.__CELL_SIZE
        cell = self.__node_to_cell(node)
        self.__table[cell] = text.rjust(Hexmap.__CELL_SIZE, Hexmap.__FILLER)



class Shape:
    """Capture the knowlege about Shape in JERSI."""

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
        """Does first shape beat second shape?"""

        assert fst_index in Shape.__indices
        assert snd_index in Shape.__indices
        return (fst_index, snd_index) in Shape.__beat_cases


    @staticmethod
    def beats_by_long_names(fst_long_name, snd_long_name):
        """Does first shape beat second shape?"""

        fst_index = Shape.__long_names.index(fst_long_name)
        snd_index = Shape.__long_names.index(snd_long_name)
        return Shape.beats(fst_index, snd_index)


    @staticmethod
    def beats_by_names(fst_name, snd_name):
        """Does first shape beat second shape?"""

        (fst_index, j) = (Shape.__names.index(fst_name), Shape.__names.index(snd_name))
        return Shape.beats(fst_index, j)


    @staticmethod
    def get_index(name):
        """Return the shape index for its name or long name."""

        name_uppered = name.upper()
        name_lowered = name.lower()

        index = None

        if name in Shape.__names:
            index = Shape.__names.index(name)

        elif name in Shape.__long_names:
            index = Shape.__long_names.index(name)

        elif name_uppered in Shape.__names:
            index = Shape.__names.index(name_uppered)

        elif name_lowered in Shape.__long_names:
            index = Shape.__long_names.index(name_lowered)

        assert index is not None

        return index


    @staticmethod
    def get_indices():
        """Return all the shape indices."""
        return Shape.__indices


    @staticmethod
    def get_long_name(index):
        """Return the long name associated to a given shape index."""
        return Shape.__long_names[index]


    @staticmethod
    def get_max_occurrences(index):
        """Return the maximum occurences of a given shape."""
        return Shape.__max_count[index]


    @staticmethod
    def get_name(index):
        """Return the name associated to a shape index."""
        return Shape.__names[index]


class Color:
    """Capture the knowlege about Color in JERSI."""

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


class Piece:
    """Capture knowlege about Piece in JERSI."""

    def __init__(self, shape, color):
        """Initialize a piece of a given shape and color,
        but not yet assigned to a node."""

        assert shape in Shape.get_indices()
        assert color in Color.get_indices()
        self.shape = shape
        self.color = color
        self.node = None


    def get_name(self):
        """Return the name of a piece."""

        name = Shape.get_name(self.shape)
        name_transformed = Color.get_transformer(self.color)(name)
        return name_transformed


    @staticmethod
    def make(shape_name, color_name):
        """Return a new piece from a given shape and color names."""

        shape = Shape.get_index(shape_name)
        color = Color.get_index(color_name)
        piece = Piece(shape, color)
        return piece


    @staticmethod
    def parse_shape_and_color(name):
        """Return the pair of indices (shape, color) piece the given name."""

        shape = Shape.get_index(name)
        color = Color.get_index(name)
        return (shape, color)


class Node:
    """Capture knowledge about Node in JERSI."""


    def __init__(self, label, graph):
        """Initialize a node at a given label for the given graph."""

        self.label = label
        self.graph = graph
        self.pieces = [None, None]
        self.first_adjacent_labels = None
        self.second_adjacent_labels = None


    def __deepcopy__(self, memo):
        """Customized deepcopy of a node: only the graph and pieces
        attributes are copied in depth."""

        new_one = Node(self.label, None)

        memo[id(self)] = new_one

        new_one.graph = copy.deepcopy(self.graph, memo)
        new_one.pieces = copy.deepcopy(self.pieces, memo)

        new_one.first_adjacent_labels = self.first_adjacent_labels
        new_one.second_adjacent_labels = self.second_adjacent_labels

        return new_one


    def get_top(self):
        """Return the top of the piece stack at this node."""

        if self.pieces[1] is not None:
            top = self.pieces[1]

        elif self.pieces[0] is not None:
            top = self.pieces[0]

        else:
            top = None

        return top


    def get_top_color(self):
        """Return the color of the top of the piece stack at this node."""

        if self.pieces[1] is not None:
            color = self.pieces[1].color

        elif self.pieces[0] is not None:
            color = self.pieces[0].color

        else:
            color = None

        return color


    def get_top_shape(self):
        """Return the shape of the top of the piece stack at this node."""

        if self.pieces[1] is not None:
            shape = self.pieces[1].shape

        elif self.pieces[0] is not None:
            shape = self.pieces[0].shape

        else:
            shape = None

        return shape


    def has_one_or_two_pieces(self):
        """Does this node have either one or two pieces?"""
        return self.pieces[0] is not None


    def has_two_pieces(self):
        """Does this node have two pieces?"""
        return self.pieces[1] is not None


    def has_zero_piece(self):
        """Does this node have no piece?"""
        return self.pieces[0] is None


    def has_zero_or_one_piece(self):
        """Does this node have either zero or one piece?"""
        return self.pieces[1] is None


    def move_one_piece(self, dst_node):
        """Move one piece (its top) from this node to a destinaiton node."""

        piece_captured = False
        kunti_captured = False

        assert dst_node is not None
        jersi_assert(dst_node.label in self.first_adjacent_labels,
                     "destination should stay at one segment from source")

        jersi_assert(self.has_one_or_two_pieces(),
                     "source should have one or two pieces")

        top = self.get_top()

        if dst_node.has_zero_piece():
            self.unset_piece(top)
            dst_node.set_piece(top)

        elif dst_node.get_top_color() == self.get_top_color():
            jersi_assert(dst_node.has_zero_or_one_piece(),
                         "source should have zero or one piece")

            self.unset_piece(top)
            dst_node.set_piece(top)

        else:
            jersi_assert(Shape.beats(self.get_top_shape(), dst_node.get_top_shape()),
                         "source should beats destination")

            piece_captured = True

            if dst_node.pieces[1] is not None:
                if dst_node.pieces[1].shape == Shape.kunti:
                    kunti_captured = True

            if dst_node.pieces[0] is not None:
                if dst_node.pieces[0].shape == Shape.kunti:
                    kunti_captured = True

            dst_node.unset_pieces()
            self.unset_piece(top)
            dst_node.set_piece(top)

        return (piece_captured, kunti_captured)


    def move_two_pieces(self, dst_node):
        """Move two pieces from this node to a destinaiton node."""

        piece_captured = False
        kunti_captured = False

        jersi_assert(self.has_two_pieces(), "source should have two pieces")
        assert dst_node is not None

        stepping_one_segment = dst_node.label in self.first_adjacent_labels
        stepping_two_segments = dst_node.label in self.second_adjacent_labels

        jersi_assert(stepping_one_segment or stepping_two_segments,
                     "destination should stay at one or two segments from source")

        if stepping_two_segments:
            dst_direction = self.second_adjacent_labels.index(dst_node.label)
            int_label = self.first_adjacent_labels[dst_direction]
            int_node = self.graph.nodes[int_label]
            jersi_assert(int_node.has_zero_piece(),
                         "path from source to destination should be free")

        if dst_node.has_zero_piece():
            pass

        else:
            jersi_assert(dst_node.get_top_color() != self.get_top_color(),
                         "source and destination colors should be different")

            jersi_assert(Shape.beats(self.get_top_shape(), dst_node.get_top_shape()),
                         "source should beat destination")

            piece_captured = True

            if dst_node.pieces[1] is not None:
                if dst_node.pieces[1].shape == Shape.kunti:
                    kunti_captured = True

            if dst_node.pieces[0] is not None:
                if dst_node.pieces[0].shape == Shape.kunti:
                    kunti_captured = True

            dst_node.unset_pieces()

        top = self.get_top()
        self.unset_piece(top)

        bottom = self.get_top()
        self.unset_piece(bottom)

        dst_node.set_piece(bottom)
        dst_node.set_piece(top)

        return (piece_captured, kunti_captured)


    def set_piece(self, piece):
        """Set a free piece to this node."""

        assert self.has_zero_or_one_piece()

        if self.pieces[0] is None:
            self.pieces[0] = piece
            piece.node = self

        else:
            jersi_assert(self.pieces[0].color == piece.color,
                         "stacked pieces should have same color")

            jersi_assert(self.pieces[0].shape != Shape.kunti,
                         "no piece should be stacked above kunti")

            self.pieces[1] = piece
            piece.node = self


    def unset_piece(self, piece):
        """Remove a given piece from this node."""

        assert self == piece.node

        if self.pieces[1] == piece:
            self.pieces[1] = None

        elif self.pieces[0] == piece:
            self.pieces[0] = None

        piece.node = None


    def unset_pieces(self):
        """Remove all pieces from this node."""

        if self.pieces[1] is not None:
            self.pieces[1].node = None
            self.pieces[1] = None

        if self.pieces[0] is not None:
            self.pieces[0].node = None
            self.pieces[0] = None


class Graph:
    """Graph is an abstraction of an Hexmap."""
    

    def __init__(self, hexmap):
        """Initialize a graph from a given hexmap."""

        self.hexmap = hexmap

        self.placement_labels = None
        self.nodes = None
        self.pieces = None

        self.__init_nodes()
        self.__init_pieces()
        self.__init_placement_labels()


    def __deepcopy__(self, memo):
        """Customized deepcopy of a node: only the nodes and pieces
        attributes are copied in depth."""

        cls = self.__class__
        new_one = cls.__new__(cls)
        memo[id(self)] = new_one

        new_one.hexmap = self.hexmap
        new_one.placement_labels = self.placement_labels

        new_one.nodes = copy.deepcopy(self.nodes, memo)
        new_one.pieces = copy.deepcopy(self.pieces, memo)

        return new_one


    def __init_nodes(self):
        """Initialize all nodes of the graph."""

        self.nodes = dict()

        for label in self.hexmap.get_labels():
            node = Node(label, self)
            node.first_adjacent_labels = self.hexmap.get_first_adjacent_labels(node.label)
            node.second_adjacent_labels = self.hexmap.get_second_adjacent_labels(node.label)
            self.nodes[label] = node


    def __init_pieces(self):
        """Initialize all pieces that could be place on the graph."""

        self.pieces = dict()
        for color in Color.get_indices():
            self.pieces[color] = dict()
            for shape in Shape.get_indices():
                self.pieces[color][shape] = list()
                shape_count = Shape.get_max_occurrences(shape)
                for _ in range(shape_count):
                    piece = Piece(shape, color)
                    self.pieces[color][shape].append(piece)


    def __init_placement_labels(self):
        """Initialize the valid nodes for the placement."""

        self.placement_labels = dict()

        self.placement_labels[0] = list()
        self.placement_labels[1] = list()

        row_labels = self.hexmap.get_row_labels()

        for row_label in row_labels[:2]:
            self.placement_labels[0].extend(self.hexmap.get_node_labels_at_row(row_label))

        for row_label in row_labels[-2:]:
            self.placement_labels[1].extend(self.hexmap.get_node_labels_at_row(row_label))


    def count_pieces_by_colors_and_shapes(self):
        """Count alive pieces by color and by shape."""

        count = dict()

        for color in Color.get_indices():
            count[color] = dict()
            for shape in Shape.get_indices():
                count[color][shape] = 0
                for piece in self.pieces[color][shape]:
                    if piece.node is not None:
                        count[color][shape] += 1
        return count


    def count_kuntis_by_colors(self):
        """Count alive kunti by color."""

        count = dict()

        for color in Color.get_indices():
            count[color] = 0
            for piece in self.pieces[color][Shape.kunti]:
                if piece.node is not None:
                    count[color] += 1

        return count


    def export_positions(self):
        """Export positions of alive pieces."""

        positions = dict()

        for color in Color.get_indices():
            for shape in Shape.get_indices():
                for piece in self.pieces[color][shape]:
                    if piece.node is not None:
                        node = piece.node
                        node_label = node.label
                        if node_label not in positions:
                            positions[node_label] = list()

                            if node.pieces[0] is not None:
                                positions[node_label].append(node.pieces[0].get_name())

                            if node.pieces[1] is not None:
                                positions[node_label].append(node.pieces[1].get_name())

        return positions


    def import_placement(self, positions):
        """Import and place pieces at given positions."""
        self.import_positions(positions, check_placement=True)


    def import_positions(self, positions, check_placement=False):
        """Import and set pieces at given positions.
        On option, check that positions are a valid placement.
        """

        self.unset_pieces()

        count = dict()
        for color in Color.get_indices():
            count[color] = dict()
            for shape in Shape.get_indices():
                count[color][shape] = 0

        for (node_label, piece_names) in positions.items():
            for piece_name in piece_names:
                (shape, color) = Piece.parse_shape_and_color(piece_name)
                instance = count[color][shape]
                piece = self.pieces[color][shape][instance]

                if check_placement:
                    self.place_piece(piece, node_label)
                else:
                    self.set_piece(piece, node_label)

                count[color][shape] += 1


    def move_one_piece(self, src_label, dst_label):
        """Move one piece from a source label to a destination label."""

        src_node = self.nodes[src_label]
        dst_node = self.nodes[dst_label]
        return src_node.move_one_piece(dst_node)


    def move_two_pieces(self, src_label, dst_label):
        """Move two pieces from a source label to a destination label."""

        src_node = self.nodes[src_label]
        dst_node = self.nodes[dst_label]
        return src_node.move_two_pieces(dst_node)


    def print(self):
        """Print the graph using the table managed by the hexmap."""

        self.__set_hexmap_nodes()
        self.hexmap.print()


    def __set_hexmap_nodes(self):
        """Set the cells of the hexmap."""

        self.hexmap.clear_nodes()

        for node in self.nodes.values():
            cell_text = ""

            if node.pieces[0] is not None:
                cell_text = node.pieces[0].get_name() + cell_text

            if node.pieces[1] is not None:
                cell_text = node.pieces[1].get_name() + cell_text

            self.hexmap.set_node_at_label(node.label, cell_text)


    def place_piece(self, piece, dst_label):
        """Place a piece at a destination label."""

        jersi_assert(dst_label in self.placement_labels[piece.color],
                     "%s is not a placement position for the %s color" %
                     (dst_label, Color.get_name(piece.color)))

        self.set_piece(piece, dst_label)


    def place_pieces_at_random_positions(self):
        """Place all the pieces at random positions."""

        self.unset_pieces()

        blue = Color.blue
        red = Color.red
        kunti = Shape.kunti

        blue_pieces_wo_kunti = list()
        blue_kunti = None
        for shape in Shape.get_indices():
            if shape != kunti:
                blue_pieces_wo_kunti.extend(self.pieces[blue][shape])
            else:
                blue_kunti = self.pieces[blue][shape][0]

        red_pieces_wo_kunti = list()
        red_kunti = None
        for shape in Shape.get_indices():
            if shape != kunti:
                red_pieces_wo_kunti.extend(self.pieces[red][shape])
            else:
                red_kunti = self.pieces[red][shape][0]

        random.shuffle(blue_pieces_wo_kunti)
        random.shuffle(red_pieces_wo_kunti)

        # set blue pieces

        self.place_piece(blue_pieces_wo_kunti[0], "b1")
        self.place_piece(blue_pieces_wo_kunti[1], "b2")
        self.place_piece(blue_pieces_wo_kunti[2], "b3")
        self.place_piece(blue_pieces_wo_kunti[3], "b4")
        self.place_piece(blue_pieces_wo_kunti[4], "b5")
        self.place_piece(blue_pieces_wo_kunti[5], "b6")

        self.place_piece(blue_pieces_wo_kunti[6], "a1")

        self.place_piece(blue_pieces_wo_kunti[7], "a2")
        self.place_piece(blue_pieces_wo_kunti[8], "a2")

        self.place_piece(blue_kunti, "a3")

        self.place_piece(blue_pieces_wo_kunti[9], "a4")
        self.place_piece(blue_pieces_wo_kunti[10], "a4")

        self.place_piece(blue_pieces_wo_kunti[11], "a5")

        # set red pieces

        self.place_piece(red_pieces_wo_kunti[0], "h6")
        self.place_piece(red_pieces_wo_kunti[1], "h5")
        self.place_piece(red_pieces_wo_kunti[2], "h4")
        self.place_piece(red_pieces_wo_kunti[3], "h3")
        self.place_piece(red_pieces_wo_kunti[4], "h2")
        self.place_piece(red_pieces_wo_kunti[5], "h1")

        self.place_piece(red_pieces_wo_kunti[6], "i5")

        self.place_piece(red_pieces_wo_kunti[7], "i4")
        self.place_piece(red_pieces_wo_kunti[8], "i4")

        self.place_piece(red_kunti, "i3")

        self.place_piece(red_pieces_wo_kunti[9], "i2")
        self.place_piece(red_pieces_wo_kunti[10], "i2")

        self.place_piece(red_pieces_wo_kunti[11], "i1")


    def place_pieces_at_standard_positions(self):
        """Place all the pieces at standard/symmetric positions."""

        self.unset_pieces()

        blue = Color.blue
        red = Color.red

        kunti = Shape.kunti
        cukla = Shape.cukla
        kurfa = Shape.kurfa
        kuctai = Shape.kuctai

        # set blue pieces

        self.place_piece(self.pieces[blue][cukla][0], "b1")
        self.place_piece(self.pieces[blue][kurfa][0], "b2")
        self.place_piece(self.pieces[blue][kuctai][0], "b3")
        self.place_piece(self.pieces[blue][cukla][1], "b4")
        self.place_piece(self.pieces[blue][kurfa][1], "b5")
        self.place_piece(self.pieces[blue][kuctai][1], "b6")

        self.place_piece(self.pieces[blue][kuctai][2], "a1")

        self.place_piece(self.pieces[blue][kurfa][2], "a2")
        self.place_piece(self.pieces[blue][cukla][2], "a2")

        self.place_piece(self.pieces[blue][kunti][0], "a3")

        self.place_piece(self.pieces[blue][kurfa][3], "a4")
        self.place_piece(self.pieces[blue][kuctai][3], "a4")

        self.place_piece(self.pieces[blue][cukla][3], "a5")

        # set red pieces

        self.place_piece(self.pieces[red][cukla][0], "h6")
        self.place_piece(self.pieces[red][kurfa][0], "h5")
        self.place_piece(self.pieces[red][kuctai][0], "h4")
        self.place_piece(self.pieces[red][cukla][1], "h3")
        self.place_piece(self.pieces[red][kurfa][1], "h2")
        self.place_piece(self.pieces[red][kuctai][1], "h1")

        self.place_piece(self.pieces[red][kuctai][2], "i5")

        self.place_piece(self.pieces[red][kurfa][2], "i4")
        self.place_piece(self.pieces[red][cukla][2], "i4")

        self.place_piece(self.pieces[red][kunti][0], "i3")

        self.place_piece(self.pieces[red][kurfa][3], "i2")
        self.place_piece(self.pieces[red][kuctai][3], "i2")

        self.place_piece(self.pieces[red][cukla][3], "i1")


    def set_piece(self, piece, dst_label):
        """Set a piece at a destination label."""

        dst_node = self.nodes[dst_label]
        dst_node.set_piece(piece)


    def unset_pieces(self):
        """Unset all pieces out of the graph."""

        for node in self.nodes.values():
            node.unset_pieces()


class Game:
    """Provide services for playing, saving and reloading a game of JERSI.
    Manage JERSI rule related to the dynamics like the alternance rule
    between the two players and the end of game.
    """


    def __init__(self):
        """Initialize the Game with an hexmap.
        Propose a to start witj a standard placement.
        """

        self.graph = None
        self.placement = None
        self.history = None
        self.game_over = None
        self.placement_over = None
        self.last_count = None
        self.move_count = None
        self.score = None

        self.graph = Graph(hexmap=Hexmap(5))
        self.init_game()
        self.new_standard_game()


    def __deepcopy__(self, memo):
        """Customized deepcopy of a game: only the graph, placement and history
        attributes are copied in depth."""

        cls = self.__class__
        new_one = cls.__new__(cls)
        memo[id(self)] = new_one

        new_one.__dict__.update(self.__dict__)

        new_one.graph = copy.deepcopy(self.graph, memo)
        new_one.placement = copy.copy(self.placement)
        new_one.history = copy.copy(self.history)

        return new_one


    def init_game(self):
        """Initialize or re-initialize the game."""

        self.graph.unset_pieces()

        self.placement = dict()
        self.history = list()
        self.game_over = False
        self.placement_over = False
        self.last_count = None
        self.move_count = 1

        self.score = dict()
        for color in sorted(Shape.get_indices()):
            self.score[color] = 0


    def new_free_game(self):
        """Initialize the game with a free placement
        i.e. no piece yet placed."""

        self.init_game()

        print()
        print("new free game")
        self.graph.print()
        self.print_status()


    def new_random_game(self):
        """Initialize the game with a random placement."""

        self.init_game()
        self.graph.place_pieces_at_random_positions()
        self.placement = self.graph.export_positions()
        self.placement_over = True

        print()
        print("new random game")
        self.graph.print()
        self.print_status()


    def new_standard_game(self):
        """Initialize the game with a standard/symmetric placement."""

        self.init_game()
        self.graph.place_pieces_at_standard_positions()
        self.placement = self.graph.export_positions()
        self.placement_over = True

        print()
        print("new standard game")
        self.graph.print()
        self.print_status()


    def parse_and_play_instruction(self, instruction):
        """Parse and play an instruction."""

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
        """Parse an instruction and update the given positions and moves."""

        instruction_validated = True

        rule_set_piece = re.compile(
            r"^(?P<node_label>\w{2}):(?P<piece_name>\w)$")

        rule_move_one_piece = re.compile(
            r"^(?P<src_label>\w{2})-(?P<dst_label>\w{2})!{0,2}$")

        rule_move_two_pieces = re.compile(
            r"^(?P<src_label>\w{2})=(?P<dst_label>\w{2})!{0,2}$")

        rule_move_one_then_two_pieces = re.compile(
            r"^(?P<src_label>\w{2})-(?P<int_label>\w{2})!{0,1}=(?P<dst_label>\w{2})!{0,2}$")

        rule_move_two_then_one_pieces = re.compile(
            r"^(?P<src_label>\w{2})=(?P<int_label>\w{2})!{0,1}-(?P<dst_label>\w{2})!{0,2}$")

        match_set_piece = rule_set_piece.match(instruction)
        match_move_one_piece = rule_move_one_piece.match(instruction)
        match_move_two_pieces = rule_move_two_pieces.match(instruction)
        match_move_one_then_two_pieces = rule_move_one_then_two_pieces.match(instruction)
        match_move_two_then_one_pieces = rule_move_two_then_one_pieces.match(instruction)

        if match_set_piece:
            node_label = match_set_piece.group("node_label")
            piece_name = match_set_piece.group("piece_name")
            if node_label not in positions:
                positions[node_label] = list()
            positions[node_label].append(piece_name)

        elif match_move_one_piece:
            src_label = match_move_one_piece.group("src_label")
            dst_label = match_move_one_piece.group("dst_label")
            moves.append([(1, src_label, dst_label)])

        elif match_move_two_pieces:
            src_label = match_move_two_pieces.group("src_label")
            dst_label = match_move_two_pieces.group("dst_label")
            moves.append([(2, src_label, dst_label)])

        elif match_move_one_then_two_pieces:
            src_label = match_move_one_then_two_pieces.group("src_label")
            int_label = match_move_one_then_two_pieces.group("int_label")
            dst_label = match_move_one_then_two_pieces.group("dst_label")
            moves.append([(1, src_label, int_label), (2, int_label, dst_label)])

        elif match_move_two_then_one_pieces:
            src_label = match_move_two_then_one_pieces.group("src_label")
            int_label = match_move_two_then_one_pieces.group("int_label")
            dst_label = match_move_two_then_one_pieces.group("dst_label")
            moves.append([(2, src_label, int_label), (1, int_label, dst_label)])

        else:
            print("syntax error in instruction '%s'" % instruction)
            instruction_validated = False

        return instruction_validated


    def play_moves(self, moves):
        """Play the given moves."""

        play_validated = True

        try:
            for move_steps in moves:

                jersi_assert(not self.game_over, "game should be not over")
                jersi_assert(self.placement_over, "placement should be over")

                move_color = (self.move_count - 1) % Color.get_count()
                step_count = 1
                annotated_steps = list()

                for (piece_count, src_label, dst_label) in move_steps:

                    jersi_assert(src_label in self.graph.nodes.keys(),
                                 "source label should be valid")

                    jersi_assert(dst_label in self.graph.nodes.keys(),
                                 "destination label should be valid")

                    src_node = self.graph.nodes[src_label]

                    jersi_assert(src_node.has_one_or_two_pieces(),
                                 "source should have one or two pieces")

                    jersi_assert(src_node.get_top_color() == move_color,
                                 "moved color should be valid")

                    if piece_count == 1:
                        (piece_captured,
                         kunti_captured) = self.graph.move_one_piece(src_label, dst_label)

                    elif piece_count == 2:
                        (piece_captured,
                         kunti_captured) = self.graph.move_two_pieces(src_label, dst_label)

                    else:
                        assert False

                    annotated_steps.append((piece_count, src_label, dst_label,
                                            piece_captured, kunti_captured))
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
        """Play the given positions as a placement."""

        play_validated = True

        try:
            assert len(positions) == 1
            [(node_label, piece_names)] = positions.items()

            assert len(piece_names) == 1
            piece_name = piece_names[0]

            jersi_assert(not self.game_over, "game should be not over")
            jersi_assert(not self.placement_over, "placement should be not over")

            (shape, color) = Piece.parse_shape_and_color(piece_name)

            move_color = (self.move_count - 1) % Color.get_count()
            jersi_assert(color == move_color, "moved color should be valid")

            piece_count = self.graph.count_pieces_by_colors_and_shapes()
            instance = piece_count[color][shape]
            jersi_assert(instance < Shape.get_max_occurrences(shape), "shape should be available")

            piece = self.graph.pieces[color][shape][instance]
            self.graph.place_piece(piece, node_label)

            self.move_count += 1

            has_available_piece = False
            for color in piece_count.keys():
                for shape in piece_count[color].keys():
                    if piece_count[color][shape] < Shape.get_max_occurrences(shape):
                        has_available_piece = True
                        break

            if not has_available_piece:
                self.placement_over = False

            if self.placement_over:
                self.placement = self.graph.export_positions()

        except(JersiError) as jersi_assertion_error:
            print("assertion failed: %s !!!" % jersi_assertion_error.message)
            play_validated = False

        return play_validated


    @staticmethod
    def print_help():
        """Print help about the commands."""

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
        """Print the history of moves. Placement is not printed."""

        print()
        print("move history:")
        for line in Game.textify_history(self.history):
            print(line)


    def print_status(self):
        """Print the status of the game: turn, score, count of pieces."""

        piece_count = self.graph.count_pieces_by_colors_and_shapes()

        if self.game_over:
            text = "game over"

            for color in sorted(piece_count.keys()):
                text += " / %s %d" % (Color.get_name(color), self.score[color])

        else:
            move_color = (self.move_count - 1) % Color.get_count()
            move_color_name = Color.get_name(move_color)
            text = "%s turn" % move_color_name

            text += " / move %d" % self.move_count

            if self.last_count is not None:
                text += " / last %d moves" % self.last_count

        for color in sorted(piece_count.keys()):
            text += " / " + Color.get_name(color)
            color_transformer = Color.get_transformer(color)
            for shape in sorted(piece_count[color].keys()):
                text += " %s=%d" % (color_transformer(Shape.get_name(shape)),
                                    piece_count[color][shape])

        print()
        print(text)


    def read_game(self, file_path):
        """Read a game from a file: set initial positions of pieces (placement)
        and play read moves."""

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
            self.init_game()

            playing_validated = True

            try:
                self.graph.import_placement(positions)
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
                self.graph.print()
                self.print_status()

            else:
                self.restore_game(saved_game)


    def read_positions(self, file_path):
        """Remove all pieces from the graph and set pieces only
        at the read positions from the file."""

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
            self.init_game()

            importing_validated = True
            try:
                jersi_assert(len(moves) == 0, "file should not have moves")

                self.graph.import_positions(positions)
                self.placement_over = True
                self.placement = self.graph.export_positions()

            except(JersiError) as jersi_assertion_error:
                print("assertion failed: %s !!!" % jersi_assertion_error.message)
                importing_validated = False

            if importing_validated:
                print()
                print("positions from file '%s'" % file_path)
                self.graph.print()
                self.print_status()

            else:
                self.restore_game(saved_game)


    def restore_game(self, saved_game):
        """Restore all saved attributes of the game."""

        self.__dict__.update(saved_game.__dict__)


    def run(self):
        """Run all entered commands until the command for quitting."""

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
                        self.graph.print()
                        self.print_status()
                else:
                    print("turn syntax error !!!")


    def save_game(self):
        """Save all atributes of the game."""

        saved_game = copy.deepcopy(self)
        return saved_game


    @staticmethod
    def stringify_move(move_steps):
        """Convert all steps of the given move as a string."""

        move_text = ""

        for (step_index, step) in enumerate(move_steps):

            if len(step) == 5:
                (piece_count, src_label, dst_label,
                 piece_captured, kunti_captured) = step

            elif len(step) == 3:
                (piece_count, src_label, dst_label,
                 piece_captured, kunti_captured) = (*step, False, False)

            else:
                assert False

            step_text = ""

            if step_index == 0:
                step_text += src_label

            if piece_count == 1:
                step_text += "-"

            elif piece_count == 2:
                step_text += "="

            step_text += dst_label

            if piece_captured:
                step_text += "!"

            if kunti_captured:
                step_text += "!"

            move_text += step_text

        return move_text


    @staticmethod
    def textify_history(history):
        """Convert all played moves as a list of string."""

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
        """Convert all given piece positions as a list of string."""

        lines = list()

        start_index = 0

        for (node_label, piece_names) in  sorted(positions.items()):

            for piece_name in piece_names:

                piece_text = "%s:%s" % (node_label, piece_name)

                if start_index % 2 == 0:
                    lines.append(piece_text)
                else:
                    lines[-1] += " "*4 + piece_text

                start_index += 1

        return lines


    def update_end_conditions(self):
        """Determine conditions for ending a game."""

        piece_count = self.graph.count_pieces_by_colors_and_shapes()

        for color in piece_count.keys():
            self.score[color] = 1
            if piece_count[color][Shape.kunti] == 0:
                self.game_over = True
                self.score[color] = 0

        if not self.game_over:

            if self.last_count is None:
                for color in piece_count.keys():
                    for shape in piece_count[color].keys():
                        if piece_count[color][shape] == 0:
                            self.last_count = 20
            else:
                self.last_count -= 1
                if self.last_count == 0:
                    self.game_over = True


    def write_game(self, file_path):
        """Write a game into a file: set initial positions of pieces (placement)
        and play read moves."""

        file_stream = open(os.path.join(os.curdir, file_path), 'w')

        for line in Game.textify_positions(self.placement):
            file_stream.write("%s\n" % line)

        file_stream.write("\n")

        for line in Game.textify_history(self.history):
            file_stream.write("%s\n" % line)

        file_stream.close()

        print("saving game in file '%s' done" % file_path)


    def write_positions(self, file_path):
        """Write into a file the actual positions of pieces."""

        file_stream = open(os.path.join(os.curdir, file_path), 'w')

        for line in Game.textify_positions(self.graph.export_positions()):
            file_stream.write("%s\n" % line)

        file_stream.close()

        print("saving positions in file '%s' done" % file_path)


def main():
    """Start JERSI."""

    print(_COPYRIGHT_AND_LICENSE)
    my_game = Game()
    my_game.run()


if __name__ == "__main__":
    main()
