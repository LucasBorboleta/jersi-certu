# -*- coding: utf-8 -*-
"""
Data structure for "jersi" game : fast when performance is required.
"""

import numpy as np


print()
print("Hello!")

UNDEFINED = -1

# Define cube color domain

CUBE_COLOR_DOMAIN = np.array(["BLACK", "WHITE"])
CUBE_COLOR_COUNT = CUBE_COLOR_DOMAIN.size
CUBE_COLOR_CODOMAIN = np.arange(CUBE_COLOR_COUNT, dtype=np.int8)
CUBE_COLOR_FUNCTION = np.array([str.upper, str.lower])

print()
print(f"{CUBE_COLOR_COUNT=!s}")
print(f"{CUBE_COLOR_DOMAIN=!s}")
print(f"{CUBE_COLOR_CODOMAIN=!s}")

assert CUBE_COLOR_FUNCTION.size == CUBE_COLOR_COUNT
assert np.unique(CUBE_COLOR_DOMAIN).size == CUBE_COLOR_COUNT

CUBE_COLOR_BLACK = np.argwhere(CUBE_COLOR_DOMAIN == "BLACK")[0][0]
CUBE_COLOR_WHITE = np.argwhere(CUBE_COLOR_DOMAIN == "WHITE")[0][0]
print(f"{CUBE_COLOR_BLACK=!s}")
print(f"{CUBE_COLOR_WHITE=!s}")


# Define cube type domain

CUBE_TYPE_DOMAIN = np.array(["FOUL", "KING", "MOUNTAIN", "PAPER", "ROCK", "SCISSORS", "WISE"])
CUBE_TYPE_COUNT = CUBE_TYPE_DOMAIN.size
CUBE_TYPE_CODOMAIN = np.arange(CUBE_TYPE_COUNT, dtype=np.int8)
CUBE_TYPE_KEY = np.vectorize(lambda x:x[0].upper())(CUBE_TYPE_DOMAIN)

print()
print(f"{CUBE_TYPE_DOMAIN=!s}")
print(f"{CUBE_TYPE_KEY=!s}")
print(f"{CUBE_TYPE_CODOMAIN=!s}")
print(f"{CUBE_TYPE_COUNT=!s}")

assert CUBE_TYPE_KEY.size == CUBE_TYPE_COUNT
assert np.unique(CUBE_TYPE_DOMAIN).size == CUBE_TYPE_COUNT
assert np.unique(CUBE_TYPE_KEY).size == CUBE_TYPE_COUNT

CUBE_TYPE_FOUL = np.argwhere(CUBE_TYPE_DOMAIN == "FOUL")[0][0]
CUBE_TYPE_KING = np.argwhere(CUBE_TYPE_DOMAIN == "KING")[0][0]
CUBE_TYPE_MOUNTAIN = np.argwhere(CUBE_TYPE_DOMAIN == "MOUNTAIN")[0][0]
CUBE_TYPE_PAPER = np.argwhere(CUBE_TYPE_DOMAIN == "PAPER")[0][0]
CUBE_TYPE_ROCK = np.argwhere(CUBE_TYPE_DOMAIN == "ROCK")[0][0]
CUBE_TYPE_SCISSORS = np.argwhere(CUBE_TYPE_DOMAIN == "SCISSORS")[0][0]
CUBE_TYPE_WISE = np.argwhere(CUBE_TYPE_DOMAIN == "WISE")[0][0]

print(f"{CUBE_TYPE_FOUL=!s}")
print(f"{CUBE_TYPE_KING=!s}")
print(f"{CUBE_TYPE_MOUNTAIN=!s}")
print(f"{CUBE_TYPE_PAPER=!s}")
print(f"{CUBE_TYPE_ROCK=!s}")
print(f"{CUBE_TYPE_SCISSORS=!s}")
print(f"{CUBE_TYPE_WISE=!s}")


# Define cube colored type

CUBE_CTYPE_COUNT = CUBE_COLOR_COUNT*CUBE_TYPE_COUNT
CUBE_CTYPE_CODOMAIN = np.arange(CUBE_CTYPE_COUNT, dtype=np.int8)
CUBE_CTYPE_COLOR = np.full(CUBE_CTYPE_COUNT, UNDEFINED, dtype=np.int8)
CUBE_CTYPE_TYPE = np.full(CUBE_CTYPE_COUNT, UNDEFINED, dtype=np.int8)

