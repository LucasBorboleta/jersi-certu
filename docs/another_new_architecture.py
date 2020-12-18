# -*- coding: utf-8 -*-
"""
Data structure for "jersi" game : fast when performance is required.
"""

import types
import numpy as np


print()
print("Hello!")


# Define jersi constants

def _make_ConstJersi():

    ConstJersi = types.SimpleNamespace()

    ConstJersi.do_debug = True
    ConstJersi.undefined = -1

    if ConstJersi.do_debug:
        print()
        print(f"{ConstJersi.do_debug=!s}")
        print(f"{ConstJersi.undefined=!s}")

    return ConstJersi

ConstJersi = _make_ConstJersi()


# Define cube color type

def _make_TypeCubeColor():

    TypeCubeColor = types.SimpleNamespace()

    TypeCubeColor.domain = np.array(["black", "white"])
    TypeCubeColor.count = TypeCubeColor.domain.size
    TypeCubeColor.function = np.array([str.upper, str.lower])
    TypeCubeColor.codomain = np.arange(TypeCubeColor.count, dtype=np.int8)

    TypeCubeColor.black = np.argwhere(TypeCubeColor.domain == "black")[0][0]
    TypeCubeColor.white = np.argwhere(TypeCubeColor.domain == "white")[0][0]

    if ConstJersi.do_debug:
        print()
        print(f"{TypeCubeColor.count=!s}")
        print(f"{TypeCubeColor.domain=!s}")
        print(f"{TypeCubeColor.codomain=!s}")
        print(f"{TypeCubeColor.function=!s}")

        print(f"{TypeCubeColor.black=!s}")
        print(f"{TypeCubeColor.white=!s}")

    assert TypeCubeColor.function.size == TypeCubeColor.count
    assert np.unique(TypeCubeColor.domain).size == TypeCubeColor.count

    return TypeCubeColor

TypeCubeColor = _make_TypeCubeColor()


# Define cube sort type

def _make_TypeCubeSort():

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

    if ConstJersi.do_debug:
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

        print()
        print(f"{TypeCubeSort.multiplicity=!s}")
        print(f"{TypeCubeSort.multiplicity_sum=!s}")

    assert np.unique(TypeCubeSort.domain).size == TypeCubeSort.count
    assert np.unique(TypeCubeSort.key).size == TypeCubeSort.count

    return TypeCubeSort

TypeCubeSort = _make_TypeCubeSort()


# Define cube colored sort type

def _make_TypeCubeColoredSort():

    TypeCubeColoredSort = types.SimpleNamespace()

    TypeCubeColoredSort.count = TypeCubeColor.count*TypeCubeSort.count
    TypeCubeColoredSort.codomain = np.arange(TypeCubeColoredSort.count, dtype=np.int8)
    TypeCubeColoredSort.color = np.full(TypeCubeColoredSort.count, ConstJersi.undefined, dtype=np.int8)
    TypeCubeColoredSort.type = np.full(TypeCubeColoredSort.count, ConstJersi.undefined, dtype=np.int8)

    cube_csort_id_list = list()

    for cube_color_index in TypeCubeColor.codomain:
        cube_color_function = TypeCubeColor.function[cube_color_index]

        for (cube_sort_index, cube_sort_key) in enumerate(TypeCubeSort.key):

                cube_csort_index = len(cube_csort_id_list)

                cube_csort_id = cube_color_function(cube_sort_key)
                cube_csort_id_list.append(cube_csort_id)

                TypeCubeColoredSort.color[cube_csort_index] = cube_color_index
                TypeCubeColoredSort.type[cube_csort_index] = cube_sort_index

    TypeCubeColoredSort.domain = np.array(cube_csort_id_list)


    if ConstJersi.do_debug:
        print()
        print(f"{TypeCubeColoredSort.count=!s}")
        print(f"{TypeCubeColoredSort.domain=!s}")
        print(f"{TypeCubeColoredSort.codomain=!s}")
        print(f"{TypeCubeColoredSort.color=!s}")
        print(f"{TypeCubeColoredSort.type=!s}")

    assert TypeCubeColoredSort.domain.size == TypeCubeColoredSort.count
    assert np.unique(TypeCubeColoredSort.domain).size == TypeCubeColoredSort.count

    return TypeCubeColoredSort

