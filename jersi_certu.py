#!/usr/bin/env python3


import array
import collections
import copy
import cProfile
import enum
import os
import random
import sys


_no_assert = False
_do_debug = True

_script_home = os.path.abspath(os.path.dirname(__file__))
_mcts_home = os.path.join(_script_home, "packages", "MCTS-lucasborboleta-4e62716-changed")
sys.path.append(_mcts_home)


import mcts


def rgb_color_as_hexadecimal(rgb_triplet):
    (red, green, blue) = rgb_triplet
    assert _no_assert or 0 <= red <= 255
    assert _no_assert or 0 <= green <= 255
    assert _no_assert or 0 <= red <= 255
    return '#%02x%02x%02x' % (red, green, blue)


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
class HexagonColor(enum.Enum):
    BORDER = rgb_color_as_hexadecimal((191, 89, 52))
    DARK = rgb_color_as_hexadecimal((166, 109, 60))
    LIGHT = rgb_color_as_hexadecimal((242, 202, 128))
    RESERVE = rgb_color_as_hexadecimal((191, 184, 180))


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
            assert _no_assert or False


@enum.unique
class Reward(enum.IntEnum):
    WIN = 1
    DRAW = 0
    LOSS = -1

    assert _no_assert or LOSS < DRAW < WIN
    assert _no_assert or DRAW == 0
    assert _no_assert or LOSS + WIN == DRAW


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

    __all_sorted = []
    __king_index = None
    __name_to_cube = {}
    __sort_and_player_to_label = {}


    def __init__(self, name, label, sort, player):
        """Create a cube and check its properties"""

        assert _no_assert or name not in Cube.__name_to_cube
        assert _no_assert or len(name) == 2
        assert _no_assert or len(label) == 1
        assert _no_assert or label == name[0]

        assert _no_assert or sort in CubeSort
        assert _no_assert or player in Player

        if player == Player.WHITE:
            assert _no_assert or label == label.upper()
        elif player == Player.BLACK:
            assert _no_assert or label == label.lower()
        else:
            assert _no_assert or False

        if (sort, player) not in Cube.__sort_and_player_to_label:
            Cube.__sort_and_player_to_label[(sort, player)] = label
        else:
            assert _no_assert or Cube.__sort_and_player_to_label[(sort, player)] == label

        self.name = name
        self.label = label
        self.sort = sort
        self.player = player
        self.index = None

        Cube.__name_to_cube[self.name] = self


    def __str__(self):
        return f"Cube({self.name}, {self.label}, {self.sort}, {self.player})"


    def beats(self, other):

        if self.player != other.player:

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
                does_beat = other.sort in (CubeSort.ROCK, CubeSort.PAPER, CubeSort.SCISSORS, CubeSort.FOUL, CubeSort.KING, CubeSort.WISE)
        else:
            does_beat = False

        return does_beat


    @staticmethod
    def get(name):
        return Cube.__name_to_cube[name]


    @staticmethod
    def get_all():
        return Cube.__all_sorted


    @staticmethod
    def get_king_index(player):
        return Cube.__king_index[player]


    @staticmethod
    def show_all():
        for cube in Cube.__all_sorted:
            print(cube)


    @staticmethod
    def init():
        Cube.__create_cubes()
        Cube.__create_all_sorted()
        Cube.__create_king_index()


    @staticmethod
    def __create_all_sorted():
        for name in sorted(Cube.__name_to_cube.keys()):
            Cube.__all_sorted.append(Cube.__name_to_cube[name])

        for (index, cube) in enumerate(Cube.__all_sorted):
            cube.index = index


    @staticmethod
    def __create_king_index():
        Cube.__king_index = array.array('b', [Null.CUBE for _ in Player])
        Cube.__king_index[Player.WHITE] = Cube.get('K1').index
        Cube.__king_index[Player.BLACK] = Cube.get('k1').index


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

    __all_sorted = []
    __king_begins = []
    __king_ends = []
    __layout = []
    __name_to_hexagon = {}
    __next_fst = []
    __next_snd = []
    __position_uv_to_hexagon = {}


    def __init__(self, name, position_uv, reserve=False):

        assert _no_assert or name not in Hexagon.__name_to_hexagon
        assert _no_assert or len(position_uv) == 2
        assert _no_assert or reserve in [True, False]
        assert _no_assert or position_uv not in Hexagon.__position_uv_to_hexagon

        if reserve:
            assert _no_assert or len(name) == 1
        else:
            assert _no_assert or len(name) == 2

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
        return Hexagon.__all_sorted


    @staticmethod
    def get_king_begins():
        return Hexagon.__king_begins


    @staticmethod
    def get_king_ends():
        return Hexagon.__king_ends


    @staticmethod
    def get_layout():
        return Hexagon.__layout


    @staticmethod
    def get_next_fst():
        return Hexagon.__next_fst


    @staticmethod
    def get_next_snd():
        return Hexagon.__next_snd


    @staticmethod
    def show_all():
        for hexagon in Hexagon.__all_sorted:
            print(hexagon)


    @staticmethod
    def init():
        Hexagon.__create_hexagons()
        Hexagon.__create_all_sorted()
        Hexagon.__create_layout()
        Hexagon.__create_kings_hexagons()
        Hexagon.__create_delta_u_and_v()
        Hexagon.__create_next_hexagons()


    @staticmethod
    def __create_all_sorted():
        for name in sorted(Hexagon.__name_to_hexagon.keys()):
            Hexagon.__all_sorted.append(Hexagon.__name_to_hexagon[name])

        for (index, hexagon) in enumerate(Hexagon.__all_sorted):
            hexagon.index = index


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

        Hexagon.__king_begins = [None for _ in Player]
        Hexagon.__king_ends = [None for _ in Player]

        Hexagon.__king_begins[Player.WHITE] = white_first_indices
        Hexagon.__king_begins[Player.BLACK] = black_first_indices

        Hexagon.__king_ends[Player.WHITE] = black_first_indices
        Hexagon.__king_ends[Player.BLACK] = white_first_indices


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

        Hexagon.__next_fst = [None for _ in Hexagon.__all_sorted]
        Hexagon.__next_snd = [None for _ in Hexagon.__all_sorted]

        for (hexagon_index, hexagon) in enumerate(Hexagon.__all_sorted):
            (hexagon_u, hexagon_v) = hexagon.position_uv

            Hexagon.__next_fst[hexagon_index] = array.array('b', [Null.HEXAGON for _ in HexagonDirection])
            Hexagon.__next_snd[hexagon_index] = array.array('b', [Null.HEXAGON for _ in HexagonDirection])

            if not hexagon.reserve:
                for hexagon_direction in HexagonDirection:
                    hexagon_delta_u = Hexagon.__delta_u[hexagon_direction]
                    hexagon_delta_v = Hexagon.__delta_v[hexagon_direction]

                    hexagon_fst_u = hexagon_u + 1*hexagon_delta_u
                    hexagon_fst_v = hexagon_v + 1*hexagon_delta_v

                    hexagon_snd_u = hexagon_u + 2*hexagon_delta_u
                    hexagon_snd_v = hexagon_v + 2*hexagon_delta_v

                    if (hexagon_fst_u, hexagon_fst_v) in Hexagon.__position_uv_to_hexagon:
                        hexagon_fst = Hexagon.__position_uv_to_hexagon[(hexagon_fst_u, hexagon_fst_v)]
                        if not hexagon_fst.reserve:
                            Hexagon.__next_fst[hexagon_index][hexagon_direction] = hexagon_fst.index

                        if (hexagon_snd_u, hexagon_snd_v) in Hexagon.__position_uv_to_hexagon:
                            hexagon_snd = Hexagon.__position_uv_to_hexagon[(hexagon_snd_u, hexagon_snd_v)]
                            if not hexagon_snd.reserve:
                                Hexagon.__next_snd[hexagon_index][hexagon_direction] = hexagon_snd.index


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