cube_ctype_id_list = list()

for cube_color_index in CUBE_COLOR_CODOMAIN:
    cube_color_function = CUBE_COLOR_FUNCTION[cube_color_index]

    for (cube_type_index, cube_type_key) in enumerate(CUBE_TYPE_KEY):

            cube_ctype_index = len(cube_ctype_id_list)

            cube_ctype_id = cube_color_function(cube_type_key)
            cube_ctype_id_list.append(cube_ctype_id)

            CUBE_CTYPE_COLOR[cube_ctype_index] = cube_color_index
            CUBE_CTYPE_TYPE[cube_ctype_index] = cube_type_index

CUBE_CTYPE_DOMAIN = np.array(cube_ctype_id_list)

print()
print(f"{CUBE_CTYPE_DOMAIN=!s}")
print(f"{CUBE_CTYPE_COLOR=!s}")
print(f"{CUBE_CTYPE_TYPE=!s}")
print(f"{CUBE_CTYPE_CODOMAIN=!s}")
print(f"{CUBE_CTYPE_COUNT=!s}")

assert CUBE_CTYPE_DOMAIN.size == CUBE_CTYPE_COUNT
assert np.unique(CUBE_CTYPE_DOMAIN).size == CUBE_CTYPE_COUNT


# Define multiplicity of each cube type per color

CUBE_TYPE_MULTIPLICITY  = np.zeros(CUBE_TYPE_COUNT, dtype=np.int8)
CUBE_TYPE_MULTIPLICITY[CUBE_TYPE_FOUL] = 2
CUBE_TYPE_MULTIPLICITY[CUBE_TYPE_KING] = 1
CUBE_TYPE_MULTIPLICITY[CUBE_TYPE_MOUNTAIN] = 4
CUBE_TYPE_MULTIPLICITY[CUBE_TYPE_PAPER] = 4
CUBE_TYPE_MULTIPLICITY[CUBE_TYPE_ROCK] = 4
CUBE_TYPE_MULTIPLICITY[CUBE_TYPE_SCISSORS] = 4
CUBE_TYPE_MULTIPLICITY[CUBE_TYPE_WISE] = 2
CUBE_TYPE_MULTIPLICITY_SUM = CUBE_TYPE_MULTIPLICITY.sum()

print()
print(f"{CUBE_TYPE_MULTIPLICITY=!s}")
print(f"{CUBE_TYPE_MULTIPLICITY_SUM=!s}")

# Define cube status domain

CUBE_STATUS_DOMAIN = np.array(["ACTIVE", "CAPTURED", "RESERVED"])
CUBE_STATUS_COUNT = CUBE_STATUS_DOMAIN.size
CUBE_STATUS_CODOMAIN = np.arange(CUBE_STATUS_COUNT, dtype=np.int8)

assert np.unique(CUBE_STATUS_DOMAIN).size == CUBE_STATUS_COUNT

print()
print(f"{CUBE_STATUS_DOMAIN=!s}")
print(f"{CUBE_STATUS_CODOMAIN=!s}")

CUBE_STATUS_ACTIVE = np.argwhere(CUBE_STATUS_DOMAIN == "ACTIVE")[0][0]
CUBE_STATUS_CAPTURED = np.argwhere(CUBE_STATUS_DOMAIN == "CAPTURED")[0][0]
CUBE_STATUS_RESERVED = np.argwhere(CUBE_STATUS_DOMAIN == "RESERVED")[0][0]

print(f"{CUBE_STATUS_ACTIVE=!s}")
print(f"{CUBE_STATUS_CAPTURED=!s}")
print(f"{CUBE_STATUS_RESERVED=!s}")


# Define cube identifiers and assign colors and types

CUBE_ID_COUNT = CUBE_COLOR_COUNT*CUBE_TYPE_MULTIPLICITY_SUM
CUBE_ID_CODOMAIN = np.arange(CUBE_ID_COUNT, dtype=np.int8)

CUBE_COLOR = np.full(CUBE_ID_COUNT, UNDEFINED, dtype=np.int8)
CUBE_TYPE = np.full(CUBE_ID_COUNT, UNDEFINED, dtype=np.int8)