TypeCubeColoredSort = _make_TypeCubeColoredSort()


# Define cube status type

def _make_TypeCubeStatus():

    TypeCubeStatus = types.SimpleNamespace()

    TypeCubeStatus.domain = np.array(["active", "captured", "reserved"])
    TypeCubeStatus.count = TypeCubeStatus.domain.size
    TypeCubeStatus.codomain = np.arange(TypeCubeStatus.count, dtype=np.int8)

    TypeCubeStatus.active = np.argwhere(TypeCubeStatus.domain == "active")[0][0]
    TypeCubeStatus.captured = np.argwhere(TypeCubeStatus.domain == "captured")[0][0]
    TypeCubeStatus.reserved = np.argwhere(TypeCubeStatus.domain == "reserved")[0][0]

    if ConstJersi.do_debug:
        print()
        print(f"{TypeCubeStatus.count=!s}")
        print(f"{TypeCubeStatus.domain=!s}")
        print(f"{TypeCubeStatus.codomain=!s}")

        print(f"{TypeCubeStatus.active=!s}")
        print(f"{TypeCubeStatus.captured=!s}")
        print(f"{TypeCubeStatus.reserved=!s}")

    assert np.unique(TypeCubeStatus.domain).size == TypeCubeStatus.count

    return TypeCubeStatus

TypeCubeStatus = _make_TypeCubeStatus()


# Define cube constant properties

def _make_ConstCube():

    ConstCube = types.SimpleNamespace()

    ConstCube.count = TypeCubeColor.count*TypeCubeSort.multiplicity_sum
    ConstCube.codomain = np.arange(ConstCube.count, dtype=np.int8)
    ConstCube.color = np.full(ConstCube.count, ConstJersi.undefined, dtype=np.int8)
    ConstCube.sort = np.full(ConstCube.count, ConstJersi.undefined, dtype=np.int8)

    cube_id_list = list()

    for cube_color_index in TypeCubeColor.codomain:
        cube_color_function = TypeCubeColor.function[cube_color_index]

        for (cube_sort_index, cube_sort_key) in enumerate(TypeCubeSort.key):

            for ConstCube.sort_occurrence in range(TypeCubeSort.multiplicity[cube_sort_index]):
                cube_index = len(cube_id_list)

                cube_id = "%s%d" % (cube_color_function(cube_sort_key), ConstCube.sort_occurrence)
                cube_id_list.append(cube_id)

                ConstCube.color[cube_index] = cube_color_index
                ConstCube.sort[cube_index] = cube_sort_index

    ConstCube.domain = np.array(cube_id_list)

    assert ConstCube.domain.size == ConstCube.count
    assert np.unique(ConstCube.domain).size == ConstCube.count

    if ConstJersi.do_debug:
        print()
        print(f"{ConstCube.count=!s}")
        print(f"{ConstCube.domain=!s}")
        print(f"{ConstCube.codomain=!s}")
        print(f"{ConstCube.color=!s}")
        print(f"{ConstCube.sort=!s}")

    return ConstCube

ConstCube = _make_ConstCube()


# Define hexagon level type

def _make_TypeHexLevel():

    TypeHexLevel = types.SimpleNamespace()

    TypeHexLevel.domain = np.array(["bottom", "top"])
    TypeHexLevel.count = TypeHexLevel.domain.size
    TypeHexLevel.codomain = np.arange(TypeHexLevel.count, dtype=np.int8)

    TypeHexLevel.bottom = np.argwhere(TypeHexLevel.domain == "bottom")[0][0]
    TypeHexLevel.top = np.argwhere(TypeHexLevel.domain == "top")[0][0]

    if ConstJersi.do_debug:
        print()
        print(f"{TypeHexLevel.count=!s}")
        print(f"{TypeHexLevel.domain=!s}")
        print(f"{TypeHexLevel.codomain=!s}")

        print(f"{TypeHexLevel.bottom=!s}")
        print(f"{TypeHexLevel.top=!s}")

    assert np.unique(TypeHexLevel.domain).size == TypeHexLevel.count

    return TypeHexLevel

TypeHexLevel = _make_TypeHexLevel()


# Define hexagon status type