class GraphicalHexagon:

    __all_sorted = []
    __name_to_hexagon = {}


    def __init__(self, hexagon, color, shift_xy=None):

        assert _no_assert or hexagon.name not in GraphicalHexagon.__name_to_hexagon
        assert _no_assert or color in HexagonColor
        assert _no_assert or (shift_xy is not None) == hexagon.reserve

        self.name = hexagon.name
        self.position_uv = hexagon.position_uv
        self.reserve = hexagon.reserve
        self.index = hexagon.index
        self.color = color
        self.shift_xy = shift_xy

        GraphicalHexagon.__name_to_hexagon[self.name] = self


    def __str__(self):
        return f"GraphicalHexagon({self.name}, {self.position_uv}, {self.reserve}, {self.index}, {self.color}, {self.shift_xy})"


    @staticmethod
    def get(name):
        return GraphicalHexagon.__name_to_hexagon[name]


    @staticmethod
    def get_all():
        return GraphicalHexagon.__all_sorted


    @staticmethod
    def show_all():
        for hexagon in GraphicalHexagon.__all_sorted:
            print(hexagon)


    @staticmethod
    def init():
        GraphicalHexagon.__create_hexagons()
        GraphicalHexagon.__create_all_sorted()


    @staticmethod
    def __create_all_sorted():
        for name in sorted(GraphicalHexagon.__name_to_hexagon.keys()):
            GraphicalHexagon.__all_sorted.append(GraphicalHexagon.__name_to_hexagon[name])


    @staticmethod
    def __create_hexagons():

        borders = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7']
        borders += ['i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7']
        borders += ['b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1']
        borders += ['b8', 'c7', 'd8', 'e9', 'f8', 'g7', 'h8']

        darks = ['c3', 'c4', 'c5']
        darks += ['g3', 'g4', 'g5']
        darks += ['d3', 'e3', 'f3']
        darks += ['d6', 'e7', 'f6']
        darks += ['e5']

        for hexagon in Hexagon.get_all():

            if hexagon.reserve:
                color = HexagonColor.RESERVE

                if hexagon.name == 'a':
                    shift_xy = (0.75, -1.00)

                elif hexagon.name == 'b':
                    shift_xy = (0.25, 0.00)

                elif hexagon.name == 'c':
                    shift_xy = (0.75, 1.00)

                elif hexagon.name == 'g':
                    shift_xy = (-0.75, -1.00)

                elif hexagon.name == 'h':
                    shift_xy = (-0.25, 0.00)

                elif hexagon.name == 'i':
                    shift_xy = (-0.75, 1.00)

                else:
                    assert _no_assert or False

            elif hexagon.name in borders:
                color = HexagonColor.BORDER
                shift_xy = None

            elif hexagon.name in darks:
                color = HexagonColor.DARK
                shift_xy = None
            else:
                color = HexagonColor.LIGHT
                shift_xy = None

            GraphicalHexagon(hexagon, color, shift_xy)


class Notation:

    def __init__(self):
        pass


    @staticmethod
    def drop_cube(src_cube_label, dst_hexagon_name, previous_action=None):
        if previous_action is None:
            notation = ""
        else:
            notation = previous_action.notation + "/"
        notation += src_cube_label + ":" + dst_hexagon_name
        return notation


    @staticmethod
    def relocate_king(src_king_label, dst_hexagon_name, previous_action=None):
        if previous_action is None:
            notation = ""
        else:
            notation = previous_action.notation + "/"
        notation += src_king_label + ":" + dst_hexagon_name
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
            cube1 = notation[0]
            cube2 = notation[5]
            hexagon1 = notation[2:4]
            hexagon2 = notation[7:9]

            if cube1 == cube2 and hexagon1 != hexagon2:
                symmetricals.append(cube2 + ":" + hexagon1 + "/" + cube1 + ":" + hexagon2)

        return symmetricals


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


    def __str__(self):
        return str(self.notation)


    def __repr__(self):
        return str(self)


    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.notation == other.notation


    def __hash__(self):
        return hash(self.notation)


class ActionAppender:

    def __init__(self):
        self.__actions = []
        self.__notations = set()


    def get_actions(self):
        return self.__actions


    def append(self, action):
        if action.notation in self.__notations:
            return

        for symmetrical in Notation.guess_symmetricals(action.notation):
            if symmetrical in self.__notations:
                return

        self.__actions.append(action)
        self.__notations.add(action.notation)


