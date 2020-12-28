# -*- coding: utf-8 -*-
"""
Data structure for "jersi" game : fast when performance is required.
"""

import cProfile

import copy
import math
import os
import random
import sys
import timeit
import types

import numpy as np

script_home = os.path.abspath(os.path.dirname(__file__))
mcts_home = os.path.join(script_home, "packages", "MCTS-master-2020-0330")
sys.path.append(mcts_home)

import mcts


# Define jersi constants

def make_constJersi():

    constJersi = types.SimpleNamespace()

    constJersi.do_debug = True
    constJersi.undefined = -1
    constJersi.byte_bit_size = 8

    constJersi.max_credit = 40 # Max number of turns without any capture
    constJersi.credit_bit_size = int(math.ceil(math.log2(constJersi.max_credit)))

    if constJersi.do_debug:
        print()
        print(f"{constJersi.do_debug=!s}")
        print(f"{constJersi.undefined=!s}")

        print(f"{constJersi.byte_bit_size=!s}")

        print(f"{constJersi.max_credit=!s}")
        print(f"{constJersi.credit_bit_size=!s}")

    return constJersi

constJersi = make_constJersi()


# Define cube color type

def make_TypeCubeColor():

    TypeCubeColor = types.SimpleNamespace()

    TypeCubeColor.domain = np.array(["black", "white"])
    TypeCubeColor.count = TypeCubeColor.domain.size
    TypeCubeColor.function = np.array([str.lower, str.upper])
    TypeCubeColor.codomain = np.arange(TypeCubeColor.count, dtype=np.int8)

    TypeCubeColor.black = np.argwhere(TypeCubeColor.domain == "black")[0][0]
    TypeCubeColor.white = np.argwhere(TypeCubeColor.domain == "white")[0][0]

    TypeCubeColor.bit_size = int(math.ceil(math.log2(TypeCubeColor.count)))

    if constJersi.do_debug:
        print()
        print(f"{TypeCubeColor.count=!s}")
        print(f"{TypeCubeColor.bit_size=!s}")
        print(f"{TypeCubeColor.domain=!s}")
        print(f"{TypeCubeColor.codomain=!s}")
        print(f"{TypeCubeColor.function=!s}")

        print(f"{TypeCubeColor.black=!s}")
        print(f"{TypeCubeColor.white=!s}")

    assert TypeCubeColor.function.size == TypeCubeColor.count
    assert np.unique(TypeCubeColor.domain).size == TypeCubeColor.count

    return TypeCubeColor

TypeCubeColor = make_TypeCubeColor()


# Define cube sort type

def make_TypeCubeSort():

    TypeCubeSort = types.SimpleNamespace()

    TypeCubeSort.domain = np.array(["foul", "king", "mountain", "paper", "rock", "scissors", "wise"])
    TypeCubeSort.count = TypeCubeSort.domain.size
    TypeCubeSort.codomain = np.arange(TypeCubeSort.count, dtype=np.int8)
    TypeCubeSort.key = np.vectorize(lambda x:x[0].upper())(TypeCubeSort.domain)

    TypeCubeSort.foul = np.argwhere(TypeCubeSort.domain == "foul")[0][0]
    TypeCubeSort.king = np.argwhere(TypeCubeSort.domain == "king")[0][0]
    TypeCubeSort.mountain = np.argwhere(TypeCubeSort.domain == "mountain")[0][0]
    TypeCubeSort.paper = np.argwhere(TypeCubeSort.domain == "paper")[0][0]
    TypeCubeSort.rock = np.argwhere(TypeCubeSort.domain == "rock")[0][0]
    TypeCubeSort.scissors = np.argwhere(TypeCubeSort.domain == "scissors")[0][0]
    TypeCubeSort.wise = np.argwhere(TypeCubeSort.domain == "wise")[0][0]

    TypeCubeSort.multiplicity  = np.zeros(TypeCubeSort.count, dtype=np.int8)
    TypeCubeSort.multiplicity[TypeCubeSort.foul] = 2
    TypeCubeSort.multiplicity[TypeCubeSort.king] = 1
    TypeCubeSort.multiplicity[TypeCubeSort.mountain] = 4
    TypeCubeSort.multiplicity[TypeCubeSort.paper] = 4
    TypeCubeSort.multiplicity[TypeCubeSort.rock] = 4
    TypeCubeSort.multiplicity[TypeCubeSort.scissors] = 4
    TypeCubeSort.multiplicity[TypeCubeSort.wise] = 2
    TypeCubeSort.multiplicity_sum = TypeCubeSort.multiplicity.sum()

    if constJersi.do_debug:
        print()
        print(f"{TypeCubeSort.count=!s}")
        print(f"{TypeCubeSort.domain=!s}")
        print(f"{TypeCubeSort.codomain=!s}")
        print(f"{TypeCubeSort.key=!s}")

        print(f"{TypeCubeSort.foul=!s}")
        print(f"{TypeCubeSort.king=!s}")
        print(f"{TypeCubeSort.mountain=!s}")
        print(f"{TypeCubeSort.paper=!s}")
        print(f"{TypeCubeSort.rock=!s}")
        print(f"{TypeCubeSort.scissors=!s}")
        print(f"{TypeCubeSort.wise=!s}")

        print(f"{TypeCubeSort.multiplicity=!s}")
        print(f"{TypeCubeSort.multiplicity_sum=!s}")

    assert np.unique(TypeCubeSort.domain).size == TypeCubeSort.count
    assert np.unique(TypeCubeSort.key).size == TypeCubeSort.count

    return TypeCubeSort

TypeCubeSort = make_TypeCubeSort()


# Define cube colored sort type

def make_TypeCubeColoredSort():

    TypeCubeColoredSort = types.SimpleNamespace()

    TypeCubeColoredSort.count = TypeCubeColor.count*TypeCubeSort.count
    TypeCubeColoredSort.codomain = np.arange(TypeCubeColoredSort.count, dtype=np.int8)
    TypeCubeColoredSort.color = np.full(TypeCubeColoredSort.count, constJersi.undefined, dtype=np.int8)
    TypeCubeColoredSort.sort = np.full(TypeCubeColoredSort.count, constJersi.undefined, dtype=np.int8)

    cube_csort_id_list = list()

    for cube_color_index in TypeCubeColor.codomain:
        cube_color_function = TypeCubeColor.function[cube_color_index]

        for (cube_sort_index, cube_sort_key) in enumerate(TypeCubeSort.key):

                cube_csort_index = len(cube_csort_id_list)

                cube_csort_id = cube_color_function(cube_sort_key)
                cube_csort_id_list.append(cube_csort_id)

                TypeCubeColoredSort.color[cube_csort_index] = cube_color_index
                TypeCubeColoredSort.sort[cube_csort_index] = cube_sort_index

    TypeCubeColoredSort.domain = np.array(cube_csort_id_list)


    if constJersi.do_debug:
        print()
        print(f"{TypeCubeColoredSort.count=!s}")
        print(f"{TypeCubeColoredSort.domain=!s}")
        print(f"{TypeCubeColoredSort.codomain=!s}")
        print(f"{TypeCubeColoredSort.color=!s}")
        print(f"{TypeCubeColoredSort.sort=!s}")

    assert TypeCubeColoredSort.domain.size == TypeCubeColoredSort.count
    assert np.unique(TypeCubeColoredSort.domain).size == TypeCubeColoredSort.count

    return TypeCubeColoredSort