def _make_TypeHexStatus():

    TypeHexStatus = types.SimpleNamespace()

    TypeHexStatus.domain = np.array(["has_no_cube", "has_one_cube", "has_two_cubes"])
    TypeHexStatus.count = TypeHexStatus.domain.size
    TypeHexStatus.codomain = np.arange(TypeHexStatus.count, dtype=np.int8)

    TypeHexStatus.has_no_cube = np.argwhere(TypeHexStatus.domain == "has_no_cube")[0][0]
    TypeHexStatus.has_one_cube = np.argwhere(TypeHexStatus.domain == "has_one_cube")[0][0]
    TypeHexStatus.has_two_cubes = np.argwhere(TypeHexStatus.domain == "has_two_cubes")[0][0]

    if ConstJersi.do_debug:
        print()
        print(f"{TypeHexStatus.count=!s}")
        print(f"{TypeHexStatus.domain=!s}")
        print(f"{TypeHexStatus.codomain=!s}")

        print(f"{TypeHexStatus.has_no_cube=!s}")
        print(f"{TypeHexStatus.has_one_cube=!s}")
        print(f"{TypeHexStatus.has_two_cubes=!s}")

    assert np.unique(TypeHexStatus.domain).size == TypeHexStatus.count

    return TypeHexStatus

TypeHexStatus = _make_TypeHexStatus()


# Define hexagon direction type

def _make_TypeHexDirection():

    TypeHexDirection = types.SimpleNamespace()

    TypeHexDirection.domain = np.array(["090", "150", "210", "270", "330", "030"])
    TypeHexDirection.count = TypeHexDirection.domain.size
    TypeHexDirection.codomain = np.arange(TypeHexDirection.count, dtype=np.int8)
    TypeHexDirection.delta_u = np.array([+1, +1, +0, -1, -1, +0], dtype=np.int8)
    TypeHexDirection.delta_v = np.array([+0, -1, -1, +0, +1, +1], dtype=np.int8)

    if ConstJersi.do_debug:
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

TypeHexDirection = _make_TypeHexDirection()


# Define hexagon constant properties