cube_id_list = list()

for cube_color_index in CUBE_COLOR_CODOMAIN:
    cube_color_function = CUBE_COLOR_FUNCTION[cube_color_index]

    for (cube_type_index, cube_type_key) in enumerate(CUBE_TYPE_KEY):

        for cube_type_occurrence in range(CUBE_TYPE_MULTIPLICITY[cube_type_index]):
            cube_index = len(cube_id_list)

            cube_id = "%s%d" % (cube_color_function(cube_type_key), cube_type_occurrence)
            cube_id_list.append(cube_id)

            CUBE_COLOR[cube_index] = cube_color_index
            CUBE_TYPE[cube_index] = cube_type_index

CUBE_ID_DOMAIN = np.array(cube_id_list)
assert CUBE_ID_DOMAIN.size == CUBE_ID_COUNT
assert np.unique(CUBE_ID_DOMAIN).size == CUBE_ID_COUNT

print()
print(f"{CUBE_ID_COUNT=!s}")
print(f"{CUBE_ID_DOMAIN=!s}")
print(f"{CUBE_ID_CODOMAIN=!s}")
print(f"{CUBE_COLOR=!s}")
print(f"{CUBE_TYPE=!s}")


# Define hexagon level domain

HEX_LEVEL_DOMAIN = np.array(["BOTTOM", "TOP"])
HEX_LEVEL_COUNT = HEX_LEVEL_DOMAIN.size
HEX_LEVEL_CODOMAIN = np.arange(HEX_LEVEL_COUNT, dtype=np.int8)

assert np.unique(HEX_LEVEL_DOMAIN).size == HEX_LEVEL_COUNT

print()
print(f"{HEX_LEVEL_DOMAIN=!s}")
print(f"{HEX_LEVEL_CODOMAIN=!s}")

HEX_LEVEL_BOTTOM = np.argwhere(HEX_LEVEL_DOMAIN == "BOTTOM")[0][0]
HEX_LEVEL_TOP = np.argwhere(HEX_LEVEL_DOMAIN == "TOP")[0][0]

print(f"{HEX_LEVEL_BOTTOM=!s}")
print(f"{HEX_LEVEL_TOP=!s}")

# Define hex direction domain

HEX_DIRECTION_DOMAIN = np.array(["090", "150", "210", "270", "330", "030"])
HEX_DIRECTION_COUNT = HEX_DIRECTION_DOMAIN.size
HEX_DIRECTION_CODOMAIN = np.arange(HEX_DIRECTION_COUNT, dtype=np.int8)
HEX_DIRECTION_U = np.array([+1, +1, +0, -1, -1, +0])
HEX_DIRECTION_V = np.array([+0, -1, -1, +0, +1, +1])

assert np.unique(HEX_DIRECTION_DOMAIN).size == HEX_DIRECTION_COUNT
assert HEX_DIRECTION_U.size == HEX_DIRECTION_COUNT
assert HEX_DIRECTION_V.size == HEX_DIRECTION_COUNT

print()
print(f"{HEX_DIRECTION_DOMAIN=!s}")
print(f"{HEX_DIRECTION_CODOMAIN=!s}")
print(f"{HEX_DIRECTION_COUNT=!s}")
print(f"{HEX_DIRECTION_U=!s}")
print(f"{HEX_DIRECTION_V=!s}")

# Define hex status domain

HEX_STATUS_DOMAIN = np.array(["HAS_CUBE", "IS_EMPTY", "HAS_STACK"])
CUBE_STATUS_COUNT = HEX_STATUS_DOMAIN.size
HEX_STATUS_CODOMAIN = np.arange(CUBE_STATUS_COUNT, dtype=np.int8)

print()
print(f"{HEX_STATUS_DOMAIN=!s}")
print(f"{HEX_STATUS_CODOMAIN=!s}")

assert np.unique(HEX_STATUS_DOMAIN).size == CUBE_STATUS_COUNT