class JersiState:

    #__max_credit = 40
    __max_credit = 10

    def __init__(self):

        # Shortcut to global references
        self.cubes = Cube.get_all()
        self.cube_count = len(Cube.get_all())
        self.hexagons = Hexagon.get_all()
        self.hexagon_count = len(Hexagon.get_all())
        self.white_king_index = Cube.get_king_index(Player.WHITE)
        self.black_king_index = Cube.get_king_index(Player.BLACK)

        # Real JersiState attributes

        self.cube_status = None
        self.hexagon_bottom = None
        self.hexagon_top = None

        self.player = Player.WHITE
        self.turn = 1
        self.credit = JersiState.__max_credit

        self.taken = False
        self.terminated = None
        self.terminal_case = None
        self.rewards = None
        self.actions = None

        self.___init_cube_status()
        self.___init_hexagon_top_and_bottom()


    def ___init_cube_status(self):

        self.cube_status = array.array('b', [CubeStatus.ACTIVATED for _ in range(self.cube_count)])

        for (cube_index, cube) in enumerate(self.cubes):
            if cube.sort in (CubeSort.MOUNTAIN, CubeSort.WISE):
                self.cube_status[cube_index] = CubeStatus.RESERVED


    def ___init_hexagon_top_and_bottom(self):

        self.hexagon_top = array.array('b', [Null.CUBE for _ in range(self.hexagon_count)])
        self.hexagon_bottom = array.array('b', [Null.CUBE for _ in range(self.hexagon_count)])

        # whites
        self.set_cube_at_hexagon_by_names('F1', 'b1')
        self.set_cube_at_hexagon_by_names('F2', 'b8')
        self.set_cube_at_hexagon_by_names('K1', 'a4')

        self.set_cube_at_hexagon_by_names('R1', 'b2')
        self.set_cube_at_hexagon_by_names('P1', 'b3')
        self.set_cube_at_hexagon_by_names('S1', 'b4')
        self.set_cube_at_hexagon_by_names('R2', 'b5')
        self.set_cube_at_hexagon_by_names('P2', 'b6')
        self.set_cube_at_hexagon_by_names('S2', 'b7')

        self.set_cube_at_hexagon_by_names('R3', 'a3')
        self.set_cube_at_hexagon_by_names('S3', 'a2')
        self.set_cube_at_hexagon_by_names('P3', 'a1')
        self.set_cube_at_hexagon_by_names('S4', 'a5')
        self.set_cube_at_hexagon_by_names('R4', 'a6')
        self.set_cube_at_hexagon_by_names('P4', 'a7')

        # blacks
        self.set_cube_at_hexagon_by_names('f1', 'h1')
        self.set_cube_at_hexagon_by_names('f2', 'h8')
        self.set_cube_at_hexagon_by_names('k1', 'i4')

        self.set_cube_at_hexagon_by_names('r1', 'h7')
        self.set_cube_at_hexagon_by_names('p1', 'h6')
        self.set_cube_at_hexagon_by_names('s1', 'h5')
        self.set_cube_at_hexagon_by_names('r2', 'h4')
        self.set_cube_at_hexagon_by_names('p2', 'h3')
        self.set_cube_at_hexagon_by_names('s2', 'h2')

        self.set_cube_at_hexagon_by_names('r3', 'i5')
        self.set_cube_at_hexagon_by_names('s3', 'i6')
        self.set_cube_at_hexagon_by_names('p3', 'i7')
        self.set_cube_at_hexagon_by_names('s4', 'i3')
        self.set_cube_at_hexagon_by_names('r4', 'i2')
        self.set_cube_at_hexagon_by_names('p4', 'i1')

        # white reserve
        self.set_cube_at_hexagon_by_names('W1', 'c')
        self.set_cube_at_hexagon_by_names('W2', 'c')

        self.set_cube_at_hexagon_by_names('M1', 'b')
        self.set_cube_at_hexagon_by_names('M2', 'b')

        self.set_cube_at_hexagon_by_names('M3', 'a')
        self.set_cube_at_hexagon_by_names('M4', 'a')

        # black reserve
        self.set_cube_at_hexagon_by_names('m1', 'i')
        self.set_cube_at_hexagon_by_names('m2', 'i')

        self.set_cube_at_hexagon_by_names('m3', 'h')
        self.set_cube_at_hexagon_by_names('m4', 'h')

        self.set_cube_at_hexagon_by_names('w1', 'g')
        self.set_cube_at_hexagon_by_names('w2', 'g')


    def set_cube_at_hexagon_by_names(self, cube_name, hexagon_name):
        cube_index = Cube.get(cube_name).index
        hexagon_index = Hexagon.get(hexagon_name).index
        self.set_cube_at_hexagon(cube_index, hexagon_index)


    def set_cube_at_hexagon(self, cube_index, hexagon_index):

        if self.hexagon_bottom[hexagon_index] == Null.CUBE:
            # hexagon has zero cube
            self.hexagon_bottom[hexagon_index] = cube_index

        elif self.hexagon_top[hexagon_index] == Null.CUBE:
            # hexagon has one cube
            self.hexagon_top[hexagon_index] = cube_index

        else:
            # hexagon is expected with either zero or one cube
            assert _no_assert or False


    def move_cube(self, src_hexagon_index, dst_hexagon_index):

        assert _no_assert or not self.hexagons[src_hexagon_index].reserve
        assert _no_assert or not self.hexagons[dst_hexagon_index].reserve

        if self.hexagon_top[src_hexagon_index] != Null.CUBE:
            # source hexagon has two cubes
            cube_index = self.hexagon_top[src_hexagon_index]
            self.hexagon_top[src_hexagon_index] = Null.CUBE

        elif self.hexagon_bottom[src_hexagon_index] != Null.CUBE:
            # source hexagon has one cube
            cube_index = self.hexagon_bottom[src_hexagon_index]
            self.hexagon_bottom[src_hexagon_index] = Null.CUBE

        else:
            # source hexagon is expected with either one or two cubes
            assert _no_assert or False

        assert _no_assert or self.cube_status[cube_index] == CubeStatus.ACTIVATED
        cube = self.cubes[cube_index]
        assert _no_assert or cube.player == self.player
        assert _no_assert or cube.sort != CubeSort.MOUNTAIN

        if self.hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has zero cube
            self.hexagon_bottom[dst_hexagon_index] = cube_index

        elif self.hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube
            self.hexagon_top[dst_hexagon_index] = cube_index

            bottom_cube = self.cubes[self.hexagon_bottom[dst_hexagon_index]]
            assert _no_assert or bottom_cube.sort != CubeSort.KING
            assert _no_assert or cube.player == bottom_cube.player or bottom_cube.sort == CubeSort.MOUNTAIN

        else:
            # destination hexagon is expected with either zero or one cube
            assert _no_assert or False


    def move_stack(self, src_hexagon_index, dst_hexagon_index):

        assert _no_assert or not self.hexagons[src_hexagon_index].reserve
        assert _no_assert or not self.hexagons[dst_hexagon_index].reserve

        bottom_cube_index = self.hexagon_bottom[src_hexagon_index]
        top_cube_index = self.hexagon_top[src_hexagon_index]
        self.hexagon_bottom[src_hexagon_index] = Null.CUBE
        self.hexagon_top[src_hexagon_index] = Null.CUBE

        # source hexagon is expected with two cubes
        assert _no_assert or bottom_cube_index != Null.CUBE
        assert _no_assert or top_cube_index != Null.CUBE

        # destination hexagon is expected with zero cube
        assert _no_assert or self.hexagon_bottom[dst_hexagon_index] == Null.CUBE
        assert _no_assert or self.hexagon_top[dst_hexagon_index] == Null.CUBE

        # moved cubes are expected to be movable
        assert _no_assert or self.cube_status[bottom_cube_index] == CubeStatus.ACTIVATED
        assert _no_assert or self.cube_status[top_cube_index] == CubeStatus.ACTIVATED
        bottom_cube = self.cubes[bottom_cube_index]
        top_cube = self.cubes[top_cube_index]
        assert _no_assert or bottom_cube.player == self.player
        assert _no_assert or top_cube.player == self.player
        assert _no_assert or bottom_cube.sort != CubeSort.MOUNTAIN
        assert _no_assert or top_cube.sort != CubeSort.MOUNTAIN

        self.hexagon_bottom[dst_hexagon_index] = bottom_cube_index
        self.hexagon_top[dst_hexagon_index] = top_cube_index


    def drop_cube(self, cube_index, dst_hexagon_index):

        assert _no_assert or not self.hexagons[dst_hexagon_index].reserve
        assert _no_assert or self.cube_status[cube_index] == CubeStatus.RESERVED
        cube = self.cubes[cube_index]
        assert _no_assert or cube.sort in [CubeSort.MOUNTAIN, CubeSort.WISE]
        assert _no_assert or cube.player == self.player

        if cube_index in self.hexagon_top:
            src_hexagon_index = self.hexagon_top.index(cube_index)
            self.hexagon_top[src_hexagon_index] = Null.CUBE

        else:
            src_hexagon_index = self.hexagon_bottom.index(cube_index)
            self.hexagon_bottom[src_hexagon_index] = Null.CUBE

        assert _no_assert or self.hexagons[src_hexagon_index].reserve

        if self.hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has zero cube
            self.hexagon_bottom[dst_hexagon_index] = cube_index

        elif self.hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube
            self.hexagon_top[dst_hexagon_index] = cube_index

            bottom_cube = self.cubes[self.hexagon_bottom[dst_hexagon_index]]
            assert _no_assert or bottom_cube.player == self.player
            assert _no_assert or bottom_cube.sort != CubeSort.KING
            if cube.sort == CubeSort.MOUNTAIN:
                assert _no_assert or bottom_cube.sort == CubeSort.MOUNTAIN

        else:
            # destination hexagon is expected with either zero or one cube
            assert _no_assert or False

        self.cube_status[cube_index] = CubeStatus.ACTIVATED


    def relocate_king(self, king_index, dst_hexagon_index):

        king_cube = self.cubes[king_index]
        assert _no_assert or king_cube.sort == CubeSort.KING
        assert _no_assert or king_cube.player != self.player
        assert _no_assert or self.cube_status[king_index] == CubeStatus.CAPTURED
        assert _no_assert or dst_hexagon_index in Hexagon.get_king_ends()[self.player] # equivalent to king_begins of other player

        if self.hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has zero cube
            self.hexagon_bottom[dst_hexagon_index] = king_index

        elif self.hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube
            self.hexagon_top[dst_hexagon_index] = king_index

            bottom_cube_index = self.hexagon_bottom[dst_hexagon_index]
            bottom_cube = self.cubes[bottom_cube_index]
            assert _no_assert or bottom_cube.player == king_cube.player or bottom_cube.sort == CubeSort.MOUNTAIN
            assert _no_assert or bottom_cube.sort != CubeSort.KING

        else:
            # destination hexagon is expected with either zero or one cube
            assert _no_assert or False

        self.cube_status[king_index] = CubeStatus.ACTIVATED


    def capture_cube(self, src_hexagon_index, dst_hexagon_index):
        """Capture but do not move"""

        assert _no_assert or not self.hexagons[src_hexagon_index].reserve
        assert _no_assert or not self.hexagons[dst_hexagon_index].reserve

        if self.hexagon_top[src_hexagon_index] != Null.CUBE:
            # source hexagon has two cubes
            cube_index = self.hexagon_top[src_hexagon_index]

        elif self.hexagon_bottom[src_hexagon_index] != Null.CUBE:
            # source hexagon has one cube
            cube_index = self.hexagon_bottom[src_hexagon_index]

        else:
            # source hexagon is expected with either one or two cubes
            assert _no_assert or False

        assert _no_assert or self.cube_status[cube_index] == CubeStatus.ACTIVATED
        cube = self.cubes[cube_index]
        assert _no_assert or cube.player == self.player
        assert _no_assert or cube.sort != CubeSort.MOUNTAIN

        if self.hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon is expected with either one or two cubes
            assert _no_assert or False

        elif self.hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube
            bottom_cube_index = self.hexagon_bottom[dst_hexagon_index]
            bottom_cube = self.cubes[bottom_cube_index]
            assert _no_assert or cube.beats(bottom_cube)

            self.cube_status[bottom_cube_index] = CubeStatus.CAPTURED
            self.hexagon_bottom[dst_hexagon_index] = Null.CUBE

        else:
            # destination hexagon has two cubes
            bottom_cube_index = self.hexagon_bottom[dst_hexagon_index]
            bottom_cube = self.cubes[bottom_cube_index]
            assert _no_assert or bottom_cube.sort == CubeSort.MOUNTAIN

            top_cube_index = self.hexagon_top[dst_hexagon_index]
            top_cube = self.cubes[top_cube_index]
            assert _no_assert or cube.beats(top_cube)

            self.cube_status[top_cube_index] = CubeStatus.CAPTURED
            self.hexagon_top[dst_hexagon_index] = Null.CUBE


    def capture_stack(self, src_hexagon_index, dst_hexagon_index):
        """Capture but do not move"""

        assert _no_assert or not self.hexagons[src_hexagon_index].reserve
        assert _no_assert or not self.hexagons[dst_hexagon_index].reserve

        if self.hexagon_top[src_hexagon_index] != Null.CUBE:
            # source hexagon has two cubes
            cube_index = self.hexagon_top[src_hexagon_index]

        elif self.hexagon_bottom[src_hexagon_index] != Null.CUBE:
            # source hexagon has one cube
            cube_index = self.hexagon_bottom[src_hexagon_index]

        else:
            # source hexagon is expected with either one or two cubes
            assert _no_assert or False

        assert _no_assert or self.cube_status[cube_index] == CubeStatus.ACTIVATED
        cube = self.cubes[cube_index]
        assert _no_assert or cube.player == self.player
        assert _no_assert or cube.sort != CubeSort.MOUNTAIN

        top_cube_index = self.hexagon_top[dst_hexagon_index]
        top_cube = self.cubes[top_cube_index]
        assert _no_assert or cube.beats(top_cube)

        bottom_cube_index = self.hexagon_bottom[dst_hexagon_index]
        bottom_cube = self.cubes[bottom_cube_index]
        assert _no_assert or bottom_cube.sort != CubeSort.MOUNTAIN

        self.cube_status[top_cube_index] = CubeStatus.CAPTURED
        self.cube_status[bottom_cube_index] = CubeStatus.CAPTURED

        self.hexagon_top[dst_hexagon_index] = Null.CUBE
        self.hexagon_bottom[dst_hexagon_index] = Null.CUBE


    def show(self):

        shift = " " * len("a1KR")

        print()

        for (row_shift_count, row_hexagon_names) in Hexagon.get_layout():

            row_text = shift*row_shift_count

            for hexagon_name in row_hexagon_names:

                row_text += hexagon_name
                hexagon = Hexagon.get(hexagon_name)
                hexagon_index = hexagon.index

                top_index = self.hexagon_top[hexagon_index]
                bottom_index = self.hexagon_bottom[hexagon_index]

                if bottom_index == Null.CUBE:
                    row_text += ".."

                elif top_index == Null.CUBE:
                    bottom_label = self.cubes[bottom_index].label
                    row_text += "." + bottom_label

                elif top_index != Null.CUBE:
                    top_label = self.cubes[top_index].label
                    bottom_label = self.cubes[bottom_index].label
                    row_text += top_label + bottom_label

                else:
                    assert _no_assert or False

                row_text += shift
            print(row_text)

        reserved_labels = collections.Counter()
        captured_labels = collections.Counter()

        for (cube_index, cube_status) in enumerate(self.cube_status):
            cube = self.cubes[cube_index]

            if cube_status == CubeStatus.RESERVED:
                reserved_labels[cube.label] += 1

            elif cube_status == CubeStatus.CAPTURED:
                captured_labels[cube.label] += 1

        print()
        print(f"turn {self.turn} / player {self.player} / credit {self.credit} / " +
              "reserved %s" % " ".join([f"{label}:{count}" for (label, count) in sorted(reserved_labels.items())]) + " / " +
              "captured %s" % " ".join([f"{label}:{count}" for (label, count) in sorted(captured_labels.items())]))


    def fork(self):

        state = copy.copy(self)

        state.cube_status = copy.deepcopy(state.cube_status)
        state.hexagon_bottom = copy.deepcopy(state.hexagon_bottom)
        state.hexagon_top = copy.deepcopy(state.hexagon_top)

        state.taken = False
        state.terminated = None
        state.rewards = None
        state.actions = None

        return state


    def get_current_player(self):
        return self.player


    def get_other_player(self):
        if self.player == Player.WHITE:
            return Player.BLACK
        else:
             return Player.WHITE


    def get_rewards(self):
        assert _no_assert or self.is_terminal()
        return self.rewards


    def take_action(self, action):
        # use_fork = True

        # if use_fork:
        #     state = action.state.fork()
        # else:
        #     assert action.state is not None
        #     state = action.state
        #     action.state = None

        state = action.state

        if state.taken == False:
            state.taken = True
            state.player = state.get_other_player()
            state.turn += 1
            state.credit = max(0, state.credit - 1)

            if action.capture in (Capture.SOME, Capture.KING):
                state.credit = JersiState.__max_credit

        return state


    def is_terminal(self):

        if self.terminated is None:

            self.terminated = False

            white_captured = self.cube_status[self.white_king_index] == CubeStatus.CAPTURED
            black_captured = self.cube_status[self.black_king_index] == CubeStatus.CAPTURED

            white_arrived = False
            black_arrived = False

            if not (white_captured or black_captured):

                if self.white_king_index in self.hexagon_bottom:
                    hexagon_index = self.hexagon_bottom.index(self.white_king_index)
                    white_arrived = hexagon_index in Hexagon.get_king_ends()[Player.WHITE]

                else:
                    hexagon_index = self.hexagon_top.index(self.white_king_index)
                    white_arrived = hexagon_index in Hexagon.get_king_ends()[Player.WHITE]

                if not white_arrived:

                    if self.black_king_index in self.hexagon_bottom:
                        hexagon_index = self.hexagon_bottom.index(self.black_king_index)
                        black_arrived = hexagon_index in Hexagon.get_king_ends()[Player.BLACK]

                    else:
                        hexagon_index = self.hexagon_top.index(self.black_king_index)
                        black_arrived = hexagon_index in Hexagon.get_king_ends()[Player.BLACK]

            if white_captured:
                # white king captured without possible relocation ==> black wins
                self.terminated = True
                self.terminal_case = TerminalCase.WHITE_CAPTURED
                self.rewards = [Reward.DRAW for _ in Player]
                self.rewards[Player.BLACK] = Reward.WIN
                self.rewards[Player.WHITE] = Reward.LOSS

            elif black_captured:
                # black king captured without possible relocation ==> white wins
                self.terminated = True
                self.terminal_case = TerminalCase.BLACK_CAPTURED
                self.rewards = [Reward.DRAW for _ in Player]
                self.rewards[Player.WHITE] = Reward.WIN
                self.rewards[Player.BLACK] = Reward.LOSS

            elif white_arrived:
                # white arrived at goal ==> white wins
                self.terminated = True
                self.terminal_case = TerminalCase.WHITE_ARRIVED
                self.rewards = [Reward.DRAW for _ in Player]
                self.rewards[Player.WHITE] = Reward.WIN
                self.rewards[Player.BLACK] = Reward.LOSS

            elif black_arrived:
                # black arrived at goal ==> black wins
                self.terminated = True
                self.terminal_case = TerminalCase.BLACK_ARRIVED
                self.rewards = [Reward.DRAW for _ in Player]
                self.rewards[Player.BLACK] = Reward.WIN
                self.rewards[Player.WHITE] = Reward.LOSS

            elif self.credit == 0:
                # credit is exhausted ==> nobody wins
                self.terminated = True
                self.terminal_case = TerminalCase.ZERO_CREDIT
                self.rewards = [Reward.DRAW for _ in Player]
                self.rewards[Player.WHITE] = Reward.DRAW
                self.rewards[Player.BLACK] = Reward.DRAW

            elif len(self.get_actions()) == 0:
                # the current player looses and the other player wins
                self.terminated = True
                self.rewards = [Reward.DRAW for _ in Player]

                if self.player == Player.WHITE:
                    self.terminal_case = TerminalCase.WHITE_BLOCKED
                    self.rewards[Player.WHITE] = Reward.LOSS
                    self.rewards[Player.BLACK] = Reward.WIN
                else:
                    self.terminal_case = TerminalCase.BLACK_BLOCKED
                    self.rewards[Player.BLACK] = Reward.LOSS
                    self.rewards[Player.WHITE] = Reward.WIN

        return self.terminated


    def get_actions(self):
        if self.actions is None:
            self.actions = self.find_drops() + self.find_moves()
        return self.actions


    def try_drop(self, src_cube_index, dst_hexagon_index, previous_action=None):

        src_cube_label = self.cubes[src_cube_index].label
        dst_hexagon_name = self.hexagons[dst_hexagon_index].name
        notation = Notation.drop_cube(src_cube_label, dst_hexagon_name, previous_action=previous_action)

        if self.hexagons[dst_hexagon_index].reserve:
            action = None

        elif self.hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has zero cube
            state = self.fork()
            state.drop_cube(src_cube_index, dst_hexagon_index)
            action = JersiAction(notation, state)

        elif self.hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube
            bottom_cube_index = self.hexagon_bottom[dst_hexagon_index]
            bottom_cube = self.cubes[bottom_cube_index]
            top_cube = self.cubes[src_cube_index]

            if bottom_cube.player != self.player:
                action = None

            elif bottom_cube.sort == CubeSort.KING:
                action = None

            elif top_cube.sort == CubeSort.MOUNTAIN and bottom_cube.sort != CubeSort.MOUNTAIN:
                action = None

            else:
                state = self.fork()
                state.drop_cube(src_cube_index, dst_hexagon_index)
                action = JersiAction(notation, state)

        else:
            # destination hexagon has two cubes
            action = None

        return action


    def find_droppable_cubes(self):
        droppable_cubes = []

        mountain_found = False
        wise_found = False

        for (src_cube_index, src_cube_status) in enumerate(self.cube_status):
            if src_cube_status == CubeStatus.RESERVED:
                cube = self.cubes[src_cube_index]
                if cube.player == self.player:

                    if cube.sort == CubeSort.MOUNTAIN and not mountain_found:
                        droppable_cubes.append(src_cube_index)
                        mountain_found = True

                    elif cube.sort == CubeSort.WISE and not wise_found:
                        droppable_cubes.append(src_cube_index)
                        wise_found = True

                    if mountain_found and wise_found:
                        break
        return droppable_cubes


    def find_drops(self):
        action_appender = ActionAppender()

        for cube1_index in self.find_droppable_cubes():
            hexagons1 = range(self.hexagon_count)
            for dst1_hexagon_index in hexagons1:

                action1 = self.try_drop(cube1_index, dst1_hexagon_index)
                if action1 is not None:
                    action_appender.append(action1)

                    state1 = action1.state.fork()

                    for cube2_index in state1.find_droppable_cubes():
                        hexagons2 = [dst1_hexagon_index] + [x for x in Hexagon.get_next_fst()[dst1_hexagon_index] if x != Null.HEXAGON]
                        for dst2_hexagon_index in hexagons2:

                            action2 = state1.try_drop(cube2_index, dst2_hexagon_index, previous_action=action1)
                            if action2 is not None:
                                action_appender.append(action2)
        return action_appender.get_actions()


    def is_hexagon_with_movable_cube(self, hexagon_index):
        to_be_returned = False

        if self.hexagons[hexagon_index].reserve:
            to_be_returned = False

        elif self.hexagon_top[hexagon_index] != Null.CUBE:
            cube_index = self.hexagon_top[hexagon_index]
            cube = self.cubes[cube_index]
            if cube.player == self.player and cube.sort != CubeSort.MOUNTAIN:
                to_be_returned = True

        elif self.hexagon_bottom[hexagon_index] != Null.CUBE:
            cube_index = self.hexagon_bottom[hexagon_index]
            cube = self.cubes[cube_index]
            if cube.player == self.player and cube.sort != CubeSort.MOUNTAIN:
                to_be_returned = True

        return to_be_returned


    def is_hexagon_with_movable_stack(self, hexagon_index):
        to_be_returned = False

        if self.hexagons[hexagon_index].reserve:
            to_be_returned = False

        else:
            top_cube_index = self.hexagon_top[hexagon_index]
            bottom_cube_index = self.hexagon_bottom[hexagon_index]

            if top_cube_index != Null.CUBE and bottom_cube_index != Null.CUBE:
                top_cube = self.cubes[top_cube_index]
                bottom_cube = self.cubes[bottom_cube_index]

                if (top_cube.player == self.player and bottom_cube.player == self.player and
                    top_cube.sort != CubeSort.MOUNTAIN and bottom_cube.sort != CubeSort.MOUNTAIN):
                    to_be_returned = True

        return to_be_returned


    def find_hexagons_with_movable_cube(self):
         return [x for x in range(self.hexagon_count) if self.is_hexagon_with_movable_cube(x)]


    def find_hexagons_with_movable_stack(self):
        return [x for x in range(self.hexagon_count) if self.is_hexagon_with_movable_stack(x)]


    def find_moves(self):

        actions = []

        other_player = self.get_other_player()
        king_index = Cube.get_king_index(other_player)
        king = self.cubes[king_index]
        king_label = king.label

        dst_hexagons = Hexagon.get_king_begins()[other_player]

        for action in self.find_cube_first_moves() + self.find_stack_first_moves():
            if action.capture == Capture.KING:
                # try to relocate king
                can_relocate_king = False
                state = action.state

                for dst1_hexagon_index in dst_hexagons:
                    dst1_name = self.hexagons[dst1_hexagon_index].name

                    if state.hexagon_top[dst1_hexagon_index] != Null.CUBE:
                        # hexagon has two cubes
                        pass

                    elif state.hexagon_bottom[dst1_hexagon_index] == Null.CUBE:
                        # hexagon has zero cube
                        state1 = state.fork()
                        state1.relocate_king(king_index, dst1_hexagon_index)
                        notation1 = Notation.relocate_king(king_label, dst1_name, previous_action=action)
                        action1 = JersiAction(notation1, state1, capture=Capture.SOME, previous_action=action)
                        actions.append(action1)
                        can_relocate_king = True

                    else:
                        # hexagon has one cube
                        bottom_cube_index = state.hexagon_bottom[dst1_hexagon_index]
                        bottom_cube = self.cubes[bottom_cube_index]
                        if (bottom_cube.player == king.player or bottom_cube.sort == CubeSort.MOUNTAIN) and bottom_cube.sort != CubeSort.KING:
                            state1 = state.fork()
                            state1.relocate_king(king_index, dst1_hexagon_index)
                            notation1 = Notation.relocate_king(king_label, dst1_name, previous_action=action)
                            action1 = JersiAction(notation1, state1, capture=Capture.SOME, previous_action=action)
                            actions.append(action1)
                            can_relocate_king = True

                if not can_relocate_king:
                    actions.append(action)

            else:
                actions.append(action)

        return actions


    def try_move_cube(self, src_hexagon_index, dst_hexagon_index, previous_action=None):
        src_hexagon_name = self.hexagons[src_hexagon_index].name
        dst_hexagon_name = self.hexagons[dst_hexagon_index].name

        if self.hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has zero cube
            state = self.fork()
            state.move_cube(src_hexagon_index, dst_hexagon_index)
            notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=Capture.NONE, previous_action=previous_action)
            action = JersiAction(notation, state, previous_action=previous_action)

        elif self.hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube
            bottom_cube_index = self.hexagon_bottom[dst_hexagon_index]
            bottom_cube = self.cubes[bottom_cube_index]

            if self.hexagon_top[src_hexagon_index] != Null.CUBE:
                cube_index = self.hexagon_top[src_hexagon_index]
            else:
                cube_index = self.hexagon_bottom[src_hexagon_index]
            cube = self.cubes[cube_index]

            if bottom_cube.sort == CubeSort.MOUNTAIN:
                state = self.fork()
                state.move_cube(src_hexagon_index, dst_hexagon_index)
                notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=Capture.NONE, previous_action=previous_action)
                action = JersiAction(notation, state, previous_action=previous_action)

            elif bottom_cube.player != self.player:
                # Try to capture the bottom cube
                if cube.beats(bottom_cube):
                    state = self.fork()
                    state.capture_cube(src_hexagon_index, dst_hexagon_index)
                    state.move_cube(src_hexagon_index, dst_hexagon_index)
                    if bottom_cube.sort == CubeSort.KING:
                        capture = Capture.KING
                    else:
                        capture = Capture.SOME
                    notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                    action = JersiAction(notation, state, capture=capture, previous_action=previous_action)
                else:
                    action = None

            elif bottom_cube.sort == CubeSort.KING:
                action = None

            else:
                state = self.fork()
                state.move_cube(src_hexagon_index, dst_hexagon_index)
                notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=Capture.NONE, previous_action=previous_action)
                action = JersiAction(notation, state, previous_action=previous_action)

        else:
            # destination hexagon has two cubes
            top_cube_index = self.hexagon_top[dst_hexagon_index]
            bottom_cube_index = self.hexagon_bottom[dst_hexagon_index]
            top_cube = self.cubes[top_cube_index]
            bottom_cube = self.cubes[bottom_cube_index]

            if self.hexagon_top[src_hexagon_index] != Null.CUBE:
                cube_index = self.hexagon_top[src_hexagon_index]
            else:
                cube_index = self.hexagon_bottom[src_hexagon_index]
            cube = self.cubes[cube_index]

            if top_cube.player == self.player:
                action = None

            else:
                if top_cube.player != self.player:
                    if bottom_cube.sort != CubeSort.MOUNTAIN:
                        # Try to capture the stack
                        if cube.beats(top_cube):
                            state = self.fork()
                            state.capture_stack(src_hexagon_index, dst_hexagon_index)
                            state.move_cube(src_hexagon_index, dst_hexagon_index)
                            if top_cube.sort == CubeSort.KING:
                                capture = Capture.KING
                            else:
                                capture = Capture.SOME

                            notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                            action = JersiAction(notation, state, capture=capture, previous_action=previous_action)

                        else:
                            action = None
                    else:
                        # Try to capture the top of the stack
                        if cube.beats(top_cube):
                            state = self.fork()
                            state.capture_cube(src_hexagon_index, dst_hexagon_index)
                            state.move_cube(src_hexagon_index, dst_hexagon_index)
                            if top_cube.sort == CubeSort.KING:
                                capture = Capture.KING
                            else:
                                capture = Capture.SOME

                            notation = Notation.move_cube(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                            action = JersiAction(notation, state, capture=capture, previous_action=previous_action)
                        else:
                            action = None

                else:
                    action = None

        return action


    def try_move_stack(self, src_hexagon_index, dst_hexagon_index, previous_action=None):
        src_hexagon_name = self.hexagons[src_hexagon_index].name
        dst_hexagon_name = self.hexagons[dst_hexagon_index].name

        if self.hexagon_bottom[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has zero cube
            state = self.fork()
            state.move_stack(src_hexagon_index, dst_hexagon_index)
            notation = Notation.move_stack(src_hexagon_name, dst_hexagon_name, capture=Capture.NONE, previous_action=previous_action)
            action = JersiAction(notation, state, previous_action=previous_action)

        elif self.hexagon_top[dst_hexagon_index] == Null.CUBE:
            # destination hexagon has one cube
            bottom_cube_index = self.hexagon_bottom[dst_hexagon_index]
            bottom_cube = self.cubes[bottom_cube_index]

            cube_index = self.hexagon_top[src_hexagon_index]
            cube = self.cubes[cube_index]

            if bottom_cube.player == self.player:
                 action = None

            elif bottom_cube.sort == CubeSort.MOUNTAIN:
                action = None

            else:
                # Try to capture the bottom cube
                if cube.beats(bottom_cube):
                    state = self.fork()
                    state.capture_cube(src_hexagon_index, dst_hexagon_index)
                    state.move_stack(src_hexagon_index, dst_hexagon_index)
                    if bottom_cube.sort == CubeSort.KING:
                        capture = Capture.KING
                    else:
                        capture = Capture.SOME

                    notation = Notation.move_stack(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                    action = JersiAction(notation, state, capture=capture, previous_action=previous_action)

                else:
                    action = None

        else:
            # destination hexagon has two cubes
            top_cube_index = self.hexagon_top[dst_hexagon_index]
            bottom_cube_index = self.hexagon_bottom[dst_hexagon_index]
            top_cube = self.cubes[top_cube_index]
            bottom_cube = self.cubes[bottom_cube_index]

            cube_index = self.hexagon_top[src_hexagon_index]
            cube = self.cubes[cube_index]

            if top_cube.player == self.player:
                action = None

            elif bottom_cube.sort == CubeSort.MOUNTAIN:
                 action = None

            else:
                # Try to capture the stack
                if cube.beats(top_cube):
                    state = self.fork()
                    state.capture_stack(src_hexagon_index, dst_hexagon_index)
                    state.move_stack(src_hexagon_index, dst_hexagon_index)

                    if top_cube.sort == CubeSort.KING:
                        capture = Capture.KING
                    else:
                        capture = Capture.SOME

                    notation = Notation.move_stack(src_hexagon_name, dst_hexagon_name, capture=capture, previous_action=previous_action)
                    action = JersiAction(notation, state, capture=capture, previous_action=previous_action)

                else:
                    action = None

        return action


    def find_cube_first_moves(self):
        actions = []

        next_fst_hexagons = Hexagon.get_next_fst()
        next_snd_hexagons = Hexagon.get_next_snd()

        hexagons1 = self.find_hexagons_with_movable_cube()
        for src1_hexagon_index in hexagons1:

            for dir1_index in HexagonDirection:
                dst1_hexagon_index = next_fst_hexagons[src1_hexagon_index][dir1_index]
                if dst1_hexagon_index != Null.HEXAGON:
                    action1 = self.try_move_cube(src1_hexagon_index, dst1_hexagon_index)
                    if action1 is not None:
                        actions.append(action1)

                        state1 = action1.state.fork()

                        if state1.is_hexagon_with_movable_stack(dst1_hexagon_index):

                            for dir2_index in HexagonDirection:

                                dst21_hexagon_index = next_fst_hexagons[dst1_hexagon_index][dir2_index]
                                if dst21_hexagon_index != Null.HEXAGON:
                                    action21 = state1.try_move_stack(dst1_hexagon_index, dst21_hexagon_index, previous_action=action1)
                                    if action21 is not None:
                                        actions.append(action21)

                                    if self.hexagon_bottom[dst21_hexagon_index] == Null.CUBE:
                                        # dst21_hexagon has zero cube
                                        dst22_hexagon_index = next_snd_hexagons[dst1_hexagon_index][dir2_index]
                                        if dst22_hexagon_index != Null.HEXAGON:
                                            action22 = state1.try_move_stack(dst1_hexagon_index, dst22_hexagon_index, previous_action=action1)
                                            if action22 is not None:
                                                actions.append(action22)


        return actions


    def find_stack_first_moves(self):
        actions = []

        next_fst_hexagons = Hexagon.get_next_fst()
        next_snd_hexagons = Hexagon.get_next_snd()

        hexagons1 = self.find_hexagons_with_movable_stack()
        for src1_hexagon_index in hexagons1:

            for dir1_index in HexagonDirection:

                dst11_hexagon_index = next_fst_hexagons[src1_hexagon_index][dir1_index]
                if dst11_hexagon_index != Null.HEXAGON:
                    action11 = self.try_move_stack(src1_hexagon_index, dst11_hexagon_index)
                    if action11 is not None:
                        actions.append(action11)

                        state11 = action11.state.fork()

                        if state11.is_hexagon_with_movable_cube(dst11_hexagon_index):

                            for dir21_index in HexagonDirection:

                                dst21_hexagon_index = next_fst_hexagons[dst11_hexagon_index][dir21_index]
                                if dst21_hexagon_index != Null.HEXAGON:
                                    action21 = state11.try_move_cube(dst11_hexagon_index, dst21_hexagon_index, previous_action=action11)
                                    if action21 is not None:
                                        actions.append(action21)

                    if self.hexagon_bottom[dst11_hexagon_index] == Null.CUBE:
                        # dst11_hexagon_index has zero cube
                        dst12_hexagon_index = next_snd_hexagons[src1_hexagon_index][dir1_index]
                        if dst12_hexagon_index != Null.HEXAGON:
                            action12 = self.try_move_stack(src1_hexagon_index, dst12_hexagon_index)
                            if action12 is not None:
                                actions.append(action12)

                                state12 = action12.state.fork()

                                if state12.is_hexagon_with_movable_cube(dst12_hexagon_index):

                                    for dir22_index in HexagonDirection:

                                        dst22_hexagon_index = next_fst_hexagons[dst12_hexagon_index][dir22_index]
                                        if dst22_hexagon_index != Null.HEXAGON:
                                            action22 = state12.try_move_cube(dst12_hexagon_index, dst22_hexagon_index, previous_action=action12)
                                            if action22 is not None:
                                                actions.append(action22)

        return actions


class MctsState:
    """Adaptater to mcts interface for JersiState"""

    def __init__(self, jersi_state, mcts_player):
        self.__jersi_state = jersi_state
        self.__mcts_player = mcts_player


    def __getPreviousPlayer(self):
       """ Opposite of getCurrentPlayer. Not required in the mcts interface."""
       return -self.getCurrentPlayer()


    def getCurrentPlayer(self):
       """ Returns 1 if it is the maximizer player's turn to choose an action,
       or -1 for the minimiser player"""
       if self.__jersi_state.player == self.__mcts_player:
           return 1
       else:
           return -1


    def isTerminal(self):
        return self.__jersi_state.is_terminal()


    def getReward(self):
        # >> reward for the previous player from the perspective of JersiState
        # >> indeed: <mcts current player> == <JersiState previous player>
        previous_player = self.__jersi_state.get_other_player()
        previous_reward = self.__jersi_state.get_rewards()[previous_player]
        return previous_reward*self.__getPreviousPlayer()


    def getPossibleActions(self):
        return self.__jersi_state.get_actions()


    def takeAction(self, action):
        return MctsState(self.__jersi_state.take_action(action), self.__mcts_player)


def extractStatistics(searcher, action):
    statistics = {}
    statistics['rootNumVisits'] = searcher.root.numVisits
    statistics['rootTotalReward'] = searcher.root.totalReward
    statistics['actionNumVisits'] = searcher.root.children[action].numVisits
    statistics['actionTotalReward'] = searcher.root.children[action].totalReward
    return statistics


def run_game(do_print=True):

    #searcher = mcts.mcts(timeLimit=2*60_000) # 2 minutes
    #searcher = mcts.mcts(timeLimit=30_000) # 30 seconds
    searcher = mcts.mcts(iterationLimit=10)

    action_count_total = 0

    state = JersiState()

    if do_print:
        state.show()

    while not state.is_terminal():
        actions = state.get_actions()
        action_count_total += len(actions)

        player = state.get_current_player()

        if player == Player.WHITE:
            action = searcher.search(initialState=MctsState(state, player))
            statistics = extractStatistics(searcher, action)

            # action = random.choice(actions)
            # statistics = None
        else:
            action = random.choice(actions)
            statistics = None

        state = state.take_action(action)
        if do_print:
            print(f"{Player.name(player)} takes action {action} amongst {len(actions)}")

            if statistics is not None:
                print("mcts statitics:" +
                      f" chosen action= {statistics['actionTotalReward']} total reward" +
                      f" over {statistics['actionNumVisits']} visits /"
                      f" all explored actions= {statistics['rootTotalReward']} total reward" +
                      f" over {statistics['rootNumVisits']} visits")

            print('-'*60)
            state.show()

    if do_print:
        print('-'*60)

        if state.is_terminal():

            rewards = state.get_rewards()
            player = state.get_current_player()

            print(f"{state.terminal_case}")

            if rewards[Player.WHITE] == rewards[Player.BLACK]:
                text = f"nobody wins ; the game is a draw between {Player.name(Player.WHITE)} and {Player.name(Player.BLACK)}"
                print(text)

            elif rewards[Player.WHITE] > rewards[Player.BLACK]:
                text = f"{Player.name(Player.WHITE)} wins against {Player.name(Player.BLACK)}"
                print(text)

            else:
                text = f"{Player.name(Player.BLACK)} wins against {Player.name(Player.WHITE)}"
                print(text)

        else:
            assert _no_assert or False

        print(f"{action_count_total} possible actions over {state.turn} turns ; {action_count_total/state.turn:.1f} average possible actions per turn")

    return state.terminal_case


class RandomSearcher():


    def __init__(self):
        pass


    def search(self, state):
        actions = state.get_actions()
        action = random.choice(actions)
        return action


class MctsSearcher():


    def __init__(self, time_limit=None, iteration_limit=None):

        assert time_limit is None or iteration_limit is None

        if time_limit is None and iteration_limit is None:
            time_limit = 1_000

        self.time_limit = time_limit
        self.iteration_limit = iteration_limit


    def search(self, state):

        use_slices = True

        self.searchInit(state)

        if use_slices:
            while not self.searchEnded():
                progression = self.searchGetProgression()
                print(f"progression:{progression:3.0f}")
                self.searchRun()
            progression = self.searchGetProgression()
            print(f"progression:{progression:3.0f}")
            action = self.searchGetAction()
        else:
            action = self.searcher.search(initialState=state)

        if _do_debug:
            statistics = self.searcher.getStatistics(action)
            print(f"    mcts statitics for the chosen action: {statistics['actionTotalReward']} total reward over {statistics['actionNumVisits']} visits")
            print(f"    mcts statitics for all explored actions: {statistics['rootTotalReward']} total reward over {statistics['rootNumVisits']} visits")
            for (child_action, child) in self.searcher.root.children.items():
                print(f"    action {child_action} numVisits={child.numVisits} totalReward={child.totalReward}")

        return action


    def searchInit(self, initialState):

        if self.time_limit is not None:
            # time in milli-seconds
            self.searcher = mcts.mcts(timeLimit=self.time_limit)

        elif self.iteration_limit is not None:
            # number of mcts rounds
            self.searcher = mcts.mcts(iterationLimit=self.iteration_limit)

        self.searcher.searchInit(initialState)


    def searchEnded(self):
        return self.searcher.searchEnded()


    def searchRun(self):
        self.searcher.searchRun()


    def searchGetProgression(self):
        return self.searcher.searchGetProgression()


    def searchGetAction(self):
        return self.searcher.searchGetAction()



searcher_catalog = dict()

searcher_catalog["random"] = RandomSearcher()

# searcher_catalog["mcts-s-1"] = MctsSearcher(time_limit=1_000)
# searcher_catalog["mcts-s-2"] = MctsSearcher(time_limit=2_000)
# searcher_catalog["mcts-s-5"] = MctsSearcher(time_limit=5_000)
# searcher_catalog["mcts-s-10"] = MctsSearcher(time_limit=10_000)
# searcher_catalog["mcts-s-20"] = MctsSearcher(time_limit=20_000)
# searcher_catalog["mcts-s-30"] = MctsSearcher(time_limit=30_000)
# searcher_catalog["mcts-s-60"] = MctsSearcher(time_limit=60_000)
# searcher_catalog["mcts-m-5"] = MctsSearcher(time_limit=5*60_000)

searcher_catalog["mcts-i-10"] = MctsSearcher(iteration_limit=10)
# searcher_catalog["mcts-i-50"] = MctsSearcher(iteration_limit=50)
# searcher_catalog["mcts-i-100"] = MctsSearcher(iteration_limit=100)
# searcher_catalog["mcts-i-500"] = MctsSearcher(iteration_limit=500)
# searcher_catalog["mcts-i-1k"] = MctsSearcher(iteration_limit=1_000)
# searcher_catalog["mcts-i-10k"] = MctsSearcher(iteration_limit=10_000)


class Simulation:

    def __init__(self):
        self.selected_searcher_name = [None, None]
        self.selected_searcher = [None, None]

        self.js = None
        self.iter_count = None
        self.iter_index = None
        self.log = None


    def set_white_player(self, name):
        self.selected_searcher_name[Player.WHITE] = name
        self.selected_searcher[Player.WHITE] = searcher_catalog[name]


    def set_black_player(self, name):
        self.selected_searcher_name[Player.BLACK] = name
        self.selected_searcher[Player.BLACK] = searcher_catalog[name]


    def start(self):

        assert self.selected_searcher_name[Player.WHITE] is not None
        assert self.selected_searcher_name[Player.BLACK] is not None

        assert self.selected_searcher[Player.WHITE] is not None
        assert self.selected_searcher[Player.BLACK] is not None

        self.js = JersiState()

        self.js.show()

        self.iter_count = 1_000
        self.iter_index = 0

        self.log = ""


    def get_log(self):
        return self.log


    def has_next_turn(self):
        return self.iter_index < self.iter_count and not self.js.is_terminal()


    def next_turn(self):

        self.log = ""

        if self.has_next_turn():
            player = self.js.get_current_player()
            player_name = f"{Player.name(player)}-{self.selected_searcher_name[player]}"
            action_count = len(self.js.get_actions())

            print()
            print(f"{player_name} is thinking ...")

            if isinstance(self.selected_searcher[player], MctsSearcher):
                action = self.selected_searcher[player].search(MctsState(self.js,player))

            else:
                action = self.selected_searcher[player].search(self.js)

            print(f"{player_name} is done")

            self.log = f"iteration {self.iter_index}: {player_name} selects {action} amongst {action_count} actions"
            print(self.log)
            print("-"*40)

            self.js = self.js.take_action(action)
            self.js.show()

            self.iter_index += 1

        if self.js.is_terminal():

            rewards = self.js.get_rewards()
            player = self.js.get_current_player()

            print()
            print("-"*40)

            white_player = f"{Player.name(Player.WHITE)}-{self.selected_searcher_name[Player.WHITE]}"
            black_player = f"{Player.name(Player.BLACK)}-{self.selected_searcher_name[Player.BLACK]}"

            if rewards[Player.WHITE] == rewards[Player.BLACK]:
                self.log = f"nobody wins ; the game is a draw between {white_player} and {black_player}"
                print(self.log)

            elif rewards[Player.WHITE] > rewards[Player.BLACK]:
                self.log = f"{white_player} wins against {black_player}"
                print(self.log)

            else:
                self.log = f"{black_player} wins against {white_player}"
                print(self.log)

        else:
            print()
            print("-"*40)
            print("not a terminal state")



def run_games():
    terminal_cases = collections.Counter()

    game_count = 1
    for game_index in range(game_count):
        terminal_case = run_game(do_print=True)
        print(f"{game_index} {terminal_case}")
        terminal_cases[terminal_case] += 1

    print()
    for (label, count) in terminal_cases.items():
        print(f"{label}:{count}")


def run_simulation():

    simulation = Simulation()

    simulation.set_white_player(random.choice(list(searcher_catalog.keys())))
    simulation.set_black_player(random.choice(list(searcher_catalog.keys())))

    simulation.start()

    while simulation.has_next_turn():
        simulation.next_turn()


Cube.init()
Hexagon.init()
GraphicalHexagon.init()


if __name__ == "__main__":
    if False:
        run_games()

    if True:
        run_simulation()

    if False:
        cProfile.run("run_games()")
        #print(timeit.timeit("main()", setup="from __main__ import main", number=1))
