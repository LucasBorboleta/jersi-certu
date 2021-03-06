#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""jersi_certu.py implements a rule engine for the JERSI boardgame."""

_COPYRIGHT_AND_LICENSE = """
JERSI-CERTU implements a GUI and a rule engine for the JERSI boardgame.

Copyright (C) 2020 Lucas Borboleta (lucas.borboleta@free.fr).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""


import array
import collections
import copy
import enum
import os
import random
import sys


_do_debug = False

_script_home = os.path.abspath(os.path.dirname(__file__))
_mcts_home = os.path.join(_script_home, "packages", "MCTS", "commit-4e62716afdc1691784e33998297067cc4413dc6f")
sys.path.append(_mcts_home)
import mcts


@enum.unique
class Capture(enum.Enum):
    KING = enum.auto()
    NONE = enum.auto()
    SOME = enum.auto()


@enum.unique
class CubeSort(enum.Enum):
    FOUL = enum.auto()
    KING = enum.auto()
    MOUNTAIN = enum.auto()
    PAPER = enum.auto()
    ROCK = enum.auto()
    SCISSORS = enum.auto()
    WISE = enum.auto()


@enum.unique
class CubeStatus(enum.IntEnum):
    ACTIVATED = -121
    CAPTURED = -122
    RESERVED = -123


@enum.unique
class HexagonDirection(enum.IntEnum):
    PHI_090 = 0
    PHI_150 = 1
    PHI_210 = 2
    PHI_270 = 3
    PHI_330 = 4
    PHI_030 = 5


@enum.unique
class Null(enum.IntEnum):
    CUBE = -101
    HEXAGON = -102


class Player(enum.IntEnum):
    WHITE = 0
    BLACK = 1

    @staticmethod
    def name(player):
        if player == Player.WHITE:
            return "white"

        elif player == Player.BLACK:
            return "black"

        else:
            assert False


@enum.unique
class Reward(enum.IntEnum):
    WIN = 1
    DRAW = 0
    LOSS = -1

    assert LOSS < DRAW < WIN
    assert DRAW == 0
    assert LOSS + WIN == DRAW


@enum.unique
class TerminalCase(enum.Enum):

    BLACK_ARRIVED = enum.auto()
    BLACK_CAPTURED = enum.auto()
    BLACK_BLOCKED = enum.auto()

    WHITE_ARRIVED = enum.auto()
    WHITE_CAPTURED = enum.auto()
    WHITE_BLOCKED = enum.auto()

    ZERO_CREDIT = enum.auto()


class Cube:

    __all_sorted_cubes = []
    __init_done = False
    __king_index = None
    __name_to_cube = {}
    __sort_and_player_to_label = {}

    all = None # shortcut to Cube.get_all()
    black_king_index = None
    white_king_index = None


    def __init__(self, name, label, sort, player):
        """Create a cube and check its properties"""

        assert name not in Cube.__name_to_cube
        assert len(name) == 2
        assert len(label) == 1
        assert label == name[0]

        assert sort in CubeSort
        assert player in Player

        if player == Player.WHITE:
            assert label == label.upper()
        elif player == Player.BLACK:
            assert label == label.lower()
        else:
            assert False

        if (sort, player) not in Cube.__sort_and_player_to_label:
            Cube.__sort_and_player_to_label[(sort, player)] = label
        else:
            assert Cube.__sort_and_player_to_label[(sort, player)] == label

        self.name = name
        self.label = label
        self.sort = sort
        self.player = player
        self.index = None

        Cube.__name_to_cube[self.name] = self


    def __str__(self):
        return f"Cube({self.name}, {self.label}, {self.sort}, {self.player}, {self.index})"


    def beats(self, other):

        if self.player == other.player:
            does_beat = False

        else:

            if self.sort in (CubeSort.KING, CubeSort.WISE, CubeSort.MOUNTAIN):
                does_beat = False

            elif other.sort == CubeSort.MOUNTAIN:
                does_beat = False

            elif self.sort == CubeSort.ROCK:
                does_beat = other.sort in (CubeSort.SCISSORS, CubeSort.FOUL, CubeSort.KING, CubeSort.WISE)

            elif self.sort == CubeSort.PAPER:
                does_beat = other.sort in (CubeSort.ROCK, CubeSort.FOUL, CubeSort.KING, CubeSort.WISE)

            elif self.sort == CubeSort.SCISSORS:
                does_beat = other.sort in (CubeSort.PAPER, CubeSort.FOUL, CubeSort.KING, CubeSort.WISE)

            elif self.sort == CubeSort.FOUL:
                does_beat = other.sort in (CubeSort.ROCK, CubeSort.PAPER, CubeSort.SCISSORS, CubeSort.FOUL, CubeSort.KING)

            else:
                assert False

        return does_beat


    @staticmethod
    def get(name):
        return Cube.__name_to_cube[name]


    @staticmethod
    def get_all():
        return Cube.__all_sorted_cubes


    @staticmethod
    def get_king_index(player):
        return Cube.__king_index[player]


    @staticmethod
    def init():
        if not Cube.__init_done:
            Cube.__create_cubes()
            Cube.__create_all_sorted_cubes()
            Cube.__create_king_index()
            Cube.__init_done = True


    @staticmethod
    def show_all():
        for cube in Cube.__all_sorted_cubes:
            print(cube)


    @staticmethod
    def __create_all_sorted_cubes():
        for name in sorted(Cube.__name_to_cube.keys()):
            Cube.__all_sorted_cubes.append(Cube.__name_to_cube[name])

        for (index, cube) in enumerate(Cube.__all_sorted_cubes):
            cube.index = index

        Cube.all = Cube.__all_sorted_cubes


    @staticmethod
    def __create_king_index():
        Cube.__king_index = array.array('b', [Null.CUBE for _ in Player])
        Cube.__king_index[Player.WHITE] = Cube.get('K1').index
        Cube.__king_index[Player.BLACK] = Cube.get('k1').index

        Cube.white_king_index = Cube.get_king_index(Player.WHITE)
        Cube.black_king_index = Cube.get_king_index(Player.BLACK)


    @staticmethod
    def __create_cubes():

        Cube(name='K1', label='K', sort=CubeSort.KING, player=Player.WHITE)

        Cube(name='F1', label='F', sort=CubeSort.FOUL, player=Player.WHITE)
        Cube(name='F2', label='F', sort=CubeSort.FOUL, player=Player.WHITE)

        Cube(name='W1', label='W', sort=CubeSort.WISE, player=Player.WHITE)
        Cube(name='W2', label='W', sort=CubeSort.WISE, player=Player.WHITE)

        Cube(name='R1', label='R', sort=CubeSort.ROCK, player=Player.WHITE)
        Cube(name='R2', label='R', sort=CubeSort.ROCK, player=Player.WHITE)
        Cube(name='R3', label='R', sort=CubeSort.ROCK, player=Player.WHITE)
        Cube(name='R4', label='R', sort=CubeSort.ROCK, player=Player.WHITE)

        Cube(name='P1', label='P', sort=CubeSort.PAPER, player=Player.WHITE)
        Cube(name='P2', label='P', sort=CubeSort.PAPER, player=Player.WHITE)
        Cube(name='P3', label='P', sort=CubeSort.PAPER, player=Player.WHITE)
        Cube(name='P4', label='P', sort=CubeSort.PAPER, player=Player.WHITE)

        Cube(name='S1', label='S', sort=CubeSort.SCISSORS, player=Player.WHITE)
        Cube(name='S2', label='S', sort=CubeSort.SCISSORS, player=Player.WHITE)
        Cube(name='S3', label='S', sort=CubeSort.SCISSORS, player=Player.WHITE)
        Cube(name='S4', label='S', sort=CubeSort.SCISSORS, player=Player.WHITE)

        Cube(name='M1', label='M', sort=CubeSort.MOUNTAIN, player=Player.WHITE)
        Cube(name='M2', label='M', sort=CubeSort.MOUNTAIN, player=Player.WHITE)
        Cube(name='M3', label='M', sort=CubeSort.MOUNTAIN, player=Player.WHITE)
        Cube(name='M4', label='M', sort=CubeSort.MOUNTAIN, player=Player.WHITE)

        Cube(name='k1', label='k', sort=CubeSort.KING, player=Player.BLACK)

        Cube(name='f1', label='f', sort=CubeSort.FOUL, player=Player.BLACK)
        Cube(name='f2', label='f', sort=CubeSort.FOUL, player=Player.BLACK)

        Cube(name='w1', label='w', sort=CubeSort.WISE, player=Player.BLACK)
        Cube(name='w2', label='w', sort=CubeSort.WISE, player=Player.BLACK)

        Cube(name='r1', label='r', sort=CubeSort.ROCK, player=Player.BLACK)
        Cube(name='r2', label='r', sort=CubeSort.ROCK, player=Player.BLACK)
        Cube(name='r3', label='r', sort=CubeSort.ROCK, player=Player.BLACK)
        Cube(name='r4', label='r', sort=CubeSort.ROCK, player=Player.BLACK)

        Cube(name='p1', label='p', sort=CubeSort.PAPER, player=Player.BLACK)
        Cube(name='p2', label='p', sort=CubeSort.PAPER, player=Player.BLACK)
        Cube(name='p3', label='p', sort=CubeSort.PAPER, player=Player.BLACK)
        Cube(name='p4', label='p', sort=CubeSort.PAPER, player=Player.BLACK)

        Cube(name='s1', label='s', sort=CubeSort.SCISSORS, player=Player.BLACK)
        Cube(name='s2', label='s', sort=CubeSort.SCISSORS, player=Player.BLACK)
        Cube(name='s3', label='s', sort=CubeSort.SCISSORS, player=Player.BLACK)
        Cube(name='s4', label='s', sort=CubeSort.SCISSORS, player=Player.BLACK)

        Cube(name='m1', label='m', sort=CubeSort.MOUNTAIN, player=Player.BLACK)
        Cube(name='m2', label='m', sort=CubeSort.MOUNTAIN, player=Player.BLACK)
        Cube(name='m3', label='m', sort=CubeSort.MOUNTAIN, player=Player.BLACK)
        Cube(name='m4', label='m', sort=CubeSort.MOUNTAIN, player=Player.BLACK)


class Hexagon:

    __all_active_indices = []
    __all_indices = []
    __all_sorted_hexagons = []
    __init_done = False
    __king_begin_indices = []
    __king_end_indices = []
    __layout = []
    __name_to_hexagon = {}
    __next_fst_indices = []
    __next_snd_indices = []
    __position_uv_to_hexagon = {}

    all = None # shortcut to Hexagon.get_all()


    def __init__(self, name, position_uv, reserve=False):

        assert name not in Hexagon.__name_to_hexagon
        assert len(position_uv) == 2
        assert reserve in [True, False]
        assert position_uv not in Hexagon.__position_uv_to_hexagon

        if reserve:
            assert len(name) == 1
        else:
            assert len(name) == 2

        self.name = name
        self.position_uv = position_uv
        self.reserve = reserve
        self.index = None

        Hexagon.__name_to_hexagon[self.name] = self
        Hexagon.__position_uv_to_hexagon[position_uv] = self


    def __str__(self):
        return f"Hexagon({self.name}, {self.position_uv}, {self.reserve}), {self.index}"


    @staticmethod
    def get(name):
        return Hexagon.__name_to_hexagon[name]


    @staticmethod
    def get_all():
        return Hexagon.__all_sorted_hexagons


    @staticmethod
    def get_all_active_indices():
        return Hexagon.__all_active_indices


    @staticmethod
    def get_all_indices():
        return Hexagon.__all_indices


    @staticmethod
    def get_king_begin_indices(player):
        return Hexagon.__king_begin_indices[player]


    @staticmethod
    def get_king_end_indices(player):
        return Hexagon.__king_end_indices[player]


    @staticmethod
    def get_layout():
        return Hexagon.__layout


    @staticmethod
    def get_next_fst_active_indices(hexagon_index):
        return [x for x in Hexagon.__next_fst_indices[hexagon_index] if x != Null.HEXAGON]


    @staticmethod
    def get_next_fst_indices(hexagon_index, hexagon_dir):
        return Hexagon.__next_fst_indices[hexagon_index][hexagon_dir]


    @staticmethod
    def get_next_snd_indices(hexagon_index, hexagon_dir):
        return Hexagon.__next_snd_indices[hexagon_index][hexagon_dir]


    @staticmethod
    def init():
        if not  Hexagon.__init_done:
            Hexagon.__create_hexagons()
            Hexagon.__create_all_sorted_hexagons()
            Hexagon.__create_layout()
            Hexagon.__create_kings_hexagons()
            Hexagon.__create_delta_u_and_v()
            Hexagon.__create_next_hexagons()
            Hexagon.__init_done = True


    @staticmethod
    def show_all():
        for hexagon in Hexagon.__all_sorted_hexagons:
            print(hexagon)


    @staticmethod
    def __create_all_sorted_hexagons():
        for name in sorted(Hexagon.__name_to_hexagon.keys()):
            Hexagon.__all_sorted_hexagons.append(Hexagon.__name_to_hexagon[name])

        for (index, hexagon) in enumerate(Hexagon.__all_sorted_hexagons):
            hexagon.index = index

        for hexagon in Hexagon.__all_sorted_hexagons:
            Hexagon.__all_indices.append(hexagon.index)
            if not hexagon.reserve:
                Hexagon.__all_active_indices.append(hexagon.index)

        Hexagon.all = Hexagon.__all_sorted_hexagons


    @staticmethod
    def __create_delta_u_and_v():
        Hexagon.__delta_u = array.array('b', [+1, +1, +0, -1, -1, +0])
        Hexagon.__delta_v = array.array('b', [+0, -1, -1, +0, +1, +1])


    @staticmethod
    def __create_kings_hexagons():

        white_first_hexagons = ["a1", "a2", "a3", "a4", "a5", "a6", "a7"]
        black_first_hexagons = ["i1", "i2", "i3", "i4", "i5", "i6", "i7"]

        white_first_indices = array.array('b', map(lambda x: Hexagon.get(x).index, white_first_hexagons))
        black_first_indices = array.array('b', map(lambda x: Hexagon.get(x).index, black_first_hexagons))

        Hexagon.__king_begin_indices = [None for _ in Player]
        Hexagon.__king_end_indices = [None for _ in Player]

        Hexagon.__king_begin_indices[Player.WHITE] = white_first_indices
        Hexagon.__king_begin_indices[Player.BLACK] = black_first_indices

        Hexagon.__king_end_indices[Player.WHITE] = black_first_indices
        Hexagon.__king_end_indices[Player.BLACK] = white_first_indices


    @staticmethod
    def __create_layout():

        Hexagon.__layout = []

        Hexagon.__layout.append( (2, ["i1", "i2", "i3", "i4", "i5", "i6", "i7"]))
        Hexagon.__layout.append( (1, ["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8"]))
        Hexagon.__layout.append( (2, ["g1", "g2", "g3", "g4", "g5", "g6", "g7"]))
        Hexagon.__layout.append( (1, ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"]))
        Hexagon.__layout.append( (0, ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9"]))
        Hexagon.__layout.append( (1, ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8"]))
        Hexagon.__layout.append( (2, ["c1", "c2", "c3", "c4", "c5", "c6", "c7"]))
        Hexagon.__layout.append( (1, ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"]))
        Hexagon.__layout.append( (2, ["a1", "a2", "a3", "a4", "a5", "a6", "a7"]))


    @staticmethod
    def __create_next_hexagons():

        Hexagon.__next_fst_indices = [None for _ in Hexagon.__all_sorted_hexagons]
        Hexagon.__next_snd_indices = [None for _ in Hexagon.__all_sorted_hexagons]

        for (hexagon_index, hexagon) in enumerate(Hexagon.__all_sorted_hexagons):
            (hexagon_u, hexagon_v) = hexagon.position_uv

            Hexagon.__next_fst_indices[hexagon_index] = array.array('b', [Null.HEXAGON for _ in HexagonDirection])
            Hexagon.__next_snd_indices[hexagon_index] = array.array('b', [Null.HEXAGON for _ in HexagonDirection])

            if not hexagon.reserve:
                for hexagon_dir in HexagonDirection:
                    hexagon_delta_u = Hexagon.__delta_u[hexagon_dir]
                    hexagon_delta_v = Hexagon.__delta_v[hexagon_dir]

                    hexagon_fst_u = hexagon_u + 1*hexagon_delta_u
                    hexagon_fst_v = hexagon_v + 1*hexagon_delta_v

                    hexagon_snd_u = hexagon_u + 2*hexagon_delta_u
                    hexagon_snd_v = hexagon_v + 2*hexagon_delta_v

                    if (hexagon_fst_u, hexagon_fst_v) in Hexagon.__position_uv_to_hexagon:
                        hexagon_fst = Hexagon.__position_uv_to_hexagon[(hexagon_fst_u, hexagon_fst_v)]
                        if not hexagon_fst.reserve:
                            Hexagon.__next_fst_indices[hexagon_index][hexagon_dir] = hexagon_fst.index

                        if (hexagon_snd_u, hexagon_snd_v) in Hexagon.__position_uv_to_hexagon:
                            hexagon_snd = Hexagon.__position_uv_to_hexagon[(hexagon_snd_u, hexagon_snd_v)]
                            if not hexagon_snd.reserve:
                                Hexagon.__next_snd_indices[hexagon_index][hexagon_dir] = hexagon_snd.index


    @staticmethod
    def __create_hexagons():

        # Row "a"
        Hexagon('a1', (-1, -4))
        Hexagon('a2', (-0, -4))
        Hexagon('a3', (1, -4))
        Hexagon('a4', (2, -4))
        Hexagon('a5', (3, -4))
        Hexagon('a6', (4, -4))
        Hexagon('a7', (5, -4))

        Hexagon('a', (6, -4), reserve=True)

        # Row "b"
        Hexagon('b1', (-2, -3))
        Hexagon('b2', (-1, -3))
        Hexagon('b3', (0, -3))
        Hexagon('b4', (1, -3))
        Hexagon('b5', (2, -3))
        Hexagon('b6', (3, -3))
        Hexagon('b7', (4, -3))
        Hexagon('b8', (5, -3))

        Hexagon('b', (6, -3), reserve=True)

        # Row "c"
        Hexagon('c1', (-2, -2))
        Hexagon('c2', (-1, -2))
        Hexagon('c3', (0, -2))
        Hexagon('c4', (1, -2))
        Hexagon('c5', (2, -2))
        Hexagon('c6', (3, -2))
        Hexagon('c7', (4, -2))

        Hexagon('c', (5, -2), reserve=True)

        # Row "d"
        Hexagon('d1', (-3, -1))
        Hexagon('d2', (-2, -1))
        Hexagon('d3', (-1, -1))
        Hexagon('d4', (0, -1))
        Hexagon('d5', (1, -1))
        Hexagon('d6', (2, -1))
        Hexagon('d7', (3, -1))
        Hexagon('d8', (4, -1))

        # Row "e"
        Hexagon('e1', (-4, 0))
        Hexagon('e2', (-3, 0))
        Hexagon('e3', (-2, 0))
        Hexagon('e4', (-1, 0))
        Hexagon('e5', (0, 0))
        Hexagon('e6', (1, 0))
        Hexagon('e7', (2, 0))
        Hexagon('e8', (3, 0))
        Hexagon('e9', (4, 0))

        # Row "f"
        Hexagon('f1', (-4, 1))
        Hexagon('f2', (-3, 1))
        Hexagon('f3', (-2, 1))
        Hexagon('f4', (-1, 1))
        Hexagon('f5', (0, 1))
        Hexagon('f6', (1, 1))
        Hexagon('f7', (2, 1))
        Hexagon('f8', (3, 1))

        # Row "g"
        Hexagon('g', (-5, 2), reserve=True)

        Hexagon('g1', (-4, 2))
        Hexagon('g2', (-3, 2))
        Hexagon('g3', (-2, 2))
        Hexagon('g4', (-1, 2))
        Hexagon('g5', (0, 2))
        Hexagon('g6', (1, 2))
        Hexagon('g7', (2, 2))

        # Row "h"
        Hexagon('h', (-6, 3), reserve=True)

        Hexagon('h1', (-5, 3))
        Hexagon('h2', (-4, 3))
        Hexagon('h3', (-3, 3))
        Hexagon('h4', (-2, 3))
        Hexagon('h5', (-1, 3))
        Hexagon('h6', (0, 3))
        Hexagon('h7', (1, 3))
        Hexagon('h8', (2, 3))

        # Row "i"
        Hexagon('i', (-6, 4), reserve=True)

        Hexagon('i1', (-5, 4))
        Hexagon('i2', (-4, 4))
        Hexagon('i3', (-3, 4))
        Hexagon('i4', (-2, 4))
        Hexagon('i5', (-1, 4))
        Hexagon('i6', (0, 4))
        Hexagon('i7', (1, 4))


class Notation:

    def __init__(self):
        assert False


    @staticmethod
    def drop_cube(src_cube_label, dst_hexagon_name, previous_action=None):
        if previous_action is None:
            notation = ""
        else:
            notation = previous_action.notation + "/"
        notation += src_cube_label + ":" + dst_hexagon_name
        return notation


    @staticmethod
    def move_cube(src_hexagon_name, dst_hexagon_name, capture, previous_action=None):
        if previous_action is None:
            notation = src_hexagon_name + "-" + dst_hexagon_name
        else:
            notation = previous_action.notation + "-" + dst_hexagon_name

        if capture == Capture.NONE:
            pass

        elif capture == Capture.SOME:
            notation += "!"

        elif capture == Capture.KING:
            notation += "!!"

        else:
            assert False

        return notation


    @staticmethod
    def move_stack(src_hexagon_name, dst_hexagon_name, capture, previous_action=None):
        if previous_action is None:
            notation = src_hexagon_name + "=" + dst_hexagon_name
        else:
            notation = previous_action.notation + "=" + dst_hexagon_name

        if capture == Capture.NONE:
            pass

        elif capture == Capture.SOME:
            notation += "!"

        elif capture == Capture.KING:
            notation += "!!"

        else:
            assert False

        return notation


    @staticmethod
    def guess_symmetricals(notation):
        symmetricals = []

        if len(notation) == 9 and notation[1] == ':' and notation[6] == ':':
            # examples: w:a1/w:a2 | m:a1/m:a2
            # >>>>>>>>> 012345678
            cube_1 = notation[0]
            cube_2 = notation[5]
            hexagon_1 = notation[2:4]
            hexagon_2 = notation[7:9]

            if cube_1 == cube_2 and hexagon_1 != hexagon_2:
                symmetricals.append(cube_2 + ":" + hexagon_1 + "/" + cube_1 + ":" + hexagon_2)

        return symmetricals


    @staticmethod
    def relocate_king(src_king_label, dst_hexagon_name, previous_action=None):
        if previous_action is None:
            notation = ""
        else:
            notation = previous_action.notation + "/"
        notation += src_king_label + ":" + dst_hexagon_name
        return notation


class JersiAction:


    def __init__(self, notation, state, capture=Capture.NONE, previous_action=None):
        self.notation = notation
        self.state = state
        self.capture = capture

        if previous_action is not None:
            if previous_action.capture == Capture.KING or self.capture == Capture.KING:
                self.capture = Capture.KING

            elif previous_action.capture == Capture.SOME or self.capture == Capture.SOME:
                self.capture = Capture.SOME

            else:
                self.capture = Capture.NONE


    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                id(self.state) == id(other.state) and
                self.notation == other.notation)


    def __hash__(self):
        return hash((id(self.state), self.notation))


    def __repr__(self):
        return str(self)


    def __str__(self):
        return self.notation



class JersiActionAppender:

    def __init__(self):
        self.__actions = []
        self.__notations = set()


    def append(self, action):
        if action.notation in self.__notations:
            return

        for symmetrical in Notation.guess_symmetricals(action.notation):
            if symmetrical in self.__notations:
                return

        self.__actions.append(action)
        self.__notations.add(action.notation)


    def get_actions(self):
        return self.__actions


class JersiState:

    __max_credit = 40


    def __init__(self):

        self.__cube_status = None
        self.__hexagon_bottom = None
        self.__hexagon_top = None

        self.__credit = JersiState.__max_credit
        self.__player = Player.WHITE
        self.__turn = 1

        self.__actions = None
        self.__actions_by_names = None
        self.__taken = False
        self.__terminal_case = None
        self.__terminated = None
        self.__rewards = None

        self.___init_hexagon_top_and_bottom()
        self.___init_cube_status()


    def __fork(self):

        state = copy.copy(self)

        state.__cube_status = copy.deepcopy(state.__cube_status)
        state.__hexagon_bottom = copy.deepcopy(state.__hexagon_bottom)
        state.__hexagon_top = copy.deepcopy(state.__hexagon_top)

        state.__actions = None
        state.__actions_by_names = None
        state.__taken = False
        state.__terminal_case = None
        state.__terminated = None
        state.__rewards = None

        return state


    def ___init_cube_status(self):

        self.__cube_status = array.array('b', [CubeStatus.ACTIVATED for _ in Cube.all])

        for (cube_index, cube) in enumerate(Cube.all):

            if cube.sort in (CubeSort.MOUNTAIN, CubeSort.WISE):
                self.__cube_status[cube_index] = CubeStatus.RESERVED

            if not (cube_index in self.__hexagon_bottom or cube_index in self.__hexagon_top):
                self.__cube_status[cube_index] = CubeStatus.CAPTURED


    def ___init_hexagon_top_and_bottom(self):

        self.__hexagon_top = array.array('b', [Null.CUBE for _ in Hexagon.all])
        self.__hexagon_bottom = array.array('b', [Null.CUBE for _ in Hexagon.all])

        # whites
        self.__set_cube_at_hexagon_by_names('F1', 'b1')
        self.__set_cube_at_hexagon_by_names('F2', 'b8')
        self.__set_cube_at_hexagon_by_names('K1', 'a4')

        self.__set_cube_at_hexagon_by_names('R1', 'b2')
        self.__set_cube_at_hexagon_by_names('P1', 'b3')
        self.__set_cube_at_hexagon_by_names('S1', 'b4')
        self.__set_cube_at_hexagon_by_names('R2', 'b5')
        self.__set_cube_at_hexagon_by_names('P2', 'b6')
        self.__set_cube_at_hexagon_by_names('S2', 'b7')

        self.__set_cube_at_hexagon_by_names('R3', 'a3')
        self.__set_cube_at_hexagon_by_names('S3', 'a2')
        self.__set_cube_at_hexagon_by_names('P3', 'a1')
        self.__set_cube_at_hexagon_by_names('S4', 'a5')
        self.__set_cube_at_hexagon_by_names('R4', 'a6')
        self.__set_cube_at_hexagon_by_names('P4', 'a7')

        # blacks
        self.__set_cube_at_hexagon_by_names('f1', 'h1')
        self.__set_cube_at_hexagon_by_names('f2', 'h8')
        self.__set_cube_at_hexagon_by_names('k1', 'i4')

        self.__set_cube_at_hexagon_by_names('r1', 'h7')
        self.__set_cube_at_hexagon_by_names('p1', 'h6')
        self.__set_cube_at_hexagon_by_names('s1', 'h5')
        self.__set_cube_at_hexagon_by_names('r2', 'h4')
        self.__set_cube_at_hexagon_by_names('p2', 'h3')
        self.__set_cube_at_hexagon_by_names('s2', 'h2')

        self.__set_cube_at_hexagon_by_names('r3', 'i5')
        self.__set_cube_at_hexagon_by_names('s3', 'i6')
        self.__set_cube_at_hexagon_by_names('p3', 'i7')
        self.__set_cube_at_hexagon_by_names('s4', 'i3')
        self.__set_cube_at_hexagon_by_names('r4', 'i2')
        self.__set_cube_at_hexagon_by_names('p4', 'i1')

        # white reserve
        self.__set_cube_at_hexagon_by_names('W1', 'c')
        self.__set_cube_at_hexagon_by_names('W2', 'c')

        self.__set_cube_at_hexagon_by_names('M1', 'b')
        self.__set_cube_at_hexagon_by_names('M2', 'b')

        self.__set_cube_at_hexagon_by_names('M3', 'a')
        self.__set_cube_at_hexagon_by_names('M4', 'a')

        # black reserve
        self.__set_cube_at_hexagon_by_names('m1', 'i')
        self.__set_cube_at_hexagon_by_names('m2', 'i')

        self.__set_cube_at_hexagon_by_names('m3', 'h')
        self.__set_cube_at_hexagon_by_names('m4', 'h')

        self.__set_cube_at_hexagon_by_names('w1', 'g')
        self.__set_cube_at_hexagon_by_names('w2', 'g')


    def __set_cube_at_hexagon_by_names(self, cube_name, hexagon_name):
        cube_index = Cube.get(cube_name).index
        hexagon_index = Hexagon.get(hexagon_name).index
        self.__set_cube_at_hexagon(cube_index, hexagon_index)


    def __set_cube_at_hexagon(self, cube_index, hexagon_index):

        if self.__hexagon_bottom[hexagon_index] == Null.CUBE:
            # hexagon has zero cube
            self.__hexagon_bottom[hexagon_index] = cube_index

        elif self.__hexagon_top[hexagon_index] == Null.CUBE:
            # hexagon has one cube
            self.__hexagon_top[hexagon_index] = cube_index

        else:
            # hexagon is expected with either zero or one cube
            assert False


    def show(self):

        shift = " " * len("a1KR")

        print()

        for (row_shift_count, row_hexagon_names) in Hexagon.get_layout():

            row_text = shift*row_shift_count

            for hexagon_name in row_hexagon_names:

                row_text += hexagon_name
                hexagon = Hexagon.get(hexagon_name)
                hexagon_index = hexagon.index

                top_index = self.__hexagon_top[hexagon_index]
                bottom_index = self.__hexagon_bottom[hexagon_index]

                if bottom_index == Null.CUBE:
                    row_text += ".."

                elif top_index == Null.CUBE:
                    bottom_label = Cube.all[bottom_index].label
                    row_text += "." + bottom_label

                elif top_index != Null.CUBE:
                    top_label = Cube.all[top_index].label
                    bottom_label = Cube.all[bottom_index].label
                    row_text += top_label + bottom_label

                else:
                    assert False

                row_text += shift
            print(row_text)

        reserved_labels = collections.Counter()
        captured_labels = collections.Counter()

        for (cube_index, cube_status) in enumerate(self.__cube_status):
            cube = Cube.all[cube_index]

            if cube_status == CubeStatus.RESERVED:
                reserved_labels[cube.label] += 1

            elif cube_status == CubeStatus.CAPTURED:
                captured_labels[cube.label] += 1

        print()
        print(f"turn {self.__turn} / player {self.__player} / credit {self.__credit} / " +
              "reserved %s" % " ".join([f"{label}:{count}" for (label, count) in sorted(reserved_labels.items())]) + " / " +
              "captured %s" % " ".join([f"{label}:{count}" for (label, count) in sorted(captured_labels.items())]))


    @staticmethod
    def get_max_credit():
        return JersiState.__max_credit


    @staticmethod
    def set_max_credit(max_credit):
        assert max_credit > 0
        JersiState.__max_credit = max_credit


    def get_current_player(self):
        return self.__player


    def get_hexagon_bottom(self):
        return self.__hexagon_bottom


    def get_hexagon_top(self):
        return self.__hexagon_top


    def get_other_player(self):

        if self.__player == Player.WHITE:
            return Player.BLACK

        elif self.__player == Player.BLACK:
            return Player.WHITE

        else:
            assert False


    def get_rewards(self):
        assert self.is_terminal()
        return self.__rewards


    def get_terminal_case(self):
        return self.__terminal_case


    def get_turn(self):
        return self.__turn


    def take_action(self, action):

        state = action.state

        if state.__taken == False:
            state.__taken = True
            state.__player = state.get_other_player()
            state.__turn += 1
            state.__credit = max(0, state.__credit - 1)

            if action.capture in (Capture.SOME, Capture.KING):
                state.__credit = JersiState.__max_credit

        return state


    def take_action_by_name(self, action_name):
       assert action_name in self.get_action_names()
       action = self.__actions_by_names[action_name]
       self.take_action(action)


    def is_terminal(self):

        if self.__terminated is None:

            self.__terminated = False

            white_captured = self.__cube_status[Cube.white_king_index] == CubeStatus.CAPTURED
            black_captured = self.__cube_status[Cube.black_king_index] == CubeStatus.CAPTURED

            white_arrived = False
            black_arrived = False

            if not (white_captured or black_captured):

                if Cube.white_king_index in self.__hexagon_bottom:
                    hexagon_index = self.__hexagon_bottom.index(Cube.white_king_index)
                    white_arrived = hexagon_index in Hexagon.get_king_end_indices(Player.WHITE)

                else:
                    hexagon_index = self.__hexagon_top.index(Cube.white_king_index)
                    white_arrived = hexagon_index in Hexagon.get_king_end_indices(Player.WHITE)

                if not white_arrived:

                    if Cube.black_king_index in self.__hexagon_bottom:
                        hexagon_index = self.__hexagon_bottom.index(Cube.black_king_index)
                        black_arrived = hexagon_index in Hexagon.get_king_end_indices(Player.BLACK)

                    else:
                        hexagon_index = self.__hexagon_top.index(Cube.black_king_index)
                        black_arrived = hexagon_index in Hexagon.get_king_end_indices(Player.BLACK)

            if white_captured:
                # white king captured without possible relocation ==> black wins
                self.__terminated = True
                self.__terminal_case = TerminalCase.WHITE_CAPTURED
                self.__rewards = [Reward.DRAW for _ in Player]
                self.__rewards[Player.BLACK] = Reward.WIN
                self.__rewards[Player.WHITE] = Reward.LOSS

            elif black_captured:
                # black king captured without possible relocation ==> white wins
                self.__terminated = True
                self.__terminal_case = TerminalCase.BLACK_CAPTURED
                self.__rewards = [Reward.DRAW for _ in Player]
                self.__rewards[Player.WHITE] = Reward.WIN
                self.__rewards[Player.BLACK] = Reward.LOSS

            elif white_arrived:
                # white arrived at goal ==> white wins
                self.__terminated = True
                self.__terminal_case = TerminalCase.WHITE_ARRIVED
                self.__rewards = [Reward.DRAW for _ in Player]
                self.__rewards[Player.WHITE] = Reward.WIN
                self.__rewards[Player.BLACK] = Reward.LOSS

            elif black_arrived:
                # black arrived at goal ==> black wins
                self.__terminated = True
                self.__terminal_case = TerminalCase.BLACK_ARRIVED
                self.__rewards = [Reward.DRAW for _ in Player]
                self.__rewards[Player.BLACK] = Reward.WIN
                self.__rewards[Player.WHITE] = Reward.LOSS

            elif self.__credit == 0:
                # credit is exhausted ==> nobody wins
                self.__terminated = True
                self.__terminal_case = TerminalCase.ZERO_CREDIT
                self.__rewards = [Reward.DRAW for _ in Player]

            elif len(self.get_actions()) == 0:
                # the current player looses and the other player wins
                self.__terminated = True
                self.__rewards = [Reward.DRAW for _ in Player]

                if self.__player == Player.WHITE:
                    self.__terminal_case = TerminalCase.WHITE_BLOCKED
                    self.__rewards[Player.WHITE] = Reward.LOSS
                    self.__rewards[Player.BLACK] = Reward.WIN
                else:
                    self.__terminal_case = TerminalCase.BLACK_BLOCKED
                    self.__rewards[Player.BLACK] = Reward.LOSS
                    self.__rewards[Player.WHITE] = Reward.WIN

        return self.__terminated


    def get_actions(self):
        if self.__actions is None:
            self.__actions = self.__find_drops() + self.__find_moves()
            # Better to shuffle actions here than by MCTS searcher for example
            random.shuffle(self.__actions)
        return self.__actions


    def get_action_names(self):
        if self.__actions_by_names is None:
            self.__actions_by_names = {}
            for action in self.get_actions():
                action_name = action.notation.replace('!', '')
                self.__actions_by_names[action_name] = action

        return list(sorted(self.__actions_by_names.keys()))


    def get_action_by_name(self, action_name):
       assert action_name in self.get_action_names()
       action = self.__actions_by_names[action_name]
       return action


    ### Action finders

    def __find_drops(self):
        action_appender = JersiActionAppender()

        for cube_1_index in self.__find_droppable_cubes():
            for destination_1 in Hexagon.get_all_active_indices():
                action_1 = self.__try_drop(cube_1_index, destination_1)
                if action_1 is not None:
                    action_appender.append(action_1)

                    state_1 = action_1.state.__fork()

                    for cube_2_index in state_1.__find_droppable_cubes():
                        for destination_2 in [destination_1] + Hexagon.get_next_fst_active_indices(destination_1):
                            action_2 = state_1.__try_drop(cube_2_index, destination_2, previous_action=action_1)
                            if action_2 is not None:
                                action_appender.append(action_2)

        return action_appender.get_actions()


    def __find_moves(self):
        actions = self.__find_cube_first_moves() + self.__find_stack_first_moves()
        return self.__find_king_relocations(actions)


    def __find_king_relocations(self, move_actions):

        actions = []

        king_index = Cube.get_king_index(self.get_other_player())
        king = Cube.all[king_index]

        for action in move_actions:
            if action.capture == Capture.KING:
                can_relocate_king = False

                for destination_king in Hexagon.get_king_begin_indices(king.player):
                    action_king = action.state.__try_relocate_king(king_index, destination_king, previous_action=action)
                    if action_king is not None:
                        actions.append(action_king)
                        can_relocate_king = True

                if not can_relocate_king:
                    actions.append(action)

            else:
                actions.append(action)

        return actions


    def __find_cube_first_moves(self):
        actions = []

        for source_1 in self.__find_hexagons_with_movable_cube():

            for direction_1 in HexagonDirection:
                destination_1 = Hexagon.get_next_fst_indices(source_1, direction_1)
                if destination_1 != Null.HEXAGON:
                    action_1 = self.__try_move_cube(source_1, destination_1)
                    if action_1 is not None:
                        actions.append(action_1)

                        state_1 = action_1.state.__fork()
                        if state_1.__is_hexagon_with_movable_stack(destination_1):

                            for direction_2 in HexagonDirection:
                                destination_21 = Hexagon.get_next_fst_indices(destination_1, direction_2)
                                if destination_21 != Null.HEXAGON:
                                    action_21 = state_1.__try_move_stack(destination_1, destination_21, previous_action=action_1)
                                    if action_21 is not None:
                                        actions.append(action_21)

                                    if self.__hexagon_bottom[destination_21] == Null.CUBE:
                                        # stack can cross destination_21 with zero cube
                                        destination_22 = Hexagon.get_next_snd_indices(destination_1, direction_2)
                                        if destination_22 != Null.HEXAGON:
                                            action_22 = state_1.__try_move_stack(destination_1, destination_22, previous_action=action_1)
                                            if action_22 is not None:
                                                actions.append(action_22)
        return actions


    def __find_stack_first_moves(self):
        actions = []

        for source_1 in self.__find_hexagons_with_movable_stack():

            for direction_1 in HexagonDirection:
                destination_11 = Hexagon.get_next_fst_indices(source_1, direction_1)
                if destination_11 != Null.HEXAGON:
                    action_11 = self.__try_move_stack(source_1, destination_11)
                    if action_11 is not None:
                        actions.append(action_11)

                        state_11 = action_11.state.__fork()

                        for direction_21 in HexagonDirection:
                            destination_21 = Hexagon.get_next_fst_indices(destination_11, direction_21)
                            if destination_21 != Null.HEXAGON:
                                action_21 = state_11.__try_move_cube(destination_11, destination_21, previous_action=action_11)
                                if action_21 is not None:
                                    actions.append(action_21)

                    if self.__hexagon_bottom[destination_11] == Null.CUBE:
                        # stack can cross destination_11 with zero cube
                        destination_12 = Hexagon.get_next_snd_indices(source_1, direction_1)
                        if destination_12 != Null.HEXAGON:
                            action_12 = self.__try_move_stack(source_1, destination_12)
                            if action_12 is not None:
                                actions.append(action_12)

                                state_12 = action_12.state.__fork()

                                for direction_22 in HexagonDirection:
                                    destination_22 = Hexagon.get_next_fst_indices(destination_12, direction_22)
                                    if destination_22 != Null.HEXAGON:
                                        action_22 = state_12.__try_move_cube(destination_12, destination_22, previous_action=action_12)
                                        if action_22 is not None:
                                            actions.append(action_22)
        return actions

    ### Cubes and hexagons finders

    def __find_droppable_cubes(self):
        droppable_cubes = []

        mountain_found = False
        wise_found = False

        for (src_cube_index, src_cube_status) in enumerate(self.__cube_status):
            if src_cube_status == CubeStatus.RESERVED:
                cube = Cube.all[src_cube_index]
                if cube.player == self.__player:

                    if cube.sort == CubeSort.MOUNTAIN and not mountain_found:
                        droppable_cubes.append(src_cube_index)
                        mountain_found = True

                    elif cube.sort == CubeSort.WISE and not wise_found:
                        droppable_cubes.append(src_cube_index)
                        wise_found = True

                    if mountain_found and wise_found:
                        break
        return droppable_cubes


    def __find_hexagons_with_movable_cube(self):
         return [x for x in Hexagon.get_all_active_indices() if self.__is_hexagon_with_movable_cube(x)]


    def __find_hexagons_with_movable_stack(self):
        return [x for x in Hexagon.get_all_active_indices() if self.__is_hexagon_with_movable_stack(x)]

    ### Hexagon predicates

    def __is_hexagon_with_movable_cube(self, hexagon_index):
        to_be_returned = False

        if Hexagon.all[hexagon_index].reserve:
            to_be_returned = False

        elif self.__hexagon_top[hexagon_index] != Null.CUBE:
            cube_index = self.__hexagon_top[hexagon_index]
            cube = Cube.all[cube_index]
            if cube.player == self.__player and cube.sort != CubeSort.MOUNTAIN:
                to_be_returned = True

        elif self.__hexagon_bottom[hexagon_index] != Null.CUBE:
            cube_index = self.__hexagon_bottom[hexagon_index]
            cube = Cube.all[cube_index]
            if cube.player == self.__player and cube.sort != CubeSort.MOUNTAIN:
                to_be_returned = True

        return to_be_returned


    def __is_hexagon_with_movable_stack(self, hexagon_index):
        to_be_returned = False

        if Hexagon.all[hexagon_index].reserve:
            to_be_returned = False

        else:
            top_index = self.__hexagon_top[hexagon_index]
            bottom_index = self.__hexagon_bottom[hexagon_index]

            if top_index != Null.CUBE and bottom_index != Null.CUBE:

                top = Cube.all[top_index]
                bottom = Cube.all[bottom_index]

                if (top.player == self.__player and bottom.player == self.__player and
                    top.sort != CubeSort.MOUNTAIN and bottom.sort != CubeSort.MOUNTAIN):
                    to_be_returned = True

        return to_be_returned

    ### Action triers

    def __try_drop(self, src_cube_index, dst_hexagon_index, previous_action=None):

        src_cube = Cube.all[src_cube_index]
        src_cube_label = src_cube.label
        dst_hexagon_name = Hexagon.all[dst_hexagon_index].name
        notation = Notation.drop_cube(src_cube_label, dst_hexagon_name, previous_action=previous_action)

        if src_cube.player != self.__player:
            action = None

        elif src_cube.sort not in (CubeSort.MOUNTAIN, CubeSort.WISE):
            action = None

        elif self.__cube_status[src_cube_index] != CubeStatus.RESERVED:
            action = None

        elif Hexagon.all[dst_hexagon_index].reserve:
            action = None

        elif self.__hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has zero cube

            state = self.__fork()

            if src_cube_index in state.__hexagon_top:
                src_hexagon_index = state.__hexagon_top.index(src_cube_index)
                state.__hexagon_top[src_hexagon_index] = Null.CUBE
            else:
                src_hexagon_index = state.__hexagon_bottom.index(src_cube_index)
                state.__hexagon_bottom[src_hexagon_index] = Null.CUBE

            assert Hexagon.all[src_hexagon_index].reserve

            state.__hexagon_bottom[dst_hexagon_index] = src_cube_index
            state.__cube_status[src_cube_index] = CubeStatus.ACTIVATED
            action = JersiAction(notation, state)

        elif self.__hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube

            dst_bottom_index = self.__hexagon_bottom[dst_hexagon_index]
            dst_bottom = Cube.all[dst_bottom_index]

            if dst_bottom.player != self.__player:
                action = None

            elif dst_bottom.sort == CubeSort.KING:
                action = None

            elif src_cube.sort == CubeSort.MOUNTAIN and dst_bottom.sort != CubeSort.MOUNTAIN:
                action = None

            else:
                state = self.__fork()

                if src_cube_index in state.__hexagon_top:
                    src_hexagon_index = state.__hexagon_top.index(src_cube_index)
                    state.__hexagon_top[src_hexagon_index] = Null.CUBE
                else:
                    src_hexagon_index = state.__hexagon_bottom.index(src_cube_index)
                    state.__hexagon_bottom[src_hexagon_index] = Null.CUBE

                assert Hexagon.all[src_hexagon_index].reserve

                state.__hexagon_top[dst_hexagon_index] = src_cube_index
                state.__cube_status[src_cube_index] = CubeStatus.ACTIVATED
                action = JersiAction(notation, state)

        else:
            # destination hexagon has two cubes
            action = None

        return action


    def __try_relocate_king(self, king_index, dst_hexagon_index, previous_action=None):

        king = Cube.all[king_index]
        king_label = king.label
        dst_hexagon_name = Hexagon.all[dst_hexagon_index].name

        if king.sort != CubeSort.KING:
            action = None

        elif king.player == self.__player:
            action = None

        elif self.__cube_status[king_index] != CubeStatus.CAPTURED:
            action = None

        elif dst_hexagon_index not in Hexagon.get_king_begin_indices(king.player):
            action = None

        elif self.__hexagon_top[dst_hexagon_index] != Null.CUBE:
            # hexagon has two cubes
            action = None

        elif self.__hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # hexagon has zero cube

            state = self.__fork()
            state.__hexagon_bottom[dst_hexagon_index] = king_index
            state.__cube_status[king_index] = CubeStatus.ACTIVATED
            notation = Notation.relocate_king(king_label, dst_hexagon_name, previous_action=previous_action)
            action = JersiAction(notation, state, capture=Capture.KING, previous_action=previous_action)

        else:
            # hexagon has one cube

            dst_bottom_index = self.__hexagon_bottom[dst_hexagon_index]
            dst_bottom = Cube.all[dst_bottom_index]

            if dst_bottom.player == king.player or dst_bottom.sort == CubeSort.MOUNTAIN:

                state = self.__fork()
                state.__hexagon_top[dst_hexagon_index] = king_index
                state.__cube_status[king_index] = CubeStatus.ACTIVATED
                notation = Notation.relocate_king(king_label, dst_hexagon_name, previous_action=previous_action)
                action = JersiAction(notation, state, capture=Capture.KING, previous_action=previous_action)

            else:
                action = None

        return action


    def __try_move_cube(self, src_hexagon_index, dst_hexagon_index, previous_action=None):

        src_hexagon_name = Hexagon.all[src_hexagon_index].name
        dst_hexagon_name = Hexagon.all[dst_hexagon_index].name

        if not self.__is_hexagon_with_movable_cube(src_hexagon_index):
            action = None

        elif Hexagon.all[dst_hexagon_index].reserve:
            action = None

        elif self.__hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has zero cube

            state = self.__fork()

            if state.__hexagon_top[src_hexagon_index] != Null.CUBE:
                src_cube_index = state.__hexagon_top[src_hexagon_index]
                state.__hexagon_top[src_hexagon_index] = Null.CUBE
            else:
                src_cube_index = state.__hexagon_bottom[src_hexagon_index]
                state.__hexagon_bottom[src_hexagon_index] = Null.CUBE
            state.__hexagon_bottom[dst_hexagon_index] = src_cube_index

            notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=Capture.NONE, previous_action=previous_action)
            action = JersiAction(notation, state, previous_action=previous_action)

        elif self.__hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube

            dst_bottom_index = self.__hexagon_bottom[dst_hexagon_index]
            dst_bottom = Cube.all[dst_bottom_index]

            if self.__hexagon_top[src_hexagon_index] != Null.CUBE:
                src_cube_index = self.__hexagon_top[src_hexagon_index]
            else:
                src_cube_index = self.__hexagon_bottom[src_hexagon_index]
            src_cube = Cube.all[src_cube_index]

            if dst_bottom.sort == CubeSort.MOUNTAIN:
                state = self.__fork()

                if state.__hexagon_top[src_hexagon_index] != Null.CUBE:
                    state.__hexagon_top[src_hexagon_index] = Null.CUBE
                else:
                    state.__hexagon_bottom[src_hexagon_index] = Null.CUBE
                state.__hexagon_top[dst_hexagon_index] = src_cube_index

                notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=Capture.NONE, previous_action=previous_action)
                action = JersiAction(notation, state, previous_action=previous_action)

            elif dst_bottom.player != self.__player:

                if src_cube.beats(dst_bottom):
                    # Capture the bottom cube

                    state = self.__fork()

                    state.__hexagon_bottom[dst_hexagon_index] = Null.CUBE
                    state.__cube_status[dst_bottom_index] = CubeStatus.CAPTURED

                    if dst_bottom.sort == CubeSort.KING:
                        capture = Capture.KING
                    else:
                        capture = Capture.SOME

                    if state.__hexagon_top[src_hexagon_index] != Null.CUBE:
                        state.__hexagon_top[src_hexagon_index] = Null.CUBE
                    else:
                        state.__hexagon_bottom[src_hexagon_index] = Null.CUBE
                    state.__hexagon_bottom[dst_hexagon_index] = src_cube_index

                    notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                    action = JersiAction(notation, state, capture=capture, previous_action=previous_action)
                else:
                    action = None

            elif dst_bottom.sort == CubeSort.KING:
                action = None

            else:
                state = self.__fork()

                if state.__hexagon_top[src_hexagon_index] != Null.CUBE:
                    state.__hexagon_top[src_hexagon_index] = Null.CUBE
                else:
                    state.__hexagon_bottom[src_hexagon_index] = Null.CUBE
                state.__hexagon_top[dst_hexagon_index] = src_cube_index

                notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=Capture.NONE, previous_action=previous_action)
                action = JersiAction(notation, state, previous_action=previous_action)

        else:
            # destination hexagon has two cubes
            dst_top_index = self.__hexagon_top[dst_hexagon_index]
            dst_bottom_index = self.__hexagon_bottom[dst_hexagon_index]

            dst_top = Cube.all[dst_top_index]
            dst_bottom = Cube.all[dst_bottom_index]

            if self.__hexagon_top[src_hexagon_index] != Null.CUBE:
                src_cube_index = self.__hexagon_top[src_hexagon_index]
            else:
                src_cube_index = self.__hexagon_bottom[src_hexagon_index]
            src_cube = Cube.all[src_cube_index]

            if dst_top.player == self.__player:
                action = None

            elif src_cube.beats(dst_top) and dst_bottom.sort == CubeSort.MOUNTAIN:
                # Capture the top of the stack
                state = self.__fork()

                state.__hexagon_top[dst_hexagon_index] = Null.CUBE
                state.__cube_status[dst_top_index] = CubeStatus.CAPTURED

                if dst_top.sort == CubeSort.KING:
                    capture = Capture.KING
                else:
                    capture = Capture.SOME

                if state.__hexagon_top[src_hexagon_index] != Null.CUBE:
                    state.__hexagon_top[src_hexagon_index] = Null.CUBE
                else:
                    state.__hexagon_bottom[src_hexagon_index] = Null.CUBE
                state.__hexagon_top[dst_hexagon_index] = src_cube_index

                notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                action = JersiAction(notation, state, capture=capture, previous_action=previous_action)

            elif src_cube.beats(dst_top) and dst_bottom.sort != CubeSort.MOUNTAIN:
                # Capture the stack
                state = self.__fork()

                state.__hexagon_top[dst_hexagon_index] = Null.CUBE
                state.__hexagon_bottom[dst_hexagon_index] = Null.CUBE

                state.__cube_status[dst_top_index] = CubeStatus.CAPTURED
                state.__cube_status[dst_bottom_index] = CubeStatus.CAPTURED

                if dst_top.sort == CubeSort.KING:
                    capture = Capture.KING
                else:
                    capture = Capture.SOME

                if state.__hexagon_top[src_hexagon_index] != Null.CUBE:
                    state.__hexagon_top[src_hexagon_index] = Null.CUBE
                else:
                    state.__hexagon_bottom[src_hexagon_index] = Null.CUBE
                state.__hexagon_bottom[dst_hexagon_index] = src_cube_index

                notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                action = JersiAction(notation, state, capture=capture, previous_action=previous_action)

            else:
                action = None

        return action


    def __try_move_stack(self, src_hexagon_index, dst_hexagon_index, previous_action=None):

        src_hexagon_name = Hexagon.all[src_hexagon_index].name
        dst_hexagon_name = Hexagon.all[dst_hexagon_index].name

        if not self.__is_hexagon_with_movable_cube(src_hexagon_index):
            action = None

        elif Hexagon.all[dst_hexagon_index].reserve:
            action = None

        elif self.__hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has zero cube

            state = self.__fork()

            src_bottom_index = state.__hexagon_bottom[src_hexagon_index]
            src_top_index = state.__hexagon_top[src_hexagon_index]

            state.__hexagon_bottom[src_hexagon_index] = Null.CUBE
            state.__hexagon_top[src_hexagon_index] = Null.CUBE

            state.__hexagon_bottom[dst_hexagon_index] = src_bottom_index
            state.__hexagon_top[dst_hexagon_index] = src_top_index

            notation = Notation.move_stack(src_hexagon_name, dst_hexagon_name, capture=Capture.NONE, previous_action=previous_action)
            action = JersiAction(notation, state, previous_action=previous_action)

        elif self.__hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube

            src_bottom_index = self.__hexagon_bottom[src_hexagon_index]
            src_top_index = self.__hexagon_top[src_hexagon_index]

            src_top = Cube.all[src_top_index]

            dst_bottom_index = self.__hexagon_bottom[dst_hexagon_index]
            dst_bottom = Cube.all[dst_bottom_index]

            if src_top.player == dst_bottom.player:
                action = None

            elif src_top.beats(dst_bottom):
                # capture the bottom cube
                state = self.__fork()

                state.__hexagon_bottom[dst_hexagon_index] = Null.CUBE
                state.__cube_status[dst_bottom_index] = CubeStatus.CAPTURED

                if dst_bottom.sort == CubeSort.KING:
                    capture = Capture.KING
                else:
                    capture = Capture.SOME

                state.__hexagon_bottom[src_hexagon_index] = Null.CUBE
                state.__hexagon_top[src_hexagon_index] = Null.CUBE

                state.__hexagon_bottom[dst_hexagon_index] = src_bottom_index
                state.__hexagon_top[dst_hexagon_index] = src_top_index

                notation = Notation.move_stack(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                action = JersiAction(notation, state, capture=capture, previous_action=previous_action)

            else:
                action = None

        else:
            # destination hexagon has two cubes

            src_top_index = self.__hexagon_top[src_hexagon_index]
            src_top = Cube.all[src_top_index]

            src_bottom_index = self.__hexagon_bottom[src_hexagon_index]

            dst_top_index = self.__hexagon_top[dst_hexagon_index]
            dst_top = Cube.all[dst_top_index]

            dst_bottom_index = self.__hexagon_bottom[dst_hexagon_index]
            dst_bottom = Cube.all[dst_bottom_index]

            if src_top.player == dst_top.player:
                action = None

            elif src_top.beats(dst_top) and dst_bottom.sort != CubeSort.MOUNTAIN:
                # capture the stack
                state = self.__fork()

                state.__hexagon_bottom[dst_hexagon_index] = Null.CUBE
                state.__hexagon_top[dst_hexagon_index] = Null.CUBE

                state.__cube_status[dst_bottom_index] = CubeStatus.CAPTURED
                state.__cube_status[dst_top_index] = CubeStatus.CAPTURED

                if dst_top.sort == CubeSort.KING:
                    capture = Capture.KING
                else:
                    capture = Capture.SOME

                state.__hexagon_bottom[src_hexagon_index] = Null.CUBE
                state.__hexagon_top[src_hexagon_index] = Null.CUBE

                state.__hexagon_bottom[dst_hexagon_index] = src_bottom_index
                state.__hexagon_top[dst_hexagon_index] = src_top_index

                notation = Notation.move_stack(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                action = JersiAction(notation, state, capture=capture, previous_action=previous_action)

            else:
                action = None

        return action


class MctsState:
    """Adaptater to mcts.StateInterface for JersiState"""

    def __init__(self, jersi_state, maximizer_player):
        self.__jersi_state = jersi_state
        self.__maximizer_player = maximizer_player


    def getCurrentPlayer(self):
       """ Returns 1 if it is the maximizer player's turn to choose an action,
       or -1 for the minimiser player"""
       return 1 if self.__jersi_state.get_current_player() == self.__maximizer_player else -1


    def isTerminal(self):
        return self.__jersi_state.is_terminal()


    def getReward(self):
        """Returns the reward for this state: 0 for a draw,
        positive for a win by maximizer player or negative for a win by the minimizer player.
        Only needed for terminal states."""

        jersi_rewards = self.__jersi_state.get_rewards()

        if jersi_rewards[self.__maximizer_player] == Reward.DRAW:
            mcts_reward = 0

        elif jersi_rewards[self.__maximizer_player] == Reward.WIN:
            mcts_reward = 1

        else:
            mcts_reward = -1

        return mcts_reward


    def getPossibleActions(self):
        return self.__jersi_state.get_actions()


    def takeAction(self, action):
        return MctsState(self.__jersi_state.take_action(action), self.__maximizer_player)


def extractStatistics(mcts_searcher, action):
    statistics = {}
    statistics['rootNumVisits'] = mcts_searcher.root.numVisits
    statistics['rootTotalReward'] = mcts_searcher.root.totalReward
    statistics['actionNumVisits'] = mcts_searcher.root.children[action].numVisits
    statistics['actionTotalReward'] = mcts_searcher.root.children[action].totalReward
    return statistics


class HumanSearcher():


    def __init__(self, name):
        self.__name = name
        self.__action_name = None
        self.__use_command_line = False


    def get_name(self):
        return self.__name


    def is_interactive(self):
        return True


    def use_command_line(self, condition):
        assert condition in (True, False)
        self.__use_command_line = condition


    def set_action_name(self, action_name):
        assert not self.__use_command_line
        self.__action_name = action_name


    def search(self, state):

        if self.__use_command_line:
            return self.__search_using_command_line(state)

        else:
            action = state.get_action_by_name(self.__action_name)
            self.__action_name = None
            return action


    def __search_using_command_line(self, state):
        assert self.__use_command_line

        action_names = state.get_action_names()

        if False:
            with open(os.path.join(_script_home, "actions.txt"), 'w') as stream:
                for x in action_names:
                    stream.write(x + "\n")

        input_name_validated = False
        while not input_name_validated:
            input_name = input("HumanSearcher: action? ").strip()
            if input_name in action_names:
                input_name_validated = True
            else:
                print(f"action {input_name} is not valid ..." )

        action = state.get_action_by_name(input_name)

        print(f"HumanSearcher: action {action} has been selected")

        return action


class RandomSearcher():


    def __init__(self, name):
        self.__name = name


    def get_name(self):
        return self.__name


    def is_interactive(self):
        return False


    def search(self, state):
        actions = state.get_actions()
        action = random.choice(actions)
        return action


class MctsSearcher():


    def __init__(self, name, time_limit=None, iteration_limit=None):
        self.__name = name

        default_time_limit = 1_000

        assert time_limit is None or iteration_limit is None

        if time_limit is None and iteration_limit is None:
            time_limit = default_time_limit

        self.__time_limit = time_limit
        self.__iteration_limit = iteration_limit


        if self.__time_limit is not None:
            # time in milli-seconds
            self.__searcher = mcts.mcts(timeLimit=self.__time_limit)

        elif self.__iteration_limit is not None:
            # number of mcts rounds
            self.__searcher = mcts.mcts(iterationLimit=self.__iteration_limit)


    def get_name(self):
        return self.__name


    def is_interactive(self):
        return False


    def search(self, state):

        action = self.__searcher.search(initialState=MctsState(state, state.get_current_player()))

        statistics = extractStatistics(self.__searcher, action)
        print("mcts statitics:" +
              f" chosen action= {statistics['actionTotalReward']} total reward" +
              f" over {statistics['actionNumVisits']} visits /"
              f" all explored actions= {statistics['rootTotalReward']} total reward" +
              f" over {statistics['rootNumVisits']} visits")

        if _do_debug:
            for (child_action, child) in self.__searcher.root.children.items():
                print(f"    action {child_action} numVisits={child.numVisits} totalReward={child.totalReward}")

        return action


class SearcherCatalog:


    def __init__(self):
        self.__catalog = {}


    def add(self, searcher):
        searcher_name = searcher.get_name()
        assert searcher_name not in self.__catalog
        self.__catalog[searcher_name] = searcher


    def get_names(self):
        return list(sorted(self.__catalog.keys()))


    def get(self, name):
        assert name in self.__catalog
        return self.__catalog[name]


SEARCHER_CATALOG = SearcherCatalog()

SEARCHER_CATALOG.add( HumanSearcher("human") )
SEARCHER_CATALOG.add( RandomSearcher("random") )

SEARCHER_CATALOG.add( MctsSearcher("mcts-s-1", time_limit=1_000) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-s-2", time_limit=2_000) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-s-10", time_limit=10_000) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-s-20", time_limit=20_000) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-s-30", time_limit=30_000) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-s-60", time_limit=60_000) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-m-5", time_limit=5*60_000) )

SEARCHER_CATALOG.add( MctsSearcher("mcts-i-10", iteration_limit=10) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-i-50", iteration_limit=50) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-i-100", iteration_limit=100) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-i-500", iteration_limit=500) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-i-1k", iteration_limit=1_000) )
SEARCHER_CATALOG.add( MctsSearcher("mcts-i-10k", iteration_limit=10_000) )


class Game:

    def __init__(self):
        self.__searcher = [None, None]

        self.__jersi_state = None
        self.__log = None


    def set_white_searcher(self, searcher):
        self.__searcher[Player.WHITE] = searcher


    def set_black_searcher(self, searcher):
        self.__searcher[Player.BLACK] = searcher


    def start(self):

        assert self.__searcher[Player.WHITE] is not None
        assert self.__searcher[Player.BLACK] is not None

        self.__jersi_state = JersiState()

        self.__jersi_state.show()

        self.__log = ""


    def get_log(self):
        return self.__log


    def get_state(self):
        return self.__jersi_state


    def has_next_turn(self):
        return not self.__jersi_state.is_terminal()


    def next_turn(self):

        self.__log = ""

        if self.has_next_turn():
            player = self.__jersi_state.get_current_player()
            player_name = f"{Player.name(player)}-{self.__searcher[player].get_name()}"
            action_count = len(self.__jersi_state.get_actions())

            print()
            print(f"{player_name} is thinking ...")

            action = self.__searcher[player].search(self.__jersi_state)

            print(f"{player_name} is done")

            turn = self.__jersi_state.get_turn()

            self.__log = f"turn {turn} : {player_name} selects {action} amongst {action_count} actions"
            print(self.__log)
            print("-"*40)

            self.__jersi_state = self.__jersi_state.take_action(action)
            self.__jersi_state.show()

        if self.__jersi_state.is_terminal():

            rewards = self.__jersi_state.get_rewards()
            player = self.__jersi_state.get_current_player()

            print()
            print("-"*40)

            white_player = f"{Player.name(Player.WHITE)}-{self.__searcher[Player.WHITE].get_name()}"
            black_player = f"{Player.name(Player.BLACK)}-{self.__searcher[Player.BLACK].get_name()}"

            if rewards[Player.WHITE] == rewards[Player.BLACK]:
                self.__log = f"nobody wins ; the game is a draw between {white_player} and {black_player}"
                print(self.__log)

            elif rewards[Player.WHITE] > rewards[Player.BLACK]:
                self.__log = f"{white_player} wins against {black_player}"
                print(self.__log)

            else:
                self.__log = f"{black_player} wins against {white_player}"
                print(self.__log)


def test_game_between_random_players():

    print("=====================================")
    print(" test_game_between_random_players ...")
    print("=====================================")

    default_max_credit = JersiState.get_max_credit()
    JersiState.set_max_credit(10_000)

    game = Game()

    game.set_white_searcher(SEARCHER_CATALOG.get("random"))
    game.set_black_searcher(SEARCHER_CATALOG.get("random"))

    game.start()

    while game.has_next_turn():
        game.next_turn()

    JersiState.set_max_credit(default_max_credit)

    print("=====================================")
    print("test_game_between_random_players done")
    print("=====================================")


def test_game_between_mcts_players():

    print("==================================")
    print("test_game_between_mcts_players ...")
    print("==================================")

    default_max_credit = JersiState.get_max_credit()
    JersiState.set_max_credit(10)

    game = Game()

    game.set_white_searcher(SEARCHER_CATALOG.get("mcts-s-10"))
    game.set_black_searcher(SEARCHER_CATALOG.get("mcts-i-10"))

    game.start()

    while game.has_next_turn():
        game.next_turn()

    JersiState.set_max_credit(default_max_credit)

    print("===================================")
    print("test_game_between_mcts_players done")
    print("===================================")


def test_game_between_random_and_human_players():

    print("==============================================")
    print("test_game_between_random_and_human_players ...")
    print("==============================================")

    default_max_credit = JersiState.get_max_credit()
    JersiState.set_max_credit(10)

    game = Game()

    game.set_white_searcher(SEARCHER_CATALOG.get("human"))
    game.set_black_searcher(SEARCHER_CATALOG.get("random"))
    SEARCHER_CATALOG.get("human").use_command_line(True)

    game.start()

    while game.has_next_turn():
        game.next_turn()

    JersiState.set_max_credit(default_max_credit)
    SEARCHER_CATALOG.get("human").use_command_line(False)

    print("===============================================")
    print("test_game_between_random_and_human_players done")
    print("===============================================")


def main():
    print("Hello")
    print(_COPYRIGHT_AND_LICENSE)

    if True:
        test_game_between_random_players()

    if True:
        test_game_between_mcts_players()

    if False:
        test_game_between_random_and_human_players()

    print("Bye")


Cube.init()
Hexagon.init()


if __name__ == "__main__":
    main()