HEX_STATUS_HAS_ONE_CUBE = np.argwhere(HEX_STATUS_DOMAIN == "HAS_CUBE")[0][0]
HEX_STATUS_HAS_NO_CUBE = np.argwhere(HEX_STATUS_DOMAIN == "IS_EMPTY")[0][0]
HEX_STATUS_HAS_TWO_CUBES = np.argwhere(HEX_STATUS_DOMAIN == "HAS_STACK")[0][0]

print(f"{HEX_STATUS_HAS_ONE_CUBE=!s}")
print(f"{HEX_STATUS_HAS_NO_CUBE=!s}")
print(f"{HEX_STATUS_HAS_TWO_CUBES=!s}")


# Define hex identifiers

hex_id_dict = dict()
hex_uv_dict = dict()

hex_id_list = list()
hex_u_list = list()
hex_v_list = list()


def create_hexagon_at_uv(hex_id, u, v):

    assert len(hex_id) == 2
    assert hex_id not in hex_id_dict
    assert (u,v) not in hex_uv_dict

    hex_index = len(hex_id_list)

    hex_id_dict[hex_id] = hex_index
    hex_uv_dict[(u,v)] = hex_index

    hex_id_list.append(hex_id)
    hex_u_list.append(u)
    hex_v_list.append(v)


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


HEX_ID_DOMAIN = np.array(hex_id_list)
HEX_ID_COUNT = HEX_ID_DOMAIN.size
HEX_ID_CODOMAIN = np.arange(HEX_ID_COUNT, dtype=np.int8)
HEX_COORD_U = np.array(hex_u_list)
HEX_COORD_V = np.array(hex_v_list)

print()
print(f"{HEX_ID_DOMAIN=!s}")
print(f"{HEX_ID_COUNT=!s}")
print(f"{HEX_ID_CODOMAIN=!s}")
print(f"{HEX_COORD_U=!s}")
print(f"{HEX_COORD_V=!s}")

# Define hexs by one or two steps toward a given direction

HEX_NEXT_FST = np.full((HEX_ID_COUNT, HEX_DIRECTION_COUNT), UNDEFINED, dtype=np.int8)
HEX_NEXT_SND = np.full((HEX_ID_COUNT, HEX_DIRECTION_COUNT), UNDEFINED, dtype=np.int8)

for hex_index in HEX_ID_CODOMAIN:
    hex_u = HEX_COORD_U[hex_index]
    hex_v = HEX_COORD_V[hex_index]

    for hex_dir_index in HEX_DIRECTION_CODOMAIN:
        hex_delta_u = HEX_DIRECTION_U[hex_dir_index]
        hex_delta_v = HEX_DIRECTION_V[hex_dir_index]

        hex_fst_u = hex_u + 1*hex_delta_u
        hex_fst_v = hex_v + 1*hex_delta_v

        hex_snd_u = hex_u + 2*hex_delta_u
        hex_snd_v = hex_v + 2*hex_delta_v

        if (hex_fst_u, hex_fst_v) in hex_uv_dict:
            hex_fst_index = hex_uv_dict[(hex_fst_u, hex_fst_v)]
            HEX_NEXT_FST[hex_index, hex_dir_index] = hex_fst_index

            if (hex_snd_u, hex_snd_v) in hex_uv_dict:
                hex_snd_index = hex_uv_dict[(hex_snd_u, hex_snd_v)]
                HEX_NEXT_SND[hex_index, hex_dir_index] = hex_snd_index

print()
print(f"{HEX_NEXT_FST=!s}")
print(f"{HEX_NEXT_SND=!s}")


# Define cube variables properties

cube_status = np.full(CUBE_ID_COUNT, UNDEFINED, dtype=np.int8)
cube_hex = np.full(CUBE_ID_COUNT, UNDEFINED, dtype=np.int8)
cube_hex_level = np.full(CUBE_ID_COUNT, UNDEFINED, dtype=np.int8)
print()
print(f"{cube_status=!s}")
print(f"{cube_hex=!s}")
print(f"{cube_hex_level=!s}")


# Define hex variables properties

hex_status = np.full(HEX_ID_COUNT, UNDEFINED, dtype=np.int8)
hex_bottom = np.full(HEX_ID_COUNT, UNDEFINED, dtype=np.int8)
hex_top = np.full(HEX_ID_COUNT, UNDEFINED, dtype=np.int8)
print()
print(f"{hex_status=!s}")
print(f"{hex_bottom=!s}")
print(f"{hex_top=!s}")