TypeCubeColoredSort = make_TypeCubeColoredSort()


# Define cube status type

def make_TypeCubeStatus():

    TypeCubeStatus = types.SimpleNamespace()

    TypeCubeStatus.domain = np.array(["active", "captured", "reserved"])
    TypeCubeStatus.count = TypeCubeStatus.domain.size
    TypeCubeStatus.codomain = np.arange(TypeCubeStatus.count, dtype=np.int8)

    TypeCubeStatus.active = np.argwhere(TypeCubeStatus.domain == "active")[0][0]
    TypeCubeStatus.captured = np.argwhere(TypeCubeStatus.domain == "captured")[0][0]
    TypeCubeStatus.reserved = np.argwhere(TypeCubeStatus.domain == "reserved")[0][0]

    # >> Take into account the coding of constJersi.undefined
    TypeCubeStatus.bit_size = int(math.ceil(math.log2(TypeCubeStatus.count + 1)))

    if constJersi.do_debug:
        print()
        print(f"{TypeCubeStatus.count=!s}")
        print(f"{TypeCubeStatus.bit_size=!s}")
        print(f"{TypeCubeStatus.domain=!s}")
        print(f"{TypeCubeStatus.codomain=!s}")

        print(f"{TypeCubeStatus.active=!s}")
        print(f"{TypeCubeStatus.captured=!s}")
        print(f"{TypeCubeStatus.reserved=!s}")

    assert np.unique(TypeCubeStatus.domain).size == TypeCubeStatus.count

    return TypeCubeStatus

TypeCubeStatus = make_TypeCubeStatus()


# Define cube constant properties

def make_constCube():

    constCube = types.SimpleNamespace()

    constCube.count = TypeCubeColor.count*TypeCubeSort.multiplicity_sum
    constCube.codomain = np.arange(constCube.count, dtype=np.int8)
    constCube.color = np.full(constCube.count, constJersi.undefined, dtype=np.int8)
    constCube.sort = np.full(constCube.count, constJersi.undefined, dtype=np.int8)
    constCube.csort = np.full(constCube.count, constJersi.undefined, dtype=np.int8)

    cube_id_list = list()

    for cube_color_index in TypeCubeColor.codomain:
        cube_color_function = TypeCubeColor.function[cube_color_index]

        for (cube_sort_index, cube_sort_key) in enumerate(TypeCubeSort.key):

            for cube_sort_occurrence in range(TypeCubeSort.multiplicity[cube_sort_index]):
                cube_index = len(cube_id_list)

                cube_id = "%s%d" % (cube_color_function(cube_sort_key), cube_sort_occurrence)
                cube_id_list.append(cube_id)


                cube_csort_index = np.argwhere((TypeCubeColoredSort.color == cube_color_index) &
                                               (TypeCubeColoredSort.sort == cube_sort_index) )[0][0]

                constCube.color[cube_index] = cube_color_index
                constCube.sort[cube_index] = cube_sort_index
                constCube.csort[cube_index] = cube_csort_index

    constCube.domain = np.array(cube_id_list)

    assert constCube.domain.size == constCube.count
    assert np.unique(constCube.domain).size == constCube.count

    constCube.white_king = constCube.codomain[(constCube.color == TypeCubeColor.white) &
                                              (constCube.sort == TypeCubeSort.king)][0]

    constCube.black_king = constCube.codomain[(constCube.color == TypeCubeColor.black) &
                                              (constCube.sort == TypeCubeSort.king)][0]

    constCube.king = np.full(TypeCubeColor.count, constJersi.undefined, dtype=np.int8)
    constCube.king[TypeCubeColor.white] = constCube.white_king
    constCube.king[TypeCubeColor.black] = constCube.black_king

    if constJersi.do_debug:
        print()
        print(f"{constCube.count=!s}")
        print(f"{constCube.domain=!s}")
        print(f"{constCube.codomain=!s}")
        print(f"{constCube.color=!s}")
        print(f"{constCube.sort=!s}")
        print(f"{constCube.csort=!s}")
        print(f"{constCube.white_king=!s}")
        print(f"{constCube.black_king=!s}")
        print(f"{constCube.king=!s}")

    return constCube

constCube = make_constCube()


# Define hexagon level type

def make_TypeHexLevel():

    TypeHexLevel = types.SimpleNamespace()

    TypeHexLevel.domain = np.array(["bottom", "top"])
    TypeHexLevel.count = TypeHexLevel.domain.size
    TypeHexLevel.codomain = np.arange(TypeHexLevel.count, dtype=np.int8)

    TypeHexLevel.bottom = np.argwhere(TypeHexLevel.domain == "bottom")[0][0]
    TypeHexLevel.top = np.argwhere(TypeHexLevel.domain == "top")[0][0]

    # >> Take into account the coding of constJersi.undefined
    TypeHexLevel.bit_size = int(math.ceil(math.log2(TypeHexLevel.count + 1)))

    if constJersi.do_debug:
        print()
        print(f"{TypeHexLevel.count=!s}")
        print(f"{TypeHexLevel.bit_size=!s}")
        print(f"{TypeHexLevel.domain=!s}")
        print(f"{TypeHexLevel.codomain=!s}")

        print(f"{TypeHexLevel.bottom=!s}")
        print(f"{TypeHexLevel.top=!s}")

    assert np.unique(TypeHexLevel.domain).size == TypeHexLevel.count

    return TypeHexLevel

TypeHexLevel = make_TypeHexLevel()


# Define hexagon status type

def make_TypeHexStatus():

    TypeHexStatus = types.SimpleNamespace()

    TypeHexStatus.domain = np.array(["has_no_cube", "has_one_cube", "has_two_cubes"])
    TypeHexStatus.count = TypeHexStatus.domain.size
    TypeHexStatus.codomain = np.arange(TypeHexStatus.count, dtype=np.int8)

    TypeHexStatus.has_no_cube = np.argwhere(TypeHexStatus.domain == "has_no_cube")[0][0]
    TypeHexStatus.has_one_cube = np.argwhere(TypeHexStatus.domain == "has_one_cube")[0][0]
    TypeHexStatus.has_two_cubes = np.argwhere(TypeHexStatus.domain == "has_two_cubes")[0][0]

    if constJersi.do_debug:
        print()
        print(f"{TypeHexStatus.count=!s}")
        print(f"{TypeHexStatus.domain=!s}")
        print(f"{TypeHexStatus.codomain=!s}")

        print(f"{TypeHexStatus.has_no_cube=!s}")
        print(f"{TypeHexStatus.has_one_cube=!s}")
        print(f"{TypeHexStatus.has_two_cubes=!s}")

    assert np.unique(TypeHexStatus.domain).size == TypeHexStatus.count

    return TypeHexStatus