def _make_ConstHex():

    def _create_hexagon_at_uv(hex_id, u, v):

        assert len(hex_id) == 2
        assert hex_id not in ConstHex._id_dict
        assert (u,v) not in ConstHex._uv_dict

        hex_index = len(ConstHex._id_list)

        ConstHex._id_dict[hex_id] = hex_index
        ConstHex._uv_dict[(u,v)] = hex_index

        ConstHex._id_list.append(hex_id)
        ConstHex._u_list.append(u)
        ConstHex._v_list.append(v)


    def _create_all_hexagons():

        ConstHex._id_dict = dict()
        ConstHex._uv_dict = dict()

        ConstHex._id_list = list()
        ConstHex._u_list = list()
        ConstHex._v_list = list()

        # Row "a"
        _create_hexagon_at_uv('a1', -1, -4)
        _create_hexagon_at_uv('a2', -0, -4)
        _create_hexagon_at_uv('a3', 1, -4)
        _create_hexagon_at_uv('a4', 2, -4)
        _create_hexagon_at_uv('a5', 3, -4)
        _create_hexagon_at_uv('a6', 4, -4)
        _create_hexagon_at_uv('a7', 5, -4)

        # Row "b"
        _create_hexagon_at_uv('b1', -2, -3)
        _create_hexagon_at_uv('b2', -1, -3)
        _create_hexagon_at_uv('b3', 0, -3)
        _create_hexagon_at_uv('b4', 1, -3)
        _create_hexagon_at_uv('b5', 2, -3)
        _create_hexagon_at_uv('b6', 3, -3)
        _create_hexagon_at_uv('b7', 4, -3)
        _create_hexagon_at_uv('b8', 5, -3)

        # Row "c"
        _create_hexagon_at_uv('c1', -2, -2)
        _create_hexagon_at_uv('c2', -1, -2)
        _create_hexagon_at_uv('c3', 0, -2)
        _create_hexagon_at_uv('c4', 1, -2)
        _create_hexagon_at_uv('c5', 2, -2)
        _create_hexagon_at_uv('c6', 3, -2)
        _create_hexagon_at_uv('c7', 4, -2)

        # Row "d"
        _create_hexagon_at_uv('d1', -3, -1)
        _create_hexagon_at_uv('d2', -2, -1)
        _create_hexagon_at_uv('d3', -1, -1)
        _create_hexagon_at_uv('d4', 0, -1)
        _create_hexagon_at_uv('d5', 1, -1)
        _create_hexagon_at_uv('d6', 2, -1)
        _create_hexagon_at_uv('d7', 3, -1)
        _create_hexagon_at_uv('d8', 4, -1)

        # Row "e"
        _create_hexagon_at_uv('e1', -4, 0)
        _create_hexagon_at_uv('e2', -3, 0)
        _create_hexagon_at_uv('e3', -2, 0)
        _create_hexagon_at_uv('e4', -1, 0)
        _create_hexagon_at_uv('e5', 0, 0)
        _create_hexagon_at_uv('e6', 1, 0)
        _create_hexagon_at_uv('e7', 2, 0)
        _create_hexagon_at_uv('e8', 3, 0)
        _create_hexagon_at_uv('e9', 4, 0)

        # Row "f"
        _create_hexagon_at_uv('f1', -4, 1)
        _create_hexagon_at_uv('f2', -3, 1)
        _create_hexagon_at_uv('f3', -2, 1)
        _create_hexagon_at_uv('f4', -1, 1)
        _create_hexagon_at_uv('f5', 0, 1)
        _create_hexagon_at_uv('f6', 1, 1)
        _create_hexagon_at_uv('f7', 2, 1)
        _create_hexagon_at_uv('f8', 3, 1)

        # Row "g"
        _create_hexagon_at_uv('g1', -4, 2)
        _create_hexagon_at_uv('g2', -3, 2)
        _create_hexagon_at_uv('g3', -2, 2)
        _create_hexagon_at_uv('g4', -1, 2)
        _create_hexagon_at_uv('g5', 0, 2)
        _create_hexagon_at_uv('g6', 1, 2)
        _create_hexagon_at_uv('g7', 2, 2)

        # Row "h"
        _create_hexagon_at_uv('h1', -5, 3)
        _create_hexagon_at_uv('h2', -4, 3)
        _create_hexagon_at_uv('h3', -3, 3)
        _create_hexagon_at_uv('h4', -2, 3)
        _create_hexagon_at_uv('h5', -1, 3)
        _create_hexagon_at_uv('h6', 0, 3)
        _create_hexagon_at_uv('h7', 1, 3)
        _create_hexagon_at_uv('h8', 2, 3)

        # Row "i"
        _create_hexagon_at_uv('i1', -5, 4)
        _create_hexagon_at_uv('i2', -4, 4)
        _create_hexagon_at_uv('i3', -3, 4)
        _create_hexagon_at_uv('i4', -2, 4)
        _create_hexagon_at_uv('i5', -1, 4)
        _create_hexagon_at_uv('i6', 0, 4)
        _create_hexagon_at_uv('i7', 1, 4)

        ConstHex.domain = np.array(ConstHex._id_list)
        ConstHex.count = ConstHex.domain.size
        ConstHex.codomain = np.arange(ConstHex.count, dtype=np.int8)
        ConstHex.coord_u = np.array(ConstHex._u_list)
        ConstHex.coord_v = np.array(ConstHex._v_list)


    def _create_next_hexagons():

        ConstHex.next_fst = np.full((ConstHex.count, TypeHexDirection.count), ConstJersi.undefined, dtype=np.int8)
        ConstHex.next_snd = np.full((ConstHex.count, TypeHexDirection.count), ConstJersi.undefined, dtype=np.int8)

        for hex_index in ConstHex.codomain:
            hex_u = ConstHex.coord_u[hex_index]
            hex_v = ConstHex.coord_v[hex_index]

            for hex_dir_index in TypeHexDirection.codomain:
                hex_delta_u = TypeHexDirection.delta_u[hex_dir_index]
                hex_delta_v = TypeHexDirection.delta_v[hex_dir_index]

                hex_fst_u = hex_u + 1*hex_delta_u
                hex_fst_v = hex_v + 1*hex_delta_v

                hex_snd_u = hex_u + 2*hex_delta_u
                hex_snd_v = hex_v + 2*hex_delta_v

                if (hex_fst_u, hex_fst_v) in ConstHex._uv_dict:
                    hex_fst_index = ConstHex._uv_dict[(hex_fst_u, hex_fst_v)]
                    ConstHex.next_fst[hex_index, hex_dir_index] = hex_fst_index

                    if (hex_snd_u, hex_snd_v) in ConstHex._uv_dict:
                        hex_snd_index = ConstHex._uv_dict[(hex_snd_u, hex_snd_v)]
                        ConstHex.next_snd[hex_index, hex_dir_index] = hex_snd_index


    ConstHex = types.SimpleNamespace()

    _create_all_hexagons()
    _create_next_hexagons()

    if ConstJersi.do_debug:
        print()
        print(f"{ConstHex.count=!s}")
        print(f"{ConstHex.domain=!s}")
        print(f"{ConstHex.codomain=!s}")
        print(f"{ConstHex.coord_u=!s}")
        print(f"{ConstHex.coord_v=!s}")
        print()
        print(f"{ConstHex.next_fst=!s}")
        print(f"{ConstHex.next_snd=!s}")

    return ConstHex