# Initial state for cubes and hexagons

def set_cube_in_reserve(cube_color_index, cube_type_index):

    free_cube_indexes = CUBE_ID_CODOMAIN[(CUBE_COLOR == cube_color_index) &
                               (CUBE_TYPE == cube_type_index) &
                               (cube_status == UNDEFINED)]

    assert free_cube_indexes.size != 0
    cube_index = free_cube_indexes[0]
    cube_status[cube_index] = CUBE_STATUS_RESERVED


def set_cube_at_hexagon(cube_color_index, cube_type_index, hex_index):

    free_cube_indexes = CUBE_ID_CODOMAIN[(CUBE_COLOR == cube_color_index) &
                               (CUBE_TYPE == cube_type_index) &
                               (cube_status == UNDEFINED)]

    assert free_cube_indexes.size != 0
    cube_index = free_cube_indexes[0]
    cube_status[cube_index] = CUBE_STATUS_ACTIVE

    if hex_status[hex_index] == HEX_STATUS_HAS_NO_CUBE:

        hex_bottom[hex_index] = cube_index
        hex_status[hex_index] = HEX_STATUS_HAS_ONE_CUBE

        cube_hex[cube_index] = hex_index
        cube_hex_level[cube_index] = HEX_LEVEL_BOTTOM

    elif hex_status[hex_index] == HEX_STATUS_HAS_ONE_CUBE:

        hex_top[hex_index] = cube_index
        hex_status[hex_index] = HEX_STATUS_HAS_TWO_CUBES

        cube_hex[cube_index] = hex_index
        cube_hex_level[cube_index] = HEX_LEVEL_TOP

    else:
        assert hex_status[hex_index] != HEX_STATUS_HAS_TWO_CUBES


def set_cube_in_reserve_by_id(cube_ctype_id):

    cube_ctype_index = np.argwhere(CUBE_CTYPE_DOMAIN == cube_ctype_id)[0][0]
    cube_color_index = CUBE_CTYPE_COLOR[cube_ctype_index]
    cube_type_index = CUBE_CTYPE_TYPE[cube_ctype_index]

    set_cube_in_reserve(cube_color_index, cube_type_index)


def set_cube_at_hexagon_by_id(cube_ctype_id, hex_id):

    hex_index = np.argwhere(HEX_ID_DOMAIN == hex_id)[0][0]

    cube_ctype_index = np.argwhere(CUBE_CTYPE_DOMAIN == cube_ctype_id)[0][0]
    cube_color_index = CUBE_CTYPE_COLOR[cube_ctype_index]
    cube_type_index = CUBE_CTYPE_TYPE[cube_ctype_index]

    set_cube_at_hexagon(cube_color_index, cube_type_index, hex_index)


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

capture_counter = np.zeros((CUBE_COLOR_COUNT, CUBE_TYPE_COUNT), dtype=np.int8)
reserve_counter = np.zeros((CUBE_COLOR_COUNT, CUBE_TYPE_COUNT), dtype=np.int8)
active_counter = np.zeros((CUBE_COLOR_COUNT, CUBE_TYPE_COUNT), dtype=np.int8)

for cube_color_index in CUBE_COLOR_CODOMAIN:
    for cube_type_index in CUBE_TYPE_CODOMAIN:

        capture_counter[cube_color_index, cube_type_index] = np.count_nonzero(
            (CUBE_COLOR == cube_color_index) &
            (CUBE_TYPE == cube_type_index) &
            (cube_status == CUBE_STATUS_CAPTURED) )

        reserve_counter[cube_color_index, cube_type_index] = np.count_nonzero(
            (CUBE_COLOR == cube_color_index) &
            (CUBE_TYPE == cube_type_index) &
            (cube_status == CUBE_STATUS_RESERVED) )

        active_counter[cube_color_index, cube_type_index] = np.count_nonzero(
            (CUBE_COLOR == cube_color_index) &
            (CUBE_TYPE == cube_type_index) &
            (cube_status == CUBE_STATUS_ACTIVE) )

print()
print(f"{capture_counter=!s}")
print(f"{reserve_counter=!s}")
print(f"{active_counter=!s}")


print()
print("Bye!")