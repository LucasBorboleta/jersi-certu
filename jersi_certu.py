#!/usr/bin/en python3

"""Jersi-certu is a Python3 program for playing the jersi abstract game."""

# -*- coding: utf-8 -*-

import ast
import copy
import math
import random
import re
import string
import datetime

#import cProfile


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
    Captures the geometrical knowledge about the hexagonal map of JERSI.
    The Hexmap does not know about Piece having Shape and Color.

    An hexmap is made of nodes. Each node can be set with a text.
    For printing the hexmap, an auxilliary table is used,
    which is made of cells distributed in rows and columns.

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

    The nodes of an hexmap are described using an oblique coordinates system :
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
        the number of nodes per hexmap side."""

        self.__nodes_per_side = nodes_per_side
        self.__n = self.__nodes_per_side - 1

        # Many information are computed once and memorized in attributes
        # in order to accelerate further public queries.
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


    def compute_distance(self, fst_label, snd_label):
        """Compute the manhattan distance between two labels."""

        distance = None

        (fst_u, fst_v) = self.__labels_to_nodes[fst_label]
        (snd_u, snd_v) = self.__labels_to_nodes[snd_label]

        delta_u = fst_u - snd_u
        delta_v = fst_v - snd_v

        if math.copysign(1., delta_u) == math.copysign(1., delta_v):
            distance = math.fabs(delta_u + delta_v)
        else:
            distance = max(math.fabs(delta_u), math.fabs(delta_v))

        return distance


    def get_labels_at_one_link(self, label):
        """Return the labels of nodes reachable by a translation of
        one link. The returned list is indexed by the translating directions.
        If in a given direction the translation moves outside the
        Hexmap, then None is inserted in the list instead of the
        reached label."""

        node = self.__labels_to_nodes[label]
        (node_u, node_v) = node

        labels = list()

        for (delta_u, delta_v) in self.__node_directions:
            node_translated = (node_u + delta_u, node_v + delta_v)
            if self.__has_node(node_translated):
                labels.append(self.__labels_from_nodes[node_translated])
            else:
                labels.append(None)

        return labels


    def get_labels(self):
        """Return the labels of all the hexmap nodes."""
        return self.__labels_to_nodes.keys()


    def get_labels_at_row(self, row_label):
        """Return the labels of all the hexmap nodes at a given row."""

        assert row_label in self.__row_labels
        row_index = self.__row_labels.index(row_label)
        node_v = self.__v_list[row_index]

        labels = list()

        for node_u in self.__u_list:
            node = (node_u, node_v)
            if self.__has_node_values[node]:
                node_label = self.__labels_from_nodes[node]
                labels.append(node_label)

        return labels


    def __get_node_at_label(self, label):
        """Return the node at the given label."""
        return self.__labels_to_nodes[label]


    def get_row_labels(self):
        """Return the row labels."""
        return self.__row_labels


    def get_labels_at_two_links(self, label):
        """Return the labels of nodes reachable by a translation of
        two links. The returned list is indexed by the translating directions.
        If in a given direction the translation moves outside the
        Hexmap, then None is inserted in the list instead of the
        reached label."""

        node = self.__labels_to_nodes[label]
        (node_u, node_v) = node

        labels = list()

        for (delta_u, delta_v) in self.__node_directions:
            node_translated = (node_u + 2*delta_u, node_v + 2*delta_v)
            if self.__has_node(node_translated):
                labels.append(self.__labels_from_nodes[node_translated])
            else:
                labels.append(None)

        return labels


    def __has_node(self, node):
        """Is the given node inside this hexmap?"""

        self_has_node = False
        if node in self.__has_node_values:
            self_has_node = self.__has_node_values[node]
        return self_has_node


    def print_hexmap(self):
        """Print the hexmap using the table representation."""

        print()
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
    """Capture knowledge about a Node in JERSI.
    A Node hosts stacked Pieces.
    """


    def __init__(self, label):
        """Initialize a node at a given label."""

        self.label = label
        self.pieces = [None, None]
        self.nodes_at_one_link = list()
        self.nodes_at_two_links = list()


    def get_top(self):
        """Return the top of the stacked pieces at this node."""

        if self.pieces[1] is not None:
            top = self.pieces[1]

        elif self.pieces[0] is not None:
            top = self.pieces[0]

        else:
            top = None

        return top


    def get_top_color(self):
        """Return the color of the top of the stacked pieces at this node."""

        top = self.get_top()

        if top is not None:
            color = top.color
        else:
            color = None

        return color


    def get_top_shape(self):
        """Return the shape of the top of the stacked pieces at this node."""

        top = self.get_top()

        if top is not None:
            shape = top.shape
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


    def init_nodes_at_one_link(self, nodes_at_one_link):
        """Initialize nodes at one link."""
        self.nodes_at_one_link = nodes_at_one_link


    def init_nodes_at_two_links(self, nodes_at_two_links):
        """Initialize nodes at two linsk."""
        self.nodes_at_two_links = nodes_at_two_links


    def move_one_piece(self, dst_node, undo_list):
        """Move one piece from this node to the destination node."""

        piece_captured = False
        kunti_captured = False

        assert dst_node is not None
        jersi_assert(dst_node in self.nodes_at_one_link,
                     "destination should be at one link from source")

        jersi_assert(self.has_one_or_two_pieces(),
                     "source should have one or two pieces")

        top = self.get_top()

        if dst_node.has_zero_piece():

            self.unset_piece(top)
            undo_list.append((lambda node, piece: lambda: node.set_piece(piece))(self, top))

            dst_node.set_piece(top)
            undo_list.append((lambda node, piece: lambda: node.unset_piece(piece))(dst_node, top))

        elif dst_node.get_top_color() == self.get_top_color():
            jersi_assert(dst_node.has_zero_or_one_piece(),
                         "source should have zero or one piece")

            self.unset_piece(top)
            undo_list.append((lambda node, piece: lambda: node.set_piece(piece))(self, top))

            dst_node.set_piece(top)
            undo_list.append((lambda node, piece: lambda: node.unset_piece(piece))(dst_node, top))

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

            if dst_node.pieces[1] is not None:
                undo_list.append((lambda node, piece:
                                  lambda: node.set_piece(piece))(dst_node, dst_node.pieces[1]))

            if dst_node.pieces[0] is not None:
                undo_list.append((lambda node, piece:
                                  lambda: node.set_piece(piece))(dst_node, dst_node.pieces[0]))

            dst_node.unset_pieces()

            self.unset_piece(top)
            undo_list.append((lambda node, piece:
                              lambda: node.set_piece(piece))(self, top))

            dst_node.set_piece(top)
            undo_list.append((lambda node, piece:
                              lambda: node.unset_piece(piece))(dst_node, top))

        return (piece_captured, kunti_captured)


    def move_two_pieces(self, dst_node, undo_list):
        """Move two pieces from this node to the destination node."""

        piece_captured = False
        kunti_captured = False

        jersi_assert(self.has_two_pieces(), "source should have two pieces")
        assert dst_node is not None

        traveling_one_link = dst_node in self.nodes_at_one_link
        traveling_two_links = dst_node in self.nodes_at_two_links

        jersi_assert(traveling_one_link or traveling_two_links,
                     "destination should be at one or two links from source")

        if traveling_two_links:
            dst_direction = self.nodes_at_two_links.index(dst_node)
            int_node = self.nodes_at_one_link[dst_direction]
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

            if dst_node.pieces[1] is not None:
                undo_list.append((lambda node, piece:
                                  lambda: node.set_piece(piece))(dst_node, dst_node.pieces[1]))

            if dst_node.pieces[0] is not None:
                undo_list.append((lambda node, piece:
                                  lambda: node.set_piece(piece))(dst_node, dst_node.pieces[0]))

            dst_node.unset_pieces()

        top = self.get_top()
        self.unset_piece(top)
        undo_list.append((lambda node, piece: lambda: node.set_piece(piece))(self, top))

        bottom = self.get_top()
        self.unset_piece(bottom)
        undo_list.append((lambda node, piece: lambda: node.set_piece(piece))(self, bottom))

        dst_node.set_piece(bottom)
        undo_list.append((lambda node, piece: lambda: node.unset_piece(piece))(dst_node, bottom))

        dst_node.set_piece(top)
        undo_list.append((lambda node, piece: lambda: node.unset_piece(piece))(dst_node, top))

        return (piece_captured, kunti_captured)


    def set_piece(self, piece):
        """Set a free piece to this node."""

        jersi_assert(self.has_zero_or_one_piece(),
                     "the piece should be set on a node having zero or one piece")

        jersi_assert(piece.node is None, "the set piece should be free.")

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


class Absmap:
    """Absmap is an abstraction of the hexagonal map of JERSI.
    Absmap relies on Hexmap for geometrial knowledge. But Unlike Hexmap,
    Absmap knows some rules of JERSI about Nodes and Pieces.
    """


    def __init__(self, hexmap):
        """Initialize an absmap from a given hexmap."""

        self.hexmap = hexmap

        self.placement_labels = None
        self.nodes = None
        self.pieces = None

        self.__init_nodes()
        self.__init_pieces()
        self.__init_placement_labels()


    def __deepcopy__(self, memo):
        """Customized deepcopy of an Absmap."""

        cls = self.__class__
        new_one = cls.__new__(cls)
        memo[id(self)] = new_one
        new_one.__dict__.update(self.__dict__)

        new_one.nodes = copy.deepcopy(self.nodes, memo)
        new_one.pieces = copy.deepcopy(self.pieces, memo)

        return new_one


    def __init_nodes(self):
        """Initialize all nodes of the absmap."""

        self.nodes = dict()

        # Create all nodes of the absmap
        for label in self.hexmap.get_labels():
            node = Node(label)
            self.nodes[label] = node

        # Initialize links between nodes
        for label in self.nodes:

            nodes_at_one_link = list()
            for dst_label in self.hexmap.get_labels_at_one_link(label):
                if dst_label is not None:
                    nodes_at_one_link.append(self.nodes[dst_label])
                else:
                    nodes_at_one_link.append(None)

            nodes_at_two_links = list()
            for dst_label in self.hexmap.get_labels_at_two_links(label):
                if dst_label is not None:
                    nodes_at_two_links.append(self.nodes[dst_label])
                else:
                    nodes_at_two_links.append(None)

            node = self.nodes[label]
            node.init_nodes_at_one_link(nodes_at_one_link)
            node.init_nodes_at_two_links(nodes_at_two_links)


    def __init_pieces(self):
        """Initialize all pieces that could be place on the absmap."""

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
            self.placement_labels[0].extend(self.hexmap.get_labels_at_row(row_label))

        for row_label in row_labels[-2:]:
            self.placement_labels[1].extend(self.hexmap.get_labels_at_row(row_label))


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


    def get_pieces_by_colors(self):
        """Return alive pieces by color."""

        pieces = dict()

        for color in Color.get_indices():
            pieces[color] = list()
            for shape in Shape.get_indices():
                for piece in self.pieces[color][shape]:
                    if piece.node is not None:
                        pieces[color].append(piece)
        return pieces


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


    def move_one_piece(self, src_label, dst_label, undo_list):
        """Move one piece from a source label to a destination label."""

        src_node = self.nodes[src_label]
        dst_node = self.nodes[dst_label]
        return src_node.move_one_piece(dst_node, undo_list)


    def move_two_pieces(self, src_label, dst_label, undo_list):
        """Move two pieces from a source label to a destination label."""

        src_node = self.nodes[src_label]
        dst_node = self.nodes[dst_label]
        return src_node.move_two_pieces(dst_node, undo_list)


    def print_absmap(self):
        """Print the absmap using the table managed by the hexmap."""

        self.__set_hexmap_nodes()
        self.hexmap.print_hexmap()


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
        """Unset all pieces out of the absmap."""

        for node in self.nodes.values():
            node.unset_pieces()


class Game:
    """Manage JERSI rule related to the dynamics like the alternance rule
    between the two players and the end of game."""


    def __init__(self):
        """Initialize the Game with an hexmap.
        Propose a to start witj a standard placement.
        """

        self.absmap = None
        self.placement = None
        self.history = None
        self.game_over = None
        self.placement_over = None
        self.last_count = None
        self.move_count = None
        self.score = None
        self.time = None

        self.absmap = Absmap(hexmap=Hexmap(5))
        self.__init_game()
        self.new_standard_game()


    def __deepcopy__(self, memo):
        """Customized deepcopy of a Game."""

        cls = self.__class__
        new_one = cls.__new__(cls)
        memo[id(self)] = new_one
        new_one.__dict__.update(self.__dict__)

        new_one.absmap = copy.deepcopy(self.absmap, memo)
        new_one.placement = copy.copy(self.placement)
        new_one.history = copy.copy(self.history)

        return new_one


    def __can_move(self, color):
        """Can the given color move some piece?"""

        can = False
        for src_node in self.__find_nodes(color):
            for dst_node in src_node.nodes_at_one_link:
                if dst_node is not None:
                    if dst_node.has_zero_piece():
                        can = True
                        break

        if not can:
            move_list = self.find_moves(color, find_one=True)
            can = bool(move_list)

        return can


    def find_moves(self, color, find_one=False):
        """Find possible moves for the given color.
        If find_one then just return the first found move."""

        (move_list, _) = self.__find_moves_and_games(color, find_one)
        return move_list


    def find_moves_and_games(self, color, find_one=False):
        """Find possible moves and associated games for the given color.
        If find_one then just return the first found move and associated game."""

        (move_list, game_list) = self.__find_moves_and_games(color, find_one, do_save_games=True)
        move_game_list = list(zip(move_list, game_list))
        return move_game_list


    def __find_moves_and_games(self, color, find_one=False, do_save_games=False):
        """Find possible moves for the given color, and optionaly return associated games.
        If find_one then just return the first found move,and optionnaly first associated game."""

        move_list = list()

        if do_save_games:
            game_list = list()
        else:
            game_list = None

        for src_node in self.__find_nodes(color):

            for dst_node in src_node.nodes_at_one_link:
                if dst_node is not None:
                    move_steps = list()
                    move_steps.append([(1, src_node.label, dst_node.label)])

                    (play_validated, tried_game) = self.__play_moves(move_steps,
                                                                     do_try=True,
                                                                     do_save_try=do_save_games)
                    if play_validated:
                        move_list.extend(move_steps)

                        if do_save_games:
                            game_list.append(tried_game)

                        if find_one:
                            return (move_list, game_list)

                        for fin_node in dst_node.nodes_at_two_links:
                            if fin_node is not None:
                                move_steps = list()
                                move_steps.append([(1, src_node.label, dst_node.label),
                                                   (2, dst_node.label, fin_node.label)])

                                (play_validated, tried_game) = self.__play_moves(move_steps,
                                                                                 do_try=True,
                                                                                 do_save_try=do_save_games)
                                if play_validated:
                                    move_list.extend(move_steps)

                                    if do_save_games:
                                        game_list.append(tried_game)


            for dst_node in src_node.nodes_at_two_links:
                if dst_node is not None:
                    move_steps = list()
                    move_steps.append([(2, src_node.label, dst_node.label)])

                    (play_validated, tried_game) = self.__play_moves(move_steps,
                                                                     do_try=True,
                                                                     do_save_try=do_save_games)
                    if play_validated:
                        move_list.extend(move_steps)

                        if do_save_games:
                            game_list.append(tried_game)

                        if find_one:
                            return (move_list, game_list)

                        for fin_node in dst_node.nodes_at_one_link:
                            if fin_node is not None:
                                move_steps = list()
                                move_steps.append([(2, src_node.label, dst_node.label),
                                                   (1, dst_node.label, fin_node.label)])

                                (play_validated, tried_game) = self.__play_moves(move_steps,
                                                                                 do_try=True,
                                                                                 do_save_try=do_save_games)
                                if play_validated:
                                    move_list.extend(move_steps)

                                    if do_save_games:
                                        game_list.append(tried_game)

        return (move_list, game_list)


    def __find_nodes(self, color):
        """Find nodes with pieces of the given color."""

        for shape in Shape.get_indices():
            for piece in self.absmap.pieces[color][shape]:
                if piece.node is not None:
                    node = piece.node
                    if node.get_top() == piece:
                        yield node


    def get_move_color(self):
        """Return the color of tne actual player."""

        if not self.game_over:
            move_color = (self.move_count - 1) % Color.get_count()
        else:
            move_color = None

        return move_color


    def __init_game(self):
        """Initialize or re-initialize the game."""

        self.absmap.unset_pieces()

        self.placement = dict()
        self.history = list()
        self.game_over = False
        self.placement_over = False
        self.last_count = None
        self.move_count = 1
        self.time = datetime.datetime.now()

        self.score = dict()
        for color in sorted(Shape.get_indices()):
            self.score[color] = 0


    def new_free_game(self):
        """Initialize the game with a free placement
        i.e. no piece yet placed."""

        self.__init_game()

        print()
        print("new free game")
        self.absmap.print_absmap()
        self.__print_status()


    def new_random_game(self):
        """Initialize the game with a random placement."""

        self.__init_game()
        self.absmap.place_pieces_at_random_positions()
        self.placement = self.absmap.export_positions()
        self.placement_over = True

        print()
        print("new random game")
        self.absmap.print_absmap()
        self.__print_status()


    def new_standard_game(self):
        """Initialize the game with a standard/symmetric placement."""

        self.__init_game()
        self.absmap.place_pieces_at_standard_positions()
        self.placement = self.absmap.export_positions()
        self.placement_over = True

        print()
        print("new standard game")
        self.absmap.print_absmap()
        self.__print_status()


    def parse_and_play_instruction(self, instruction, do_print=True):
        """Parse and play an instruction."""

        play_validated = False

        positions = dict()
        moves = list()

        parsing_validated = Game.__parse_instruction(instruction, positions, moves)

        if parsing_validated:

            assert len(positions) == 1 or len(moves) == 1

            if len(positions) == 1:
                play_validated = self.__play_placement(positions)

            elif len(moves) == 1:
                (play_validated, _) = self.__play_moves(moves, do_print=do_print)

            if play_validated and do_print:
                self.absmap.print_absmap()
                self.__print_status()

        return play_validated


    @staticmethod
    def __parse_instruction(instruction, positions, moves):
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


    def __play_moves(self, moves, do_try=False, do_save_try=False, do_print=True):
        """Play the given moves."""

        if do_save_try:
            assert do_try

        play_validated = True
        undo_list = list()
        saved_game_partial = self.__save_game_partial()

        try:
            for move_steps in moves:

                jersi_assert(not self.game_over, "game should be not over")
                jersi_assert(self.placement_over, "placement should be over")

                move_color = (self.move_count - 1) % Color.get_count()
                step_count = 1
                annotated_steps = list()

                jersi_assert(len(move_steps) in [1, 2],
                             "a move should have one or two steps")

                first_piece_count = None

                for (piece_count, src_label, dst_label) in move_steps:

                    jersi_assert(src_label in self.absmap.nodes.keys(),
                                 "source label should be valid")

                    jersi_assert(dst_label in self.absmap.nodes.keys(),
                                 "destination label should be valid")

                    src_node = self.absmap.nodes[src_label]

                    jersi_assert(src_node.has_one_or_two_pieces(),
                                 "source should have one or two pieces")

                    jersi_assert(src_node.get_top_color() == move_color,
                                 "moved color should be valid")

                    if first_piece_count is None:
                        first_piece_count = piece_count
                    else:
                        jersi_assert(piece_count != first_piece_count,
                                     "the two steps should move different number of pieces")

                    if piece_count == 1:
                        (piece_captured,
                         kunti_captured) = self.absmap.move_one_piece(src_label,
                                                                      dst_label,
                                                                      undo_list)

                    elif piece_count == 2:
                        (piece_captured,
                         kunti_captured) = self.absmap.move_two_pieces(src_label,
                                                                       dst_label,
                                                                       undo_list)

                    else:
                        assert False

                    annotated_steps.append((piece_count, src_label, dst_label,
                                            piece_captured, kunti_captured))
                    step_count += 1

                if not do_try:
                    self.history.append(annotated_steps)
                    self.move_count += 1
                    self.update_end_conditions()

                    if do_print:
                        print("move %s OK" % Game.stringify_move_steps(annotated_steps))

        except(JersiError) as jersi_assertion_error:
            if not do_try:
                print("assertion failed: %s !!!" % jersi_assertion_error.message)
                print("move %s KO !!!" % Game.stringify_move_steps(move_steps))
            play_validated = False
            for undo in reversed(undo_list):
                undo()
            self.__restore_game_partial(saved_game_partial)
        
        tried_game = None

        if play_validated and do_try:
            
            if do_save_try:
                tried_game = self.__save_game()
                tried_game.move_count += 1
                tried_game.update_end_conditions()

            for undo in reversed(undo_list):
                undo()
            self.__restore_game_partial(saved_game_partial)

        return (play_validated, tried_game)


    def __play_placement(self, positions):
        """Play the given positions as a placement."""

        play_validated = True
        saved_game = self.__save_game()

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

            piece_count = self.absmap.count_pieces_by_colors_and_shapes()
            instance = piece_count[color][shape]
            jersi_assert(instance < Shape.get_max_occurrences(shape), "shape should be available")

            piece = self.absmap.pieces[color][shape][instance]
            self.absmap.place_piece(piece, node_label)

            self.move_count += 1

            has_available_piece = False
            piece_count = self.absmap.count_pieces_by_colors_and_shapes()
            for color in piece_count.keys():
                for shape in piece_count[color].keys():
                    if piece_count[color][shape] < Shape.get_max_occurrences(shape):
                        has_available_piece = True
                        break

            if not has_available_piece:
                self.placement_over = False

            if self.placement_over:
                self.placement = self.absmap.export_positions()

        except(JersiError) as jersi_assertion_error:
            print("assertion failed: %s !!!" % jersi_assertion_error.message)
            play_validated = False
            self.__restore_game(saved_game)

        return play_validated


    def print_possiblities(self):
        """Print the possible moves for the current color."""

        move_color = (self.move_count - 1) % Color.get_count()
        move_list = self.find_moves(move_color)

        print()
        print("%d possible moves:" % len(move_list))
        for line in Game.__textify_moves(move_list):
            print(line)


    def print_history(self):
        """Print the history of moves. Placement is not printed."""

        print()
        print("move history:")
        for line in Game.__textify_moves(self.history):
            print(line)


    def __print_status(self):
        """Print the status of the game: turn, score, count of pieces."""

        piece_count = self.absmap.count_pieces_by_colors_and_shapes()

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

        time_now = datetime.datetime.now()
        time_delta = time_now - self.time
        self.time = time_now
        text += " / clock %s" % self.time.strftime("%H:%M:%S")
        text += " / delay %d s" % time_delta.total_seconds()

        print()
        print(text)


    def read_game(self, file_path):
        """Read a game from a file: set initial positions of pieces (placement)
        and play read moves."""

        positions = dict()
        moves = list()
        parsing_validated = True

        try:
            file_stream = open(file_path, 'r')
        except OSError:
            print("cannot read game from file '%s'" % file_path)
            return

        for line in file_stream:

            if re.match(r"^s*$", line):
                continue

            elif re.match(r"^s*#.*$", line):
                continue

            else:
                instructions = line.split()
                for instruction in instructions:
                    instruction_validated = Game.__parse_instruction(instruction, positions, moves)
                    if not instruction_validated:
                        parsing_validated = False

        file_stream.close()

        if parsing_validated:

            saved_game = self.__save_game()
            self.__init_game()

            placement_validated = True
            play_validated = True

            try:
                self.absmap.import_placement(positions)
                self.placement = self.absmap.export_positions()
                self.placement_over = True

            except(JersiError) as jersi_assertion_error:
                print("assertion failed: %s !!!" % jersi_assertion_error.message)
                placement_validated = False

            if placement_validated:
                (play_validated, _) = self.__play_moves(moves)

            if placement_validated and play_validated:
                print()
                print("game from file '%s'" % file_path)
                self.absmap.print_absmap()
                self.__print_status()

            else:
                self.__restore_game(saved_game)


    def read_positions(self, file_path):
        """Remove all pieces from the absmap and set pieces only
        at the read positions from the file."""

        positions = dict()
        moves = list()
        parsing_validated = True

        try:
            file_stream = open(file_path, 'r')
        except OSError:
            print("cannot read positions from file '%s'" % file_path)
            return

        for line in file_stream:
            if re.match(r"^s*$", line):
                continue
            elif re.match(r"^s*#.*$", line):
                continue
            else:
                instructions = line.split()
                for instruction in instructions:
                    instruction_validated = Game.__parse_instruction(instruction, positions, moves)
                    if not instruction_validated:
                        parsing_validated = False

        file_stream.close()

        if parsing_validated:

            saved_game = self.__save_game()
            self.__init_game()

            importing_validated = True
            try:
                jersi_assert(not moves, "file should not have moves") # assert len(moves) == 0

                self.absmap.import_positions(positions)
                self.placement = self.absmap.export_positions()
                self.placement_over = True
                self.update_end_conditions()

            except(JersiError) as jersi_assertion_error:
                print("assertion failed: %s !!!" % jersi_assertion_error.message)
                importing_validated = False

            if importing_validated:
                print()
                print("positions from file '%s'" % file_path)
                self.absmap.print_absmap()
                self.__print_status()

            else:
                self.__restore_game(saved_game)


    def __restore_game(self, saved_game):
        """Restore all saved attributes of the game."""

        self.__dict__.update(saved_game.__dict__)


    def __restore_game_partial(self, saved_game):
        """Restore all saved attributes of the game, but not absmap."""

        self.__dict__.update(saved_game.__dict__)


    def __save_game(self):
        """Save all atributes of the game."""

        saved_game = copy.deepcopy(self)
        return saved_game


    def __save_game_partial(self):
        """Save all atributes of the game, but not absmap."""

        cls = self.__class__
        saved_game = cls.__new__(cls)

        saved_game.placement = copy.copy(self.placement)
        saved_game.history = copy.copy(self.history)
        saved_game.game_over = self.game_over
        saved_game.placement_over = self.placement_over
        saved_game.last_count = self.last_count
        saved_game.move_count = self.move_count
        saved_game.score = copy.copy(self.score)

        return saved_game


    @staticmethod
    def stringify_move_steps(move_steps):
        """Convert all steps of the given move as a string."""

        move_text = ""
        max_move_text_len = None

        for (step_index, step) in enumerate(move_steps):

            if len(step) == 5:
                (piece_count, src_label, dst_label,
                 piece_captured, kunti_captured) = step

            elif len(step) == 3:
                (piece_count, src_label, dst_label,
                 piece_captured, kunti_captured) = (*step, False, False)

            else:
                assert False

            if max_move_text_len is None:
                max_move_text_len = 3*len(src_label) + len("-")+ len("=") + 4*len("!")

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

        move_text = move_text.ljust(max_move_text_len, " ")

        return move_text


    def __swap_game(self, saved_game):
        """Return a shallow copu of self and repalce self by saved_game."""

        cls = self.__class__
        new_one = cls.__new__(cls)
        new_one.__dict__.update(self.__dict__)

        self.__dict__.update(saved_game.__dict__)

        return new_one


    @staticmethod
    def __textify_moves(moves):
        """Convert given moves as a list of string."""

        lines = list()

        for (move_index, move_steps) in enumerate(moves):

            move_text = Game.stringify_move_steps(move_steps)

            if move_index % 2 == 0:
                lines.append(move_text)
            else:
                lines[-1] += " "*2 + move_text

        return lines


    @staticmethod
    def __textify_positions(positions):
        """Convert all given piece positions as a list of string."""

        lines = list()

        start_index = 0

        for (node_label, piece_names) in  sorted(positions.items()):

            for piece_name in piece_names:

                piece_text = "%s:%s" % (node_label, piece_name)

                if start_index % 2 == 0:
                    lines.append(piece_text)
                else:
                    lines[-1] += " "*2 + piece_text

                start_index += 1

        return lines


    def update_end_conditions(self):
        """Determine conditions for ending a game."""

        piece_count = self.absmap.count_pieces_by_colors_and_shapes()

        for color in piece_count.keys():
            self.score[color] = 1
            if piece_count[color][Shape.kunti] == 0:
                self.game_over = True
                self.score[color] = 0

        if not self.game_over:

            if self.last_count is None:
                for color in piece_count.keys():
                    shape_count = 0
                    for shape in piece_count[color].keys():
                        if piece_count[color][shape] > 0:
                            shape_count += 1
                    if shape_count <= 2:
                        # Only kunti + another type of shape
                        self.last_count = 20
            else:
                self.last_count -= 1
                if self.last_count == 0:
                    self.game_over = True

        if not self.game_over:
            # Possible moves for current player?
            move_color = (self.move_count - 1) % Color.get_count()
            if not self.__can_move(move_color):
                for color in Color.get_indices():
                    self.score[color] = 1
                self.game_over = True
                self.score[move_color] = 1


    def write_game(self, file_path):
        """Write a game into a file: set initial positions of pieces (placement)
        and play read moves."""

        try:
            file_stream = open(file_path, 'w')
        except OSError:
            print("cannot write game to file '%s'" % file_path)
            return

        for line in Game.__textify_positions(self.placement):
            file_stream.write("%s\n" % line)

        file_stream.write("\n")

        for line in Game.__textify_moves(self.history):
            file_stream.write("%s\n" % line)

        file_stream.close()

        print("saving game in file '%s' done" % file_path)


    def write_positions(self, file_path):
        """Write into a file the actual positions of pieces."""

        try:
            file_stream = open(file_path, 'w')
        except OSError:
            print("cannot write positions to file '%s'" % file_path)
            return

        for line in Game.__textify_positions(self.absmap.export_positions()):
            file_stream.write("%s\n" % line)

        file_stream.close()

        print("saving positions in file '%s' done" % file_path)


class Algorithm:
    """Algorithm for playing JERSI."""

    classes = dict()

    def __init__(self, color):
        """Initialize the algorithm."""
        self._color = color
        self._enabled = False
        self._options = dict()


    def enable(self, condition):
        """Change the algorithm status."""
        self._enabled = condition


    def is_enabled(self):
        """Is the algorithm enabled?"""
        return self._enabled


    def get_advice(self, game):
        """Return an advice for playing the next move."""

        assert False # Must be redfined by some inherited class
        move_string = None
        return move_string


    def get_color(self):
        """Return the color for which the algorithm is dedicated."""
        return self._color


    def get_name(self):
        """Return name of algorithm."""
        name = None
        for (algorithm_name, algorithm_class) in Algorithm.classes.items():
            if self.__class__ == algorithm_class:
                name = algorithm_name
        return name


    def get_options(self):
        """Return options of algorithm."""
        return self._options


    @staticmethod
    def register_algorithm_class(algorithm_name, algorithm_class):
        """Register a new class of algorithm."""
        assert algorithm_name not in Algorithm.classes
        Algorithm.classes[algorithm_name] = algorithm_class


    def set_options(self, options):
        """Set options of algorithm."""
        self._options.update(options)


class AlgorithmFirstMove(Algorithm):
    """Algorithm for playing JERSI. Select first found move."""


    def __init__(self, color):
        """Initialize the algorithm."""
        Algorithm.__init__(self, color)


    def get_advice(self, game):
        """Return an advice for playing the next move."""

        move_string = None

        move_color = game.get_move_color()

        if move_color is not None:
            assert move_color == self.get_color()

            move_list = game.find_moves(move_color, find_one=True)

            if move_list:
                move = move_list[0]

                move_string = Game.stringify_move_steps(move)
                move_string = move_string.strip()

        return move_string


Algorithm.register_algorithm_class("first-move", AlgorithmFirstMove)


class AlgorithmRandomMove(Algorithm):
    """Algorithm for playing JERSI. Randomly select a move."""


    def __init__(self, color):
        """Initialize the algorithm."""
        Algorithm.__init__(self, color)


    def get_advice(self, game):
        """Return an advice for playing the next move."""

        move_string = None

        move_color = game.get_move_color()

        if move_color is not None:
            assert move_color == self.get_color()

            move_list = game.find_moves(move_color, find_one=False)

            if move_list:
                move = random.choice(move_list)

                move_string = Game.stringify_move_steps(move)
                move_string = move_string.strip()

        return move_string


Algorithm.register_algorithm_class("random-move", AlgorithmRandomMove)



class AlgorithmCertu(Algorithm):
    """Algorithm for playing JERSI. MinMax type of algorithm."""


    def __init__(self, color):
        """Initialize the algorithm."""
        Algorithm.__init__(self, color)
        self._options["debug"] = False
        self._options["depth_max"] = 2
        self._options["width_ratio"] = [None, None]


    def get_advice(self, game):
        """Return an advice for playing the next move."""

        move_string = None

        move_color = game.get_move_color()

        if move_color is not None:
            assert move_color == self.get_color()

            min_max_root = MinMaxNode(game, debug=self._options["debug"])

            min_max_root.build_children(depth_max=self._options["depth_max"],
                                        width_ratio=self._options["width_ratio"])


            min_max_root.compute_score()

            print()
            print("MinMaxNode: %d evaluated leaves" % min_max_root.count_leaves())

            move_string = min_max_root.find_child_with_min_score()

        return move_string


Algorithm.register_algorithm_class("certu", AlgorithmCertu)


class MinMaxNode:
    """Node of the exploration tree of the MinMax strategy."""

    def __init__(self, game, move_string=None, depth=0, debug=False):
        """Initialize a MinMaxNode."""

        assert (move_string is None and depth == 0) or (move_string is not None and depth > 0)

        self.game = game
        self.move_string = move_string
        self.depth = depth
        self.debug = debug

        self.move_color = self.game.get_move_color()
        self.is_player = (self.depth % 2 == 0)

        self.children = dict()
        self.score = None

        if self.debug:
            print()
            print("debug: MinMaxNode.__init__: move_string=", self.move_string)
            print("debug: MinMaxNode.__init__: depth=", self.depth)
            if self.move_color is not None:
                print("debug: MinMaxNode.__init__: move_color=", Color.get_name(self.move_color))
            print("debug: MinMaxNode.__init__: is_player=", self.is_player)


    def build_children(self, depth_max, width_ratio=None):
        """Build children from the current MinMaxNode down to the given depth."""

        if self.depth < depth_max:

            if self.debug:
                print()
                print("debug: MinMaxNode.build_children: move_string=", self.move_string)
                print("debug: MinMaxNode.build_children: depth=", self.depth)

            if self.move_color is not None:

                if width_ratio is None:
                    actual_width_ratio = None
                    
                elif self.depth < len(width_ratio):
                    actual_width_ratio = width_ratio[self.depth]
                else:
                    actual_width_ratio = width_ratio[-1]


                move_count = 0
                
                for (move, game) in self.game.find_moves_and_games(self.move_color, find_one=False):
                    
                    if actual_width_ratio is None or random.random() <= actual_width_ratio:
                        move_count += 1

                        move_string = Game.stringify_move_steps(move)
                        move_string = move_string.strip()

                        self.children[move_string] = MinMaxNode(game, move_string,
                                                                self.depth + 1,
                                                                self.debug)

                        self.children[move_string].build_children(depth_max, width_ratio)

                if self.debug:
                    print()
                    print("debug: MinMaxNode.build_children: move_count=", move_count)


    def compute_leaf_score(self):
        """Compute the score of a leaf node."""

        assert not self.children

        if self.score is None:

            self.score = 0.

            if self.game.game_over:

                if self.is_player:
                    self.score += 1.e30
                else:
                    self.score += -1.e30
            else:
                piece_count = self.game.absmap.count_pieces_by_colors_and_shapes()

                if self.is_player:
                    player_color = (self.move_color + 1) % Color.get_count()
                else:
                    player_color = self.move_color

                opponent_color = (player_color + 1) % Color.get_count()

                # compute count of pieces
                player_piece_count = 0
                for shape in piece_count[player_color].keys():
                    player_piece_count += piece_count[player_color][shape]

                opponent_piece_count = 0
                for shape in piece_count[opponent_color].keys():
                    opponent_piece_count += piece_count[opponent_color][shape]

                # compute defended pairs
                pieces = self.game.absmap.get_pieces_by_colors()

                player_defended_pair_count = 0
                for fst_piece in pieces[player_color]:
                    for snd_piece in pieces[player_color]:
                        if fst_piece != snd_piece and fst_piece.shape != Shape.kunti and snd_piece.shape != Shape.kunti:
                            fst_node = fst_piece.node
                            snd_node = snd_piece.node
                            if snd_node in fst_node.nodes_at_one_link:
                                fst_shape = fst_node.get_top_shape()
                                snd_shape = snd_node.get_top_shape()
                                if fst_shape != Shape.kunti and snd_shape != Shape.kunti:
                                    for shape in Shape.get_indices():
                                        if Shape.beats(shape, fst_shape):
                                            if Shape.beats(snd_shape, shape):
                                                player_defended_pair_count += 1

                opponent_defended_pair_count = 0
                for fst_piece in pieces[opponent_color]:
                    for snd_piece in pieces[opponent_color]:
                        if fst_piece != snd_piece and fst_piece.shape != Shape.kunti and snd_piece.shape != Shape.kunti:
                            fst_node = fst_piece.node
                            snd_node = snd_piece.node
                            if snd_node in fst_node.nodes_at_one_link:
                                fst_shape = fst_node.get_top_shape()
                                snd_shape = snd_node.get_top_shape()
                                if fst_shape != Shape.kunti and snd_shape != Shape.kunti:
                                    for shape in Shape.get_indices():
                                        if Shape.beats(shape, fst_shape):
                                            if Shape.beats(snd_shape, shape):
                                                opponent_defended_pair_count += 1

                diff_defended_pair_count = player_defended_pair_count - opponent_defended_pair_count


                # compute fly distance to kunti
                hexmap = self.game.absmap.hexmap

                player_kunti = self.game.absmap.pieces[player_color][Shape.kunti][0]
                player_kunti_label = player_kunti.node.label

                opponent_kunti = self.game.absmap.pieces[opponent_color][Shape.kunti][0]
                opponent_kunti_label = opponent_kunti.node.label

                player_kunti_distance_sum = 0
                player_kunti_distance_min = None
                for shape in Shape.get_indices():
                    if shape != Shape.kunti:
                        for piece in self.game.absmap.pieces[player_color][shape]:
                            if piece.node is not None:
                                piece_label = piece.node.label

                                distance = hexmap.compute_distance(opponent_kunti_label,
                                                                   piece_label)

                                player_kunti_distance_sum += distance

                                if player_kunti_distance_min is None:
                                    player_kunti_distance_min = distance
                                elif distance < player_kunti_distance_min:
                                    player_kunti_distance_min = distance

                opponent_kunti_distance_sum = 0
                opponent_kunti_distance_min = None
                for shape in Shape.get_indices():
                    if shape != Shape.kunti:
                        for piece in self.game.absmap.pieces[opponent_color][shape]:
                            if piece.node is not None:
                                piece_label = piece.node.label

                                distance = hexmap.compute_distance(player_kunti_label,
                                                                   piece_label)

                                opponent_kunti_distance_sum += distance

                                if opponent_kunti_distance_min is None:
                                    opponent_kunti_distance_min = distance
                                elif distance < opponent_kunti_distance_min:
                                    opponent_kunti_distance_min = distance


                diff_piece_count = player_piece_count - opponent_piece_count

                if player_kunti_distance_min is None or opponent_kunti_distance_min is None:
                    diff_kunti_distance_min = 0
                else:
                    diff_kunti_distance_min = opponent_kunti_distance_min - player_kunti_distance_min

                diff_kunti_distance_sum = opponent_kunti_distance_sum - player_kunti_distance_sum

                if not self.is_player:
                    diff_piece_count *= -1
                    diff_defended_pair_count *= -1
                    diff_kunti_distance_min *= -1
                    diff_kunti_distance_sum *= -1

                weight_piece_count = 1.e8
                weight_kunti_distance_min = 1.e4
                weight_kunti_distance_sum = 1.
                weight_defended_pair_count = 1.

                self.score += float(diff_piece_count)*weight_piece_count
                self.score += float(diff_kunti_distance_min)*weight_kunti_distance_min
                self.score += float(diff_kunti_distance_sum)*weight_kunti_distance_sum
                self.score += float(diff_defended_pair_count)*weight_defended_pair_count

        if self.debug:
            print()
            print()
            print("debug: MinMaxNode.compute_leaf_score: move_string=", self.move_string)
            print("debug: MinMaxNode.compute_leaf_score: depth=", self.depth)

            if not self.game.game_over:
                print("debug: MinMaxNode.compute_leaf_score: move_color=",
                      Color.get_name(self.move_color))

                print("debug: MinMaxNode.compute_leaf_score: diff_piece_count=",
                      diff_piece_count)

                print("debug: MinMaxNode.compute_leaf_score: diff_kunti_distance_min=",
                      diff_kunti_distance_min)

                print("debug: MinMaxNode.compute_leaf_score: diff_kunti_distance_sum=",
                      diff_kunti_distance_sum)

                print("debug: MinMaxNode.compute_leaf_score: weight_defended_pair_count=",
                      weight_defended_pair_count)

            print("debug: MinMaxNode.compute_leaf_score: score=", self.score)

        return self.score


    def compute_score(self):
        """Compute the score of the current node."""

        if self.debug:
            print()
            print("debug: MinMaxNode.compute_score: move_string=", self.move_string)
            print("debug: MinMaxNode.compute_score: depth=", self.depth)

        if self.score is None:

            if not self.children:
                self.score = self.compute_leaf_score()

            elif self.is_player:
                score_max = None
                for child in self.children.values():
                    child_score = child.compute_score()
                    if score_max is None or child_score > score_max:
                        score_max = child_score
                self.score = score_max

            else:
                score_min = None
                for child in self.children.values():
                    child_score = child.compute_score()
                    if score_min is None or child_score < score_min:
                        score_min = child_score
                self.score = score_min

        return self.score


    def count_leaves(self):
        """Count leaves"""

        if not self.children:
            count = 1

        else:
            count = 0
            for child in self.children.values():
                count += child.count_leaves()

        return count


    def find_child_with_min_score(self):
        """Find the child with the min score."""

        move_string = None
        score_min = None
        move_string_list = None

        for child in self.children.values():

            if score_min is None or child.score < score_min:
                score_min = child.score
                move_string_list = list()
                move_string_list.append(child.move_string)

            elif child.score == score_min:
                move_string_list.append(child.move_string)

            if self.debug:
                print()

                print("debug: MinMaxNode.find_child_with_min_score: child.move_string=",
                      child.move_string)

                print("debug: MinMaxNode.find_child_with_min_score: child.score=",
                      child.score)

        assert score_min is not None
        assert move_string_list is not None

        if self.debug:
            print()
            print("debug: MinMaxNode.find_child_with_min_score: score_min=", score_min)

            print("debug: MinMaxNode.find_child_with_min_score: %d move(s) with score_min"
                  % len(move_string_list))

            for move_string in move_string_list:
                print("debug: MinMaxNode.find_child_with_min_score: move=", move_string)

        move_string = random.choice(move_string_list)

        return move_string


class Runner:
    """Provide services for playing, saving and reloading a game of JERSI."""

    def __init__(self):
        """Initialize a Runner of the Game."""
        self.__game = Game()

        self.__algorithms = dict()
        for color in Color.get_indices():
            algorithm_class = Algorithm.classes["certu"]
            algorithm = algorithm_class(color)
            algorithm.enable(False)
            self.__algorithms[color] = algorithm

        self.__continue_running = False


    def __apply_algo_advice(self):
        """Apply the advice of the current color algorithm."""

        move_string = self.__get_algo_advice()
        if move_string is not None:
            print()
            print("apply %s algorithm advice" % Color.get_name(self.__game.get_move_color()))
            self.__game.parse_and_play_instruction(move_string)


    def __get_algo_advice(self):
        """Return the advice of the current color algorithm."""

        move_color = self.__game.get_move_color()
        if move_color is not None:
            algorithm = self.__algorithms[move_color]
            move_string = algorithm.get_advice(self.__game)
        else:
            move_string = None

        return move_string


    @staticmethod
    def run_help(_):
        """Print help about the commands."""

        print()
        print("commands:")
        print()
        print("    i p: instruction for a placement 'p'; examples of placement:")
        print("         i a1:K")
        print("         i h1:c")
        print()
        print("    i m: instruction for a move 'm'; examples of move in one or two steps:")
        print("         i a1-b1")
        print("         i a1=c1")
        print("         i a1-b1=d1")
        print("         i a1=c1-d1")
        print()
        print("      h: help")
        print("      q: quit")
        print()
        print("     nf: new game with free positions")
        print("     nr: new game with random positions")
        print("     ns: new game with standard positions")
        print()
        print("     ph: print game history (only moves; not placement)")
        print("     pp: print possiblities of moves for current color")
        print()
        print("   rg f: read the game from the given file 'f'")
        print("   rp f: read the positions from the given file 'f'")
        print("   wg f: write the game into the given file 'f'")
        print("   wp f: write the positions into the given file 'f'")
        print()
        print("    cba n: change blue algorithm for 'n'.")
        print("    cra n: change red algorithm for 'n'.")
        print("  sba o=v: set blue algorithm with o=v.")
        print("  sra o=v: set red algorithm with o=v.")
        print("      eba: enable blue algorithm.")
        print("      era: enable red algorithm.")
        print("      dba: disable blue algorithm.")
        print("      dra: disable red algorithm.")
        print("       pa: print algorithms (name, status and options).")
        print("      paa: print available algorithms.")
        print()
        print("     aa: ask algorithm advice for the current color.")
        print("  rea n: repeat n times the enabled blue-red algorithms.")


    def __run_quit(self, _):
        """Quit the run loop."""
        self.__continue_running = False


    def __run_new_free_game(self, _):
        """Set up a new free game."""
        self.__game.new_free_game()


    def __run_new_random_game(self, _):
        """Set up a new random game."""
        self.__game.new_random_game()


    def __run_new_standard_game(self, _):
        """Set up a new standard game."""
        self.__game.new_standard_game()


    def __run_print_history(self, _):
        """Print history."""
        self.__game.print_history()


    def __run_print_possiblities(self, _):
        """Print possiblities."""
        self.__game.print_possiblities()


    def __run_read_game(self, command_args):
        """Read game from fle."""

        if len(command_args) == 2:
            file_path = command_args[1]
            self.__game.read_game(file_path)
        else:
            print("turn syntax error !!!")


    def __run_read_positions(self, command_args):
        """Read positions from fle."""

        if len(command_args) == 2:
            file_path = command_args[1]
            self.__game.read_positions(file_path)
        else:
            print("turn syntax error !!!")


    def __run_write_game(self, command_args):
        """Write game to fle."""

        if len(command_args) == 2:
            file_path = command_args[1]
            self.__game.write_game(file_path)
        else:
            print("turn syntax error !!!")


    def __run_write_positions(self, command_args):
        """Write positions to fle."""

        if len(command_args) == 2:
            file_path = command_args[1]
            self.__game.write_positions(file_path)
        else:
            print("turn syntax error !!!")


    def __run_change_blue_algorithm(self, command_args):
        """Change blue algorithm."""
        self.__run_change_color_algorithm(Color.blue, command_args)


    def __run_change_red_algorithm(self, command_args):
        """Change red algorithm."""
        self.__run_change_color_algorithm(Color.red, command_args)


    def __run_change_color_algorithm(self, color, command_args):
        """Change algorithm of the given color."""

        assert color in self.__algorithms

        if len(command_args) == 2:
            algorithm_name = command_args[1]
            if algorithm_name in Algorithm.classes:
                algorithm_class = Algorithm.classes[algorithm_name]
                algorithm = algorithm_class(color)
                self.__algorithms[color] = algorithm
                print()
                print("%s algorithm changed" % Color.get_name(color))

            else:
                print("%s is not known" % algorithm_name)
        else:
            print("turn syntax error !!!")


    def __run_enable_blue_algorithm(self, command_args):
        """Enable blue algorithm."""
        self.__run_enable_color_algorithm(Color.blue, command_args)


    def __run_enable_red_algorithm(self, command_args):
        """Enable red algorithm."""
        self.__run_enable_color_algorithm(Color.red, command_args)


    def __run_enable_color_algorithm(self, color, _):
        """Enable algorithm of the given color."""

        assert color in self.__algorithms

        self.__algorithms[color].enable(True)
        print()
        print("%s algorithm enabled" % Color.get_name(color))
        if color == self.__game.get_move_color():
            self.__apply_algo_advice()


    def __run_disable_blue_algorithm(self, command_args):
        """Disable blue algorithm."""
        self.__run_disable_color_algorithm(Color.blue, command_args)


    def __run_disable_red_algorithm(self, command_args):
        """Disable red algorithm."""
        self.__run_disable_color_algorithm(Color.red, command_args)


    def __run_disable_color_algorithm(self, color, _):
        """Disable algorithm of the given color."""

        assert color in self.__algorithms

        self.__algorithms[color].enable(False)
        print()
        print("%s algorithm disabled" % Color.get_name(color))


    def __run_print_algorithms(self, _):
        """Print algorithms (name, status, options)."""

        for (color, algorithm) in self.__algorithms.items():
            print()
            print("%s algorithm is %s" % (Color.get_name(color), algorithm.get_name()))

            if self.__algorithms[color].is_enabled():
                print("    enabled")
            else:
                print("    disabled")

            for (option, value) in algorithm.get_options().items():
                print("    %s = %s" % (option, str(value)))


    @staticmethod
    def __run_print_available_algorithms(_):
        """Print available algorithms."""

        print()
        print("available algorithms:")
        for algorithm_name in sorted(Algorithm.classes):
            print("    %s" % algorithm_name)


    def __run_set_blue_algorithm(self, command_args):
        """Set options of the blue algorithm."""
        self.__run_set_color_algorithm(Color.blue, command_args)


    def __run_set_red_algorithm(self, command_args):
        """Set options of the red algorithm."""
        self.__run_set_color_algorithm(Color.red, command_args)


    def __run_set_color_algorithm(self, color, command_args):
        """Set option for the algorithm of the given color."""

        assert color in self.__algorithms

        options = dict()
        options_well_parsed = True

        for option_string in command_args[1:]:
            option_items = option_string.split("=")
            if len(option_items) == 2:
                key = option_items[0]

                try:
                    value = ast.literal_eval(option_items[1])
                except ValueError:
                    options_well_parsed = False
                    print("evaluation error of value in key-value pair '%s'" % option_string)

                if options_well_parsed:
                    options[key] = value
            else:
                options_well_parsed = False
                print("syntax error in key-value pair '%s'" % option_string)

        if options_well_parsed:
            self.__algorithms[color].set_options(options)
            print()
            print("%s algorithm set" % Color.get_name(color))


    def __run_algorithm_advice(self, _):
        """Ask algorithm advice."""

        move_string = self.__get_algo_advice()
        print()
        if move_string is not None:
            print("algorithm advice: %s" % move_string)
        else:
            print("no algorithm advice !!!")


    def __run_enabled_algorithms(self, command_args):
        """Run enabled algorithms (if both blue and red are enabled)."""

        if len(command_args) == 2:
            try:
                ntimes = int(command_args[1])
                assert ntimes > 0
            except ValueError:
                print("not an positive integer !!!")
                ntimes = 0

            blue_algorithm_enabled = self.__algorithms[Color.blue].is_enabled()
            red_algorithm_enabled = self.__algorithms[Color.red].is_enabled()

            if blue_algorithm_enabled and red_algorithm_enabled:
                for _ in range(2*ntimes):
                    self.__apply_algo_advice()
            else:
                print("blue and red algorithms are not both enabled !!!")

        else:
            print("turn syntax error !!!")


    def __run_instruction(self, command_args):
        """Run either a placement or move instruction."""

        blue_algorithm_enabled = self.__algorithms[Color.blue].is_enabled()
        red_algorithm_enabled = self.__algorithms[Color.red].is_enabled()

        if blue_algorithm_enabled and red_algorithm_enabled:
            print("blue and red algorithms enabled; no move input is expected !!!")

        else:
            if len(command_args) == 2:
                instruction = command_args[1]
                play_validated = self.__game.parse_and_play_instruction(instruction)

                if play_validated:
                    if blue_algorithm_enabled or red_algorithm_enabled:
                        self.__apply_algo_advice()

            else:
                print("syntax error in instruction '%s' !!!" % instruction)


    def run(self):
        """Run all entered commands until the command for quitting."""

        run_commands = dict()

        run_commands["h"] = self.run_help
        run_commands["q"] = self.__run_quit

        run_commands["nf"] = self.__run_new_free_game
        run_commands["nr"] = self.__run_new_random_game
        run_commands["ns"] = self.__run_new_standard_game

        run_commands["ph"] = self.__run_print_history
        run_commands["pp"] = self.__run_print_possiblities

        run_commands["rg"] = self.__run_read_game
        run_commands["rp"] = self.__run_read_positions
        run_commands["wg"] = self.__run_write_game
        run_commands["wp"] = self.__run_write_positions

        run_commands["cba"] = self.__run_change_blue_algorithm
        run_commands["cra"] = self.__run_change_red_algorithm
        run_commands["eba"] = self.__run_enable_blue_algorithm
        run_commands["era"] = self.__run_enable_red_algorithm
        run_commands["dba"] = self.__run_disable_blue_algorithm
        run_commands["dra"] = self.__run_disable_red_algorithm
        run_commands["pa"] = self.__run_print_algorithms
        run_commands["paa"] = self.__run_print_available_algorithms
        run_commands["sba"] = self.__run_set_blue_algorithm
        run_commands["sra"] = self.__run_set_red_algorithm

        run_commands["aa"] = self.__run_algorithm_advice
        run_commands["rea"] = self.__run_enabled_algorithms

        run_commands["i"] = self.__run_instruction

        self.__continue_running = True

        while self.__continue_running:

            command_line = input("command? ")
            command_args = command_line.split()

            if not command_args:
                print("no command !!!")

            elif command_args[0] in run_commands:
                run_commands[command_args[0]](command_args)

            else:
                print("unknown command '%s' !!!" % command_args[0])


def main():
    """Start JERSI."""

    print(_COPYRIGHT_AND_LICENSE)
    my_runner = Runner()
    my_runner.run()


if __name__ == "__main__":
    main()
    #cProfile.run("main()")