TypeHexStatus = make_TypeHexStatus()


# Define hexagon direction type

def make_TypeHexDirection():

    TypeHexDirection = types.SimpleNamespace()

    TypeHexDirection.domain = np.array(["090", "150", "210", "270", "330", "030"])
    TypeHexDirection.count = TypeHexDirection.domain.size
    TypeHexDirection.codomain = np.arange(TypeHexDirection.count, dtype=np.int8)
    TypeHexDirection.delta_u = np.array([+1, +1, +0, -1, -1, +0], dtype=np.int8)
    TypeHexDirection.delta_v = np.array([+0, -1, -1, +0, +1, +1], dtype=np.int8)

    if constJersi.do_debug:
        print()
        print(f"{TypeHexDirection.count=!s}")
        print(f"{TypeHexDirection.domain=!s}")
        print(f"{TypeHexDirection.codomain=!s}")
        print(f"{TypeHexDirection.delta_u=!s}")
        print(f"{TypeHexDirection.delta_v=!s}")

    assert np.unique(TypeHexDirection.domain).size == TypeHexDirection.count
    assert TypeHexDirection.delta_u.size == TypeHexDirection.count
    assert TypeHexDirection.delta_v.size == TypeHexDirection.count

    return TypeHexDirection

TypeHexDirection = make_TypeHexDirection()


# Define hexagon constant properties

def make_constHex():

    def create_hexagon_at_uv(hex_id, u, v):

        assert len(hex_id) == 2
        assert hex_id not in constHex._id_dict
        assert (u,v) not in constHex._uv_dict

        hex_index = len(constHex._id_list)

        constHex._id_dict[hex_id] = hex_index
        constHex._uv_dict[(u,v)] = hex_index

        constHex._id_list.append(hex_id)
        constHex._u_list.append(u)
        constHex._v_list.append(v)


    def create_all_hexagons():

        constHex._id_dict = dict()
        constHex._uv_dict = dict()

        constHex._id_list = list()
        constHex._u_list = list()
        constHex._v_list = list()

        # Row "a"
        create_hexagon_at_uv('a1', -1, -4)
        create_hexagon_at_uv('a2', -0, -4)
        create_hexagon_at_uv('a3', 1, -4)
        create_hexagon_at_uv('a4', 2, -4)
        create_hexagon_at_uv('a5', 3, -4)
        create_hexagon_at_uv('a6', 4, -4)
        create_hexagon_at_uv('a7', 5, -4)

        # Row "b"
        create_hexagon_at_uv('b1', -2, -3)
        create_hexagon_at_uv('b2', -1, -3)
        create_hexagon_at_uv('b3', 0, -3)
        create_hexagon_at_uv('b4', 1, -3)
        create_hexagon_at_uv('b5', 2, -3)
        create_hexagon_at_uv('b6', 3, -3)
        create_hexagon_at_uv('b7', 4, -3)
        create_hexagon_at_uv('b8', 5, -3)

        # Row "c"
        create_hexagon_at_uv('c1', -2, -2)
        create_hexagon_at_uv('c2', -1, -2)
        create_hexagon_at_uv('c3', 0, -2)
        create_hexagon_at_uv('c4', 1, -2)
        create_hexagon_at_uv('c5', 2, -2)
        create_hexagon_at_uv('c6', 3, -2)
        create_hexagon_at_uv('c7', 4, -2)

        # Row "d"
        create_hexagon_at_uv('d1', -3, -1)
        create_hexagon_at_uv('d2', -2, -1)
        create_hexagon_at_uv('d3', -1, -1)
        create_hexagon_at_uv('d4', 0, -1)
        create_hexagon_at_uv('d5', 1, -1)
        create_hexagon_at_uv('d6', 2, -1)
        create_hexagon_at_uv('d7', 3, -1)
        create_hexagon_at_uv('d8', 4, -1)

        # Row "e"
        create_hexagon_at_uv('e1', -4, 0)
        create_hexagon_at_uv('e2', -3, 0)
        create_hexagon_at_uv('e3', -2, 0)
        create_hexagon_at_uv('e4', -1, 0)
        create_hexagon_at_uv('e5', 0, 0)
        create_hexagon_at_uv('e6', 1, 0)
        create_hexagon_at_uv('e7', 2, 0)
        create_hexagon_at_uv('e8', 3, 0)
        create_hexagon_at_uv('e9', 4, 0)

        # Row "f"
        create_hexagon_at_uv('f1', -4, 1)
        create_hexagon_at_uv('f2', -3, 1)
        create_hexagon_at_uv('f3', -2, 1)
        create_hexagon_at_uv('f4', -1, 1)
        create_hexagon_at_uv('f5', 0, 1)
        create_hexagon_at_uv('f6', 1, 1)
        create_hexagon_at_uv('f7', 2, 1)
        create_hexagon_at_uv('f8', 3, 1)

        # Row "g"
        create_hexagon_at_uv('g1', -4, 2)
        create_hexagon_at_uv('g2', -3, 2)
        create_hexagon_at_uv('g3', -2, 2)
        create_hexagon_at_uv('g4', -1, 2)
        create_hexagon_at_uv('g5', 0, 2)
        create_hexagon_at_uv('g6', 1, 2)
        create_hexagon_at_uv('g7', 2, 2)

        # Row "h"
        create_hexagon_at_uv('h1', -5, 3)
        create_hexagon_at_uv('h2', -4, 3)
        create_hexagon_at_uv('h3', -3, 3)
        create_hexagon_at_uv('h4', -2, 3)
        create_hexagon_at_uv('h5', -1, 3)
        create_hexagon_at_uv('h6', 0, 3)
        create_hexagon_at_uv('h7', 1, 3)
        create_hexagon_at_uv('h8', 2, 3)

        # Row "i"
        create_hexagon_at_uv('i1', -5, 4)
        create_hexagon_at_uv('i2', -4, 4)
        create_hexagon_at_uv('i3', -3, 4)
        create_hexagon_at_uv('i4', -2, 4)
        create_hexagon_at_uv('i5', -1, 4)
        create_hexagon_at_uv('i6', 0, 4)
        create_hexagon_at_uv('i7', 1, 4)

        constHex.domain = np.array(constHex._id_list)
        constHex.count = constHex.domain.size
        constHex.codomain = np.arange(constHex.count, dtype=np.int8)
        constHex.coord_u = np.array(constHex._u_list)
        constHex.coord_v = np.array(constHex._v_list)

        # >> Take into account the coding of constJersi.undefined
        constHex.bit_size = int(math.ceil(math.log2(constHex.count + 1)))


    def create_hexagons_layout():

        constHex.layout = list()

        constHex.layout.append( (2, np.array(["i1", "i2", "i3", "i4", "i5", "i6", "i7"])))
        constHex.layout.append( (1, np.array(["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8"])))
        constHex.layout.append( (2, np.array(["g1", "g2", "g3", "g4", "g5", "g6", "g7"])))
        constHex.layout.append( (1, np.array(["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"])))
        constHex.layout.append( (0, np.array(["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9"])))
        constHex.layout.append( (1, np.array(["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8"])))
        constHex.layout.append( (2, np.array(["c1", "c2", "c3", "c4", "c5", "c6", "c7"])))
        constHex.layout.append( (1, np.array(["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"])))
        constHex.layout.append( (2, np.array(["a1", "a2", "a3", "a4", "a5", "a6", "a7"])))

        for (row_shift_count, row_hex_ids) in constHex.layout:
            assert row_shift_count == (9 - len(row_hex_ids))
            assert np.unique(row_hex_ids).size == len(row_hex_ids)


    def create_next_hexagons():

        constHex.next_fst = np.full((constHex.count, TypeHexDirection.count), constJersi.undefined, dtype=np.int8)
        constHex.next_snd = np.full((constHex.count, TypeHexDirection.count), constJersi.undefined, dtype=np.int8)

        for hex_index in constHex.codomain:
            hex_u = constHex.coord_u[hex_index]
            hex_v = constHex.coord_v[hex_index]

            for hex_dir_index in TypeHexDirection.codomain:
                hex_delta_u = TypeHexDirection.delta_u[hex_dir_index]
                hex_delta_v = TypeHexDirection.delta_v[hex_dir_index]

                hex_fst_u = hex_u + 1*hex_delta_u
                hex_fst_v = hex_v + 1*hex_delta_v

                hex_snd_u = hex_u + 2*hex_delta_u
                hex_snd_v = hex_v + 2*hex_delta_v

                if (hex_fst_u, hex_fst_v) in constHex._uv_dict:
                    hex_fst_index = constHex._uv_dict[(hex_fst_u, hex_fst_v)]
                    constHex.next_fst[hex_index, hex_dir_index] = hex_fst_index

                    if (hex_snd_u, hex_snd_v) in constHex._uv_dict:
                        hex_snd_index = constHex._uv_dict[(hex_snd_u, hex_snd_v)]
                        constHex.next_snd[hex_index, hex_dir_index] = hex_snd_index


    def create_kings_hexagons():
        white_first_hexagons = ["a1", "a2", "a3", "a4", "a5", "a6", "a7"]
        black_first_hexagons = ["i1", "i2", "i3", "i4", "i5", "i6", "i7"]

        white_first_indices = list(map(lambda x: constHex._id_dict[x], white_first_hexagons))
        black_first_indices = list(map(lambda x: constHex._id_dict[x], black_first_hexagons))

        assert len(white_first_hexagons) == len(black_first_indices)
        hex_count = len(white_first_hexagons)

        constHex.kind_begins = np.full((TypeCubeColor.count, hex_count), constJersi.undefined, dtype=np.int8)
        constHex.kind_ends = np.full((TypeCubeColor.count, hex_count), constJersi.undefined, dtype=np.int8)

        constHex.kind_begins[TypeCubeColor.white, :] = white_first_indices
        constHex.kind_begins[TypeCubeColor.black, :] = black_first_indices

        constHex.kind_ends[TypeCubeColor.white, :] = black_first_indices
        constHex.kind_ends[TypeCubeColor.black, :] = white_first_indices


    constHex = types.SimpleNamespace()

    create_all_hexagons()
    create_hexagons_layout()
    create_next_hexagons()
    create_kings_hexagons()

    if constJersi.do_debug:
        print()
        print(f"{constHex.count=!s}")
        print(f"{constHex.bit_size=!s}")
        print(f"{constHex.domain=!s}")
        print(f"{constHex.codomain=!s}")
        print(f"{constHex.coord_u=!s}")
        print(f"{constHex.coord_v=!s}")
        print()
        print(f"{constHex.next_fst=!s}")
        print(f"{constHex.next_snd=!s}")
        print()
        print(f"{constHex.kind_begins=!s}")
        print(f"{constHex.kind_ends=!s}")

    return constHex