ConstHex = _make_ConstHex()


# Define cube variables properties

cube_status = np.full(ConstCube.count, ConstJersi.undefined, dtype=np.int8)
cube_hex = np.full(ConstCube.count, ConstJersi.undefined, dtype=np.int8)
cube_hex_level = np.full(ConstCube.count, ConstJersi.undefined, dtype=np.int8)
print()
print(f"{cube_status=!s}")
print(f"{cube_hex=!s}")
print(f"{cube_hex_level=!s}")


# Define hexagon variables properties

hex_status = np.full(ConstHex.count, TypeHexStatus.has_no_cube, dtype=np.int8)
hex_bottom = np.full(ConstHex.count, ConstJersi.undefined, dtype=np.int8)
hex_top = np.full(ConstHex.count, ConstJersi.undefined, dtype=np.int8)
print()
print(f"{hex_status=!s}")
print(f"{hex_bottom=!s}")
print(f"{hex_top=!s}")


# Initial state for cubes and hexagons

def set_cube_in_reserve(cube_color_index, cube_sort_index):

    free_cube_indexes = ConstCube.codomain[(ConstCube.color == cube_color_index) &
                               (ConstCube.sort == cube_sort_index) &
                               (cube_status == ConstJersi.undefined)]

    assert free_cube_indexes.size != 0
    cube_index = free_cube_indexes[0]
    cube_status[cube_index] = TypeCubeStatus.reserved


def set_cube_at_hexagon(cube_color_index, cube_sort_index, hex_index):

    free_cube_indexes = ConstCube.codomain[(ConstCube.color == cube_color_index) &
                               (ConstCube.sort == cube_sort_index) &
                               (cube_status == ConstJersi.undefined)]

    assert free_cube_indexes.size != 0
    cube_index = free_cube_indexes[0]
    cube_status[cube_index] = TypeCubeStatus.active

    if hex_status[hex_index] == TypeHexStatus.has_no_cube:

        hex_bottom[hex_index] = cube_index
        hex_status[hex_index] = TypeHexStatus.has_one_cube

        cube_hex[cube_index] = hex_index
        cube_hex_level[cube_index] = TypeHexLevel.bottom

    elif hex_status[hex_index] == TypeHexStatus.has_one_cube:

        hex_top[hex_index] = cube_index
        hex_status[hex_index] = TypeHexStatus.has_two_cubes

        cube_hex[cube_index] = hex_index
        cube_hex_level[cube_index] = TypeHexLevel.top

    else:
        assert hex_status[hex_index] in [TypeHexStatus.has_no_cube, TypeHexStatus.has_one_cube]


def set_cube_in_reserve_by_id(cube_csort_id):

    cube_csort_index = np.argwhere(TypeCubeColoredSort.domain == cube_csort_id)[0][0]
    cube_color_index = TypeCubeColoredSort.color[cube_csort_index]
    cube_sort_index = TypeCubeColoredSort.type[cube_csort_index]

    set_cube_in_reserve(cube_color_index, cube_sort_index)


def set_cube_at_hexagon_by_id(cube_csort_id, hex_id):

    hex_index = np.argwhere(ConstHex.domain == hex_id)[0][0]

    cube_csort_index = np.argwhere(TypeCubeColoredSort.domain == cube_csort_id)[0][0]
    cube_color_index = TypeCubeColoredSort.color[cube_csort_index]
    cube_sort_index = TypeCubeColoredSort.type[cube_csort_index]

    set_cube_at_hexagon(cube_color_index, cube_sort_index, hex_index)