constHex = make_constHex()


# Define jersi state

class JersiState:


    def __init__(self):

        self.player = TypeCubeColor.white
        self.credit = constJersi.max_credit
        self.turn = 1

        self.mcts_player = None

        self.cube_status = np.full(constCube.count, constJersi.undefined, dtype=np.int8)
        self.cube_hex = np.full(constCube.count, constJersi.undefined, dtype=np.int8)
        self.cube_level = np.full(constCube.count, constJersi.undefined, dtype=np.int8)

        self.hex_status = np.full(constHex.count, TypeHexStatus.has_no_cube, dtype=np.int8)
        self.hex_bottom = np.full(constHex.count, constJersi.undefined, dtype=np.int8)
        self.hex_top = np.full(constHex.count, constJersi.undefined, dtype=np.int8)

        self.terminal = None
        self.rewards = None
        self.actions = None

        self.set_all_cubes()


    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.player == other.player and
                self.credit == other.credit and
                np.all(self.cube_status == other.cube_status) and
                np.all(self.cube_hex == other.cube_hex) and
                np.all(self.cube_level == other.cube_level))


    def __hash__(self):
        return hash(self.encode_state())


    ### mcts-interface-begin

    def getCurrentPlayer(self):
       """ Returns 1 if it is the maximizer player's turn to choose an action,
       or -1 for the minimiser player"""

       if self.player == self.mcts_player:
           return 1
       else:
           return -1


    def getPreviousPlayer(self):
       """ Opposite of getCurrentPlayer. Not required in the mcts-interface, but it helps."""
       return -self.getCurrentPlayer()


    def getPossibleActions(self):
        return self.get_actions()


    def isTerminal(self):
        return self.is_terminal()


    def takeAction(self, action):
        return self.take_action(action)


    def getReward(self):
        # >> reward for the previous player from the perspective of JersiState
        # >> indeed: <mcts current player> == <JersiState previous player>

        previous_player = self.previous_player()
        previous_reward = self.get_reward()[previous_player]
        return previous_reward*self.getPreviousPlayer()


    ### mcts-interface-end


    def fork(self, origin=None):

        if origin is None:
            origin = self

        next_state = copy.copy(self)

        next_state.player = origin.next_player()
        next_state.credit = max(0, origin.credit - 1)
        next_state.turn = origin.turn - 1

        next_state.cube_status = np.copy(next_state.cube_status)
        next_state.cube_hex = np.copy(next_state.cube_hex)
        next_state.cube_level = np.copy(next_state.cube_level)

        next_state.hex_status = np.copy(next_state.hex_status)
        next_state.hex_bottom = np.copy(next_state.hex_bottom)
        next_state.hex_top = np.copy(next_state.hex_top)

        next_state.terminal = None
        next_state.rewards = None
        next_state.actions = None

        return next_state


    def set_mcts_player(self, mcts_player):
        assert mcts_player in TypeCubeColor.codomain
        self.mcts_player = mcts_player


    def get_player(self):
        return self.player


    def get_actions(self):

        if self.actions is None:

            self.actions = []

            # Search active cubes
            cube_color_selection = constCube.color == self.player
            cube_status_selection = self.cube_status == TypeCubeStatus.active
            cube_hex_selection = self.cube_hex[cube_color_selection & cube_status_selection]

            for src_hex_index in cube_hex_selection:
                for hex_dir_index in TypeHexDirection.codomain:

                    fst_dst_hex_index = constHex.next_fst[src_hex_index, hex_dir_index]
                    if fst_dst_hex_index != constJersi.undefined:

                        if self.hex_status[fst_dst_hex_index] == TypeHexStatus.has_no_cube:

                            fst_action_notation = constHex.domain[src_hex_index]
                            fst_action_notation += "-" + constHex.domain[fst_dst_hex_index]

                            fst_next_state = self.fork(origin=self)
                            fst_next_state.move_cube(src_hex_index, fst_dst_hex_index)
                            self.actions.append(JersiAction(fst_action_notation, fst_next_state))

        return self.actions


    def drop_cube(self, cube_index, hex_index):

        assert self.cube_status[cube_index] in [TypeCubeStatus.reserved,
                                                TypeCubeStatus.captured]

        if self.hex_status[hex_index] == TypeHexStatus.has_no_cube:

            self.hex_bottom[hex_index] = cube_index
            self.hex_status[hex_index] = TypeHexStatus.has_one_cube

            self.cube_hex[cube_index] = hex_index
            self.cube_hex_level[cube_index] = TypeHexLevel.bottom

        elif self.hex_status[hex_index] == TypeHexStatus.has_one_cube:

            self.hex_top[hex_index] = cube_index
            self.hex_status[hex_index] = TypeHexStatus.has_two_cubes

            self.cube_hex[cube_index] = hex_index
            self.cube_hex_level[cube_index] = TypeHexLevel.top

        else:
            assert self.hex_status[hex_index] in [TypeHexStatus.has_no_cube,
                                                  TypeHexStatus.has_one_cube]


    def move_cube(self, src_hex_index, dst_hex_index):

        if self.hex_status[src_hex_index] == TypeHexStatus.has_one_cube:

            cube_index = self.hex_bottom[src_hex_index]
            assert cube_index != constJersi.undefined

            self.hex_bottom[src_hex_index] = constJersi.undefined
            self.hex_status[src_hex_index] = TypeHexStatus.has_no_cube

            if self.hex_status[dst_hex_index] == TypeHexStatus.has_no_cube:

                self.hex_bottom[dst_hex_index] = cube_index
                self.hex_status[dst_hex_index] = TypeHexStatus.has_one_cube

                self.cube_hex[cube_index] = dst_hex_index
                self.cube_level[cube_index] = TypeHexLevel.bottom

            elif self.hex_status[dst_hex_index] == TypeHexStatus.has_one_cube:

                self.hex_top[dst_hex_index] = cube_index
                self.hex_status[dst_hex_index] = TypeHexStatus.has_two_cubes_cube

                self.cube_hex[cube_index] = dst_hex_index
                self.cube_hex_level[cube_index] = TypeHexLevel.top

            else:
                assert self.hex_status[dst_hex_index] in [TypeHexStatus.has_no_cube,
                                                          TypeHexStatus.has_one_cube]


        elif self.hex_status[src_hex_index] == TypeHexStatus.has_two_cubes:

            cube_index = self.hex_top[src_hex_index]
            assert cube_index != constJersi.undefined

            self.hex_top[src_hex_index] = constJersi.undefined
            self.hex_status[src_hex_index] = TypeHexStatus.has_one_cube

            if self.hex_status[dst_hex_index] == TypeHexStatus.has_no_cube:

                self.hex_bottom[dst_hex_index] = cube_index
                self.hex_status[dst_hex_index] = TypeHexStatus.has_one_cube

                self.cube_hex[cube_index] = dst_hex_index
                self.cube_hex_level[cube_index] = TypeHexLevel.bottom

            elif self.hex_status[dst_hex_index] == TypeHexStatus.has_one_cube:

                self.hex_top[dst_hex_index] = cube_index
                self.hex_status[dst_hex_index] = TypeHexStatus.has_two_cubes_cube

                self.cube_hex[cube_index] = dst_hex_index
                self.cube_hex_level[cube_index] = TypeHexLevel.top

            else:
                assert self.hex_status[dst_hex_index] in [TypeHexStatus.has_no_cube,
                                                          TypeHexStatus.has_one_cube]

        else:
            assert self.hex_status[src_hex_index] in [TypeHexStatus.has_one_cube,
                                                      TypeHexStatus.has_two_cubes]


    def move_stack(self, src_hex_index, dst_hex_index):

        assert self.hex_status[src_hex_index] == TypeHexStatus.has_two_cubes
        assert self.hex_status[dst_hex_index] == TypeHexStatus.has_no_cube

        top_cube_index = self.hex_top[src_hex_index]
        bottom_cube_index = self.hex_bottom[src_hex_index]

        self.hex_top[dst_hex_index] = top_cube_index
        self.hex_bottom[dst_hex_index] = bottom_cube_index
        self.hex_status[dst_hex_index] = TypeHexStatus.has_two_cubes

        self.hex_top[src_hex_index] = constJersi.undefined
        self.hex_bottom[src_hex_index] = bottom_cube_index
        self.hex_status[src_hex_index] = TypeHexStatus.has_no_cube

        self.cube_hex[top_cube_index] = dst_hex_index
        self.cube_hex_level[top_cube_index] = TypeHexLevel.top

        self.cube_hex[bottom_cube_index] = dst_hex_index
        self.cube_hex_level[bottom_cube_index] = TypeHexLevel.bottom


    def capture_cube(self, hex_index):

        if self.hex_status[hex_index] == TypeHexStatus.has_one_cube:

            cube_index = self.hex_bottom[hex_index]
            assert cube_index != constJersi.undefined

            self.cube_status[cube_index] = TypeCubeStatus.captured
            self.cube_hex[cube_index] = constJersi.undefined
            self.cube_hex_level[cube_index] = constJersi.undefined

            self.hex_bottom[hex_index] = constJersi.undefined
            self.hex_status[hex_index] = TypeHexStatus.has_no_cube

        elif self.hex_status[hex_index] == TypeHexStatus.has_two_cubes:

            cube_index = self.hex_top[hex_index]
            assert cube_index != constJersi.undefined

            self.cube_status[cube_index] = TypeCubeStatus.captured
            self.cube_hex[cube_index] = constJersi.undefined
            self.cube_hex_level[cube_index] = constJersi.undefined

            self.hex_top[hex_index] = constJersi.undefined
            self.hex_status[hex_index] = TypeHexStatus.has_one_cube

        else:
            assert self.hex_status[hex_index] in [TypeHexStatus.has_one_cube,
                                                  TypeHexStatus.has_two_cubes]


    def capture_stack(self, hex_index):

        assert self.hex_status[hex_index] == TypeHexStatus.has_two_cubes

        top_cube_index = self.hex_top[hex_index]
        bottom_cube_index = self.hex_bottom[hex_index]

        self.cube_status[top_cube_index] = TypeCubeStatus.captured
        self.cube_status[bottom_cube_index] = TypeCubeStatus.captured

        self.cube_hex[top_cube_index] = constJersi.undefined
        self.cube_hex[bottom_cube_index] = constJersi.undefined

        self.cube_hex_level[top_cube_index] = constJersi.undefined
        self.cube_hex_level[bottom_cube_index] = constJersi.undefined

        self.hex_top[hex_index] = constJersi.undefined
        self.hex_bottom[hex_index] = constJersi.undefined

        self.hex_status[hex_index] = TypeHexStatus.has_no_cube


    def take_action(self, action):
        return action.next_state


    def is_terminal(self):

        if self.terminal is None:

            self.terminal = False

            # indices_of_cubes_at_white_ends = self.hex_bottom[constHex.kind_ends[TypeCubeColor.white]]
            # indices_of_cubes_at_white_ends = indices_of_cubes_at_white_ends[indices_of_cubes_at_white_ends != constJersi.undefined]
            # white_arrived = np.any(constCube.color[indices_of_cubes_at_white_ends] == TypeCubeColor.white)

            # indices_of_cubes_at_black_ends = self.hex_bottom[constHex.kind_ends[TypeCubeColor.black]]
            # indices_of_cubes_at_black_ends = indices_of_cubes_at_black_ends[indices_of_cubes_at_black_ends != constJersi.undefined]
            # black_arrived = np.any(constCube.color[indices_of_cubes_at_black_ends] == TypeCubeColor.black)

            if self.cube_hex[constCube.white_king] in constHex.kind_ends[TypeCubeColor.white]:
            #if white_arrived:
                # white arrived at goal ==> white wins
                self.terminal = True
                self.rewards = np.zeros(TypeCubeColor.count, dtype=np.int8)
                self.rewards[TypeCubeColor.white] = 1
                self.rewards[TypeCubeColor.black] = -1

            elif self.cube_hex[constCube.black_king] in constHex.kind_ends[TypeCubeColor.black]:
            #elif black_arrived:
                # black arrived at goal ==> black wins
                self.terminal = True
                self.rewards = np.zeros(TypeCubeColor.count, dtype=np.int8)
                self.rewards[TypeCubeColor.black] = 1
                self.rewards[TypeCubeColor.white] = -1

            elif self.credit == 0:
                # credit is exhausted ==> nobody wins
                self.terminal = True
                self.rewards = np.zeros(TypeCubeColor.count, dtype=np.int8)
                self.rewards[TypeCubeColor.white] = 0
                self.rewards[TypeCubeColor.black] = 0

            elif len(self.get_actions()) == 0:
                # the current player looses and the other player wins
                self.terminal = True
                self.rewards = np.zeros(TypeCubeColor.count, dtype=np.int8)

                if self.player == constCube.white_king:
                    self.rewards[TypeCubeColor.white] = -1
                    self.rewards[TypeCubeColor.black] = 1
                else:
                    self.rewards[TypeCubeColor.black] = -1
                    self.rewards[TypeCubeColor.white] = 1

        return self.terminal


    def get_reward(self):
        assert self.terminal
        return self.rewards


    def show(self):

        shift = " " * len("a1KR")

        print()

        for (row_shift_count, row_hex_ids) in constHex.layout:

            row_text = shift*row_shift_count

            for hex_id in row_hex_ids:

                hex_index = np.argwhere(constHex.domain == hex_id)[0][0]
                row_text += "%s" % hex_id

                if self.hex_status[hex_index] == TypeHexStatus.has_no_cube:
                    row_text += ".."

                elif self.hex_status[hex_index] == TypeHexStatus.has_one_cube:

                    bottom_cube_index = self.hex_bottom[hex_index]
                    bottom_cube_csort_index = constCube.csort[bottom_cube_index]
                    bottom_cube_csort = TypeCubeColoredSort.domain[bottom_cube_csort_index]

                    row_text += ".%s" % bottom_cube_csort

                elif self.hex_status[hex_index] == TypeHexStatus.has_two_cubes:

                    top_cube_index = self.hex_top[hex_index]
                    bottom_cube_index = self.hex_bottom[hex_index]

                    top_cube_csort_index = constCube.csort[top_cube_index]
                    bottom_cube_csort_index = constCube.csort[bottom_cube_index]

                    top_cube_csort = TypeCubeColoredSort.domain[top_cube_csort_index]
                    bottom_cube_csort = TypeCubeColoredSort.domain[bottom_cube_csort_index]

                    row_text += "%s%s" % (top_cube_csort, bottom_cube_csort)

                else:
                    assert self.hex_status[hex_index] in [TypeHexStatus.has_no_cube,
                                                          TypeHexStatus.has_one_cube,
                                                          TypeHexStatus.has_two_cubes]
                row_text += shift
            print(row_text)


        cube_reserved_selection = (self.cube_status == TypeCubeStatus.reserved)
        cube_csort_reserved_selection = constCube.csort[cube_reserved_selection]

        cube_csort_id_reserved_list = list(map(lambda x: TypeCubeColoredSort.domain[x], cube_csort_reserved_selection))
        cube_csort_id_reserved_list.sort()

        reserve_text = " ".join(cube_csort_id_reserved_list)
        print()
        print("reserved: %s" % reserve_text)


    def next_player(self):
        return (self.player + 1) % TypeCubeColor.count


    def previous_player(self):
        return (self.player + 1) % TypeCubeColor.count


    def encode_state(self):

        # Encode together cube_status and cube_level
        assert TypeHexLevel.bit_size + TypeCubeStatus.bit_size <= constJersi.byte_bit_size
        status_level_code = bytes((2**TypeHexLevel.bit_size)*(self.cube_status - constJersi.undefined) +
                                  (self.cube_level - constJersi.undefined))

        # Encode cube_hex
        assert constHex.bit_size <= constJersi.byte_bit_size
        hex_code = bytes(self.cube_hex - constJersi.undefined)

        # Encode together player and credit
        assert TypeCubeColor.bit_size + constJersi.credit_bit_size <= constJersi.byte_bit_size
        player_credit_code = bytes([(2**TypeCubeColor.bit_size)*self.player + self.credit])

        # Concatenate all codes
        state_code = status_level_code + hex_code + player_credit_code

        return state_code


    def set_cube_in_reserve(self, cube_color_index, cube_sort_index):

        free_cube_indexes = constCube.codomain[(constCube.color == cube_color_index) &
                                   (constCube.sort == cube_sort_index) &
                                   (self.cube_status == constJersi.undefined)]

        assert free_cube_indexes.size != 0
        cube_index = free_cube_indexes[0]
        self.cube_status[cube_index] = TypeCubeStatus.reserved


    def set_cube_at_hexagon(self, cube_color_index, cube_sort_index, hex_index):

        free_cube_indexes = constCube.codomain[(constCube.color == cube_color_index) &
                                   (constCube.sort == cube_sort_index) &
                                   (self.cube_status == constJersi.undefined)]

        assert free_cube_indexes.size != 0
        cube_index = free_cube_indexes[0]
        self.cube_status[cube_index] = TypeCubeStatus.active

        if self.hex_status[hex_index] == TypeHexStatus.has_no_cube:

            self.hex_bottom[hex_index] = cube_index
            self.hex_status[hex_index] = TypeHexStatus.has_one_cube

            self.cube_hex[cube_index] = hex_index
            self.cube_level[cube_index] = TypeHexLevel.bottom

        elif self.hex_status[hex_index] == TypeHexStatus.has_one_cube:

            self.hex_top[hex_index] = cube_index
            self.hex_status[hex_index] = TypeHexStatus.has_two_cubes

            self.cube_hex[cube_index] = hex_index
            self.cube_level[cube_index] = TypeHexLevel.top

        else:
            assert self.hex_status[hex_index] in [TypeHexStatus.has_no_cube, TypeHexStatus.has_one_cube]


    def set_cube_in_reserve_by_id(self, cube_csort_id):

        cube_csort_index = np.argwhere(TypeCubeColoredSort.domain == cube_csort_id)[0][0]
        cube_color_index = TypeCubeColoredSort.color[cube_csort_index]
        cube_sort_index = TypeCubeColoredSort.sort[cube_csort_index]

        self.set_cube_in_reserve(cube_color_index, cube_sort_index)


    def set_cube_at_hexagon_by_id(self, cube_csort_id, hex_id):

        hex_index = np.argwhere(constHex.domain == hex_id)[0][0]

        cube_csort_index = np.argwhere(TypeCubeColoredSort.domain == cube_csort_id)[0][0]
        cube_color_index = TypeCubeColoredSort.color[cube_csort_index]
        cube_sort_index = TypeCubeColoredSort.sort[cube_csort_index]

        self.set_cube_at_hexagon(cube_color_index, cube_sort_index, hex_index)


    def clear_all_cubes(self):

        self.cube_status[:] = constJersi.undefined
        self.cube_hex[:] = constJersi.undefined
        self.cube_level[:] = constJersi.undefined

        self.hex_status[:] = TypeHexStatus.has_no_cube
        self.hex_bottom[:] = constJersi.undefined
        self.hex_top[:] = constJersi.undefined


    def set_all_cubes(self):

        self.clear_all_cubes()

        # whites
        # self.set_cube_at_hexagon_by_id('F', 'b1')
        self.set_cube_at_hexagon_by_id('F', 'b8')
        self.set_cube_at_hexagon_by_id('K', 'a4')

        # self.set_cube_at_hexagon_by_id('R', 'b2')
        # self.set_cube_at_hexagon_by_id('P', 'b3')
        # self.set_cube_at_hexagon_by_id('S', 'b4')
        # self.set_cube_at_hexagon_by_id('R', 'b5')
        # self.set_cube_at_hexagon_by_id('P', 'b6')
        # self.set_cube_at_hexagon_by_id('S', 'b7')

        # self.set_cube_at_hexagon_by_id('R', 'a3')
        # self.set_cube_at_hexagon_by_id('S', 'a2')
        # self.set_cube_at_hexagon_by_id('P', 'a1')
        # self.set_cube_at_hexagon_by_id('S', 'a5')
        # self.set_cube_at_hexagon_by_id('R', 'a6')
        # self.set_cube_at_hexagon_by_id('P', 'a7')

        # blacks
        self.set_cube_at_hexagon_by_id('f', 'h1')
        # self.set_cube_at_hexagon_by_id('f', 'h8')
        self.set_cube_at_hexagon_by_id('k', 'i4')

        # self.set_cube_at_hexagon_by_id('r', 'h7')
        # self.set_cube_at_hexagon_by_id('p', 'h6')
        # self.set_cube_at_hexagon_by_id('s', 'h5')
        # self.set_cube_at_hexagon_by_id('r', 'h4')
        # self.set_cube_at_hexagon_by_id('p', 'h3')
        # self.set_cube_at_hexagon_by_id('s', 'h2')

        # self.set_cube_at_hexagon_by_id('r', 'i5')
        # self.set_cube_at_hexagon_by_id('s', 'i6')
        # self.set_cube_at_hexagon_by_id('p', 'i7')
        # self.set_cube_at_hexagon_by_id('s', 'i3')
        # self.set_cube_at_hexagon_by_id('r', 'i2')
        # self.set_cube_at_hexagon_by_id('p', 'i1')

        # white reserve
        self.set_cube_in_reserve_by_id('W')
        self.set_cube_in_reserve_by_id('W')

        self.set_cube_in_reserve_by_id('M')
        self.set_cube_in_reserve_by_id('M')

        self.set_cube_in_reserve_by_id('M')
        self.set_cube_in_reserve_by_id('M')

        # black reserve
        self.set_cube_in_reserve_by_id('m')
        self.set_cube_in_reserve_by_id('m')

        self.set_cube_in_reserve_by_id('m')
        self.set_cube_in_reserve_by_id('m')

        self.set_cube_in_reserve_by_id('w')
        self.set_cube_in_reserve_by_id('w')


    def count_per_color_and_sort(self):
        active_counter = np.zeros((TypeCubeColor.count, TypeCubeSort.count), dtype=np.int8)
        capture_counter = np.zeros((TypeCubeColor.count, TypeCubeSort.count), dtype=np.int8)
        reserve_counter = np.zeros((TypeCubeColor.count, TypeCubeSort.count), dtype=np.int8)

        for cube_color_index in TypeCubeColor.codomain:
            cube_color_selection = (constCube.color == cube_color_index)

            for cube_sort_index in TypeCubeSort.codomain:
                cube_sort_selection = (constCube.sort == cube_sort_index)

                active_counter[cube_color_index, cube_sort_index] = np.count_nonzero(
                    cube_color_selection &
                    cube_sort_selection &
                    (self.cube_status == TypeCubeStatus.active) )

                capture_counter[cube_color_index, cube_sort_index] = np.count_nonzero(
                    cube_color_selection &
                    cube_sort_selection &
                    (self.cube_status == TypeCubeStatus.captured) )

                reserve_counter[cube_color_index, cube_sort_index] = np.count_nonzero(
                    cube_color_selection &
                    cube_sort_selection &
                    (self.cube_status == TypeCubeStatus.reserved) )


        return (active_counter, capture_counter, reserve_counter)


class JersiAction:


    def __init__(self, action_notation, next_state):
        self.action_notation = action_notation
        self.next_state = next_state


    def __str__(self):
        return str(self.action_notation)


    def __repr__(self):
        return str(self)


    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.action_notation == other.action_notation


    def __hash__(self):
        return hash(self.action_notation)


def random_searcher(js):
    actions = js.get_actions()
    action = random.choice(actions)
    return action


def make_mcts_searcher(time_limit=None, iteration_limit=None):

    assert time_limit is None or iteration_limit is None

    if time_limit is None and iteration_limit is None:
        time_limit = 1_000

    def mcts_searcher(js):

        # mcts uses the following formulation with explorationValue=explorationConstant ;
        # so in order to match the most current found formula one selects explorationConstant=1.
        #
        # nodeValue = node.state.getCurrentPlayer() * child.totalReward / child.numVisits +
        #             explorationValue * math.sqrt(2 * math.log(node.numVisits) / child.numVisits)

        my_exploration_constant = 1.

        if time_limit is not None:
            # time in milli-seconds
            searcher = mcts.mcts(timeLimit=time_limit, explorationConstant=my_exploration_constant)

        elif iteration_limit is not None:
            # number of mcts rounds
            searcher = mcts.mcts(iterationLimit=iteration_limit, explorationConstant=my_exploration_constant)

        action = searcher.search(initialState=js)

        if constJersi.do_debug:
            print(f"{searcher.root.numVisits=!s}")
            print(f"{searcher.root.totalReward=!s}")
            print(f"{searcher.root.isFullyExpanded=!s}")
            print(f"{len(searcher.root.children)=!s}")
            if True:
                for (child_key, child) in searcher.root.children.items():
                    print("--------------------------------")
                    print(f"   child {child_key}")
                    print(f"   {child.numVisits=!s}")
                    print(f"   {child.totalReward=!s}")

        return action

    return mcts_searcher

searcher_catalog = dict()

searcher_catalog["random"] = random_searcher

searcher_catalog["mcts-s-1"] = make_mcts_searcher(time_limit=1_000)
searcher_catalog["mcts-s-2"] = make_mcts_searcher(time_limit=2_000)
searcher_catalog["mcts-s-5"] = make_mcts_searcher(time_limit=5_000)
searcher_catalog["mcts-s-10"] = make_mcts_searcher(time_limit=10_000)
searcher_catalog["mcts-s-20"] = make_mcts_searcher(time_limit=20_000)
searcher_catalog["mcts-s-30"] = make_mcts_searcher(time_limit=30_000)
searcher_catalog["mcts-s-60"] = make_mcts_searcher(time_limit=60_000)

searcher_catalog["mcts-i-50"] = make_mcts_searcher(iteration_limit=50)
searcher_catalog["mcts-i-100"] = make_mcts_searcher(iteration_limit=100)
searcher_catalog["mcts-i-500"] = make_mcts_searcher(iteration_limit=500)
searcher_catalog["mcts-i-1k"] = make_mcts_searcher(iteration_limit=1_000)
searcher_catalog["mcts-i-10k"] = make_mcts_searcher(iteration_limit=10_000)


class Simulation:

    def __init__(self):
        self.selected_searcher_name = [None, None]
        self.selected_searcher = [None, None]

        self.js = None
        self.iter_count = None
        self.iter_index = None
        self.log = None


    def set_white_player(self, name):
        self.selected_searcher_name[TypeCubeColor.white] = name
        self.selected_searcher[TypeCubeColor.white] = searcher_catalog[self.selected_searcher_name[TypeCubeColor.white]]


    def set_black_player(self, name):
        self.selected_searcher_name[TypeCubeColor.black] = name
        self.selected_searcher[TypeCubeColor.black] = searcher_catalog[self.selected_searcher_name[TypeCubeColor.black]]


    def start(self):

        assert self.selected_searcher_name[TypeCubeColor.white] is not None
        assert self.selected_searcher_name[TypeCubeColor.black] is not None

        assert self.selected_searcher[TypeCubeColor.white] is not None
        assert self.selected_searcher[TypeCubeColor.black] is not None

        self.js = JersiState()
        self.js.show()

        self.iter_count = 100
        self.iter_index = 0

        self.log = ""


    def get_log(self):
        return self.log


    def has_next(self):
        return self.iter_index < self.iter_count and not self.js.is_terminal()


    def next(self):

        self.log = ""

        if self.has_next():
            player = self.js.get_player()
            player_name = f"{TypeCubeColor.domain[player]}-{self.selected_searcher_name[player]}"
            action_count = len(self.js.get_actions())

            print()
            print(f"{player_name} is thinking ...")

            if self.selected_searcher[player] != random_searcher:
                self.js.set_mcts_player(player)

            action = self.selected_searcher[player](self.js)

            print(f"{player_name} is done")

            self.log = f"iteration {self.iter_index}: {player_name} selects {action} amongst {action_count} actions"
            print(self.log)
            print("-"*40)

            self.js = self.js.take_action(action)
            self.js.show()

            self.iter_index += 1

        if self.js.is_terminal():

            reward = self.js.get_reward()
            player = self.js.get_player()

            print()
            print("-"*40)

            white_player = f"{TypeCubeColor.domain[TypeCubeColor.white]}-{self.selected_searcher_name[TypeCubeColor.white]}"
            black_player = f"{TypeCubeColor.domain[TypeCubeColor.black]}-{self.selected_searcher_name[TypeCubeColor.black]}"

            if reward[TypeCubeColor.white] == reward[TypeCubeColor.black]:
                self.log = f"nobody wins ; the game is a draw between {white_player} and {black_player}"
                print(self.log)

            elif reward[TypeCubeColor.white] > reward[TypeCubeColor.black]:
                self.log = f"{white_player} wins against {black_player}"
                print(self.log)

            else:
                self.log = f"{black_player} wins against {white_player}"
                print(self.log)

        else:
            print()
            print("-"*40)
            print("not a terminal state")


def main():

    print()
    print("Hello!")

    simulation = Simulation()

    simulation.set_white_player(random.choice(list(searcher_catalog.keys())))
    simulation.set_black_player(random.choice(list(searcher_catalog.keys())))

    simulation.start()

    while simulation.has_next():
        simulation.next()

    print()
    print("Bye!")


if __name__ == "__main__":

    if True:
        main()
    else:
        cProfile.run("main()")
        #print(timeit.timeit("main()", setup="from __main__ import main", number=1))