# whites
set_cube_at_hexagon_by_id('F', 'b1')
set_cube_at_hexagon_by_id('F', 'b8')
set_cube_at_hexagon_by_id('K', 'a4')

set_cube_at_hexagon_by_id('R', 'b2')
set_cube_at_hexagon_by_id('P', 'b3')
set_cube_at_hexagon_by_id('S', 'b4')
set_cube_at_hexagon_by_id('R', 'b5')
set_cube_at_hexagon_by_id('P', 'b6')
set_cube_at_hexagon_by_id('S', 'b7')

set_cube_at_hexagon_by_id('R', 'a3')
set_cube_at_hexagon_by_id('S', 'a2')
set_cube_at_hexagon_by_id('P', 'a1')
set_cube_at_hexagon_by_id('S', 'a5')
set_cube_at_hexagon_by_id('R', 'a6')
set_cube_at_hexagon_by_id('P', 'a7')

# blacks
set_cube_at_hexagon_by_id('f', 'h1')
set_cube_at_hexagon_by_id('f', 'h8')
set_cube_at_hexagon_by_id('k', 'i4')

set_cube_at_hexagon_by_id('r', 'h7')
set_cube_at_hexagon_by_id('p', 'h6')
set_cube_at_hexagon_by_id('s', 'h5')
set_cube_at_hexagon_by_id('r', 'h4')
set_cube_at_hexagon_by_id('p', 'h3')
set_cube_at_hexagon_by_id('s', 'h2')

set_cube_at_hexagon_by_id('r', 'i5')
set_cube_at_hexagon_by_id('s', 'i6')
set_cube_at_hexagon_by_id('p', 'i7')
set_cube_at_hexagon_by_id('s', 'i3')
set_cube_at_hexagon_by_id('r', 'i2')
set_cube_at_hexagon_by_id('p', 'i1')

# white reserve
set_cube_in_reserve_by_id('W')
set_cube_in_reserve_by_id('W')

set_cube_in_reserve_by_id('M')
set_cube_in_reserve_by_id('M')

set_cube_in_reserve_by_id('M')
set_cube_in_reserve_by_id('M')

# black reserve
set_cube_in_reserve_by_id('m')
set_cube_in_reserve_by_id('m')

set_cube_in_reserve_by_id('m')
set_cube_in_reserve_by_id('m')

set_cube_in_reserve_by_id('w')
set_cube_in_reserve_by_id('w')


# Try treatments over defined data structures

capture_counter = np.zeros((TypeCubeColor.count, TypeCubeSort.count), dtype=np.int8)
reserve_counter = np.zeros((TypeCubeColor.count, TypeCubeSort.count), dtype=np.int8)
active_counter = np.zeros((TypeCubeColor.count, TypeCubeSort.count), dtype=np.int8)

for cube_color_index in TypeCubeColor.codomain:
    for cube_sort_index in TypeCubeSort.codomain:

        capture_counter[cube_color_index, cube_sort_index] = np.count_nonzero(
            (ConstCube.color == cube_color_index) &
            (ConstCube.sort == cube_sort_index) &
            (cube_status == TypeCubeStatus.captured) )

        reserve_counter[cube_color_index, cube_sort_index] = np.count_nonzero(
            (ConstCube.color == cube_color_index) &
            (ConstCube.sort == cube_sort_index) &
            (cube_status == TypeCubeStatus.reserved) )

        active_counter[cube_color_index, cube_sort_index] = np.count_nonzero(
            (ConstCube.color == cube_color_index) &
            (ConstCube.sort == cube_sort_index) &
            (cube_status == TypeCubeStatus.active) )

print()
print(f"{cube_status=!s}")
print(f"{cube_hex=!s}")
print(f"{cube_hex_level=!s}")

print()
print(f"{hex_status=!s}")
print(f"{hex_bottom=!s}")
print(f"{hex_top=!s}")

print()
print(f"{capture_counter=!s}")
print(f"{reserve_counter=!s}")
print(f"{active_counter=!s}")


print()
print("Bye!")