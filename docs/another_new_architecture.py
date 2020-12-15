# -*- coding: utf-8 -*-
"""
Data structure for "jersi" game : fast when performance is required.
"""

import numpy as np


print()
print("Hello!")

NOT_DEFINED = -1

# Define cube color domain

CUBE_COLOR_DOMAIN = np.array(["BLACK", "WHITE"])
CUBE_COLOR_COUNT = CUBE_COLOR_DOMAIN.size
CUBE_COLOR_CODOMAIN = np.arange(CUBE_COLOR_COUNT, dtype=np.int8)
CUBE_COLOR_KEY = np.vectorize(lambda x:x[0])(CUBE_COLOR_DOMAIN)
CUBE_COLOR_FUN = np.array([str.upper, str.lower])

print()
print(f"{CUBE_COLOR_COUNT=!s}")
print(f"{CUBE_COLOR_DOMAIN=!s}")
print(f"{CUBE_COLOR_CODOMAIN=!s}")
print(f"{CUBE_COLOR_KEY=!s}")

assert CUBE_COLOR_KEY.size == CUBE_COLOR_COUNT
assert CUBE_COLOR_FUN.size == CUBE_COLOR_COUNT
assert np.unique(CUBE_COLOR_DOMAIN).size == CUBE_COLOR_COUNT
assert np.unique(CUBE_COLOR_KEY).size == CUBE_COLOR_COUNT

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


# Define cube colored_type

CUBE_CTYPE_COUNT = CUBE_COLOR_COUNT*CUBE_TYPE_COUNT
CUBE_CTYPE_CODOMAIN = np.arange(CUBE_CTYPE_COUNT, dtype=np.int8)
CUBE_CTYPE_COLOR = np.full(CUBE_CTYPE_COUNT, NOT_DEFINED, dtype=np.int8)
CUBE_CTYPE_TYPE = np.full(CUBE_CTYPE_COUNT, NOT_DEFINED, dtype=np.int8)

cube_ctype_list = list()

for cube_color_index in CUBE_COLOR_CODOMAIN:
    cube_color_fun = CUBE_COLOR_FUN[cube_color_index]

    for (cube_type_index, cube_type_key) in enumerate(CUBE_TYPE_KEY):

            cube_ctype_index = len(cube_ctype_list)

            cube_ctype_id = cube_color_fun(cube_type_key)
            cube_ctype_list.append(cube_ctype_id)

            CUBE_CTYPE_COLOR[cube_ctype_index] = cube_color_index
            CUBE_CTYPE_TYPE[cube_ctype_index] = cube_type_index

CUBE_CTYPE_DOMAIN = np.array(cube_ctype_list)

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

CUBE_COLOR = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)
CUBE_TYPE = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)

cube_id_list = list()

for cube_color_index in CUBE_COLOR_CODOMAIN:
    cube_color_fun = CUBE_COLOR_FUN[cube_color_index]

    for (cube_type_index, cube_type_key) in enumerate(CUBE_TYPE_KEY):

        for cube_type_occurrence in range(CUBE_TYPE_MULTIPLICITY[cube_type_index]):
            cube_index = len(cube_id_list)

            cube_id = "%s%d" % (cube_color_fun(cube_type_key), cube_type_occurrence)
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


# Define cube elevation domain

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

HEX_STATUS_HAS_CUBE = np.argwhere(HEX_STATUS_DOMAIN == "HAS_CUBE")[0][0]
HEX_STATUS_IS_EMPTY = np.argwhere(HEX_STATUS_DOMAIN == "IS_EMPTY")[0][0]
HEX_STATUS_HAS_STACK = np.argwhere(HEX_STATUS_DOMAIN == "HAS_STACK")[0][0]

print(f"{HEX_STATUS_HAS_CUBE=!s}")
print(f"{HEX_STATUS_IS_EMPTY=!s}")
print(f"{HEX_STATUS_HAS_STACK=!s}")


# Define hex identifiers

hex_id_dict = dict()
hex_uv_dict = dict()

hex_id_list = list()
hex_u_list = list()
hex_v_list = list()


def hex_add(key, u, v):

    assert len(key) == 2
    assert key not in hex_id_dict
    assert (u,v) not in hex_uv_dict

    hex_index = len(hex_id_list)

    hex_id_dict[key] = hex_index
    hex_uv_dict[(u,v)] = hex_index

    hex_id_list.append(key)
    hex_u_list.append(u)
    hex_v_list.append(v)


# Row "a"
hex_add(key='a1', u=-1, v=-4)
hex_add(key='a2', u=-0, v=-4)
hex_add(key='a3', u=1, v=-4)
hex_add(key='a4', u=2, v=-4)
hex_add(key='a5', u=3, v=-4)
hex_add(key='a6', u=4, v=-4)
hex_add(key='a7', u=5, v=-4)

# Row "b"
hex_add(key='b1', u=-2, v=-3)
hex_add(key='b2', u=-1, v=-3)
hex_add(key='b3', u=0, v=-3)
hex_add(key='b4', u=1, v=-3)
hex_add(key='b5', u=2, v=-3)
hex_add(key='b6', u=3, v=-3)
hex_add(key='b7', u=4, v=-3)
hex_add(key='b8', u=5, v=-3)

# Row "c"
hex_add(key='c1', u=-2, v=-2)
hex_add(key='c2', u=-1, v=-2)
hex_add(key='c3', u=0, v=-2)
hex_add(key='c4', u=1, v=-2)
hex_add(key='c5', u=2, v=-2)
hex_add(key='c6', u=3, v=-2)
hex_add(key='c7', u=4, v=-2)

# Row "d"
hex_add(key='d1', u=-3, v=-1)
hex_add(key='d2', u=-2, v=-1)
hex_add(key='d3', u=-1, v=-1)
hex_add(key='d4', u=0, v=-1)
hex_add(key='d5', u=1, v=-1)
hex_add(key='d6', u=2, v=-1)
hex_add(key='d7', u=3, v=-1)
hex_add(key='d8', u=4, v=-1)

# Row "e"
hex_add(key='e1', u=-4, v=0)
hex_add(key='e2', u=-3, v=0)
hex_add(key='e3', u=-2, v=0)
hex_add(key='e4', u=-1, v=0)
hex_add(key='e5', u=0, v=0)
hex_add(key='e6', u=1, v=0)
hex_add(key='e7', u=2, v=0)
hex_add(key='e8', u=3, v=0)
hex_add(key='e9', u=4, v=0)

# Row "f"
hex_add(key='f1', u=-4, v=1)
hex_add(key='f2', u=-3, v=1)
hex_add(key='f3', u=-2, v=1)
hex_add(key='f4', u=-1, v=1)
hex_add(key='f5', u=0, v=1)
hex_add(key='f6', u=1, v=1)
hex_add(key='f7', u=2, v=1)
hex_add(key='f8', u=3, v=1)

# Row "g"
hex_add(key='g1', u=-4, v=2)
hex_add(key='g2', u=-3, v=2)
hex_add(key='g3', u=-2, v=2)
hex_add(key='g4', u=-1, v=2)
hex_add(key='g5', u=0, v=2)
hex_add(key='g6', u=1, v=2)
hex_add(key='g7', u=2, v=2)

# Row "h"
hex_add(key='h1', u=-5, v=3)
hex_add(key='h2', u=-4, v=3)
hex_add(key='h3', u=-3, v=3)
hex_add(key='h4', u=-2, v=3)
hex_add(key='h5', u=-1, v=3)
hex_add(key='h6', u=0, v=3)
hex_add(key='h7', u=1, v=3)
hex_add(key='h8', u=2, v=3)

# Row "i"
hex_add(key='i1', u=-5, v=4)
hex_add(key='i2', u=-4, v=4)
hex_add(key='i3', u=-3, v=4)
hex_add(key='i4', u=-2, v=4)
hex_add(key='i5', u=-1, v=4)
hex_add(key='i6', u=0, v=4)
hex_add(key='i7', u=1, v=4)


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

HEX_NEXT_FST = np.full((HEX_ID_COUNT, HEX_DIRECTION_COUNT), NOT_DEFINED, dtype=np.int8)
HEX_NEXT_SND = np.full((HEX_ID_COUNT, HEX_DIRECTION_COUNT), NOT_DEFINED, dtype=np.int8)

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

cube_status = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)
cube_hex = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)
cube_hex_level = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)
print()
print(f"{cube_status=!s}")
print(f"{cube_hex=!s}")
print(f"{cube_hex_level=!s}")


# Define hex variables properties

hex_status = np.full(HEX_ID_COUNT, NOT_DEFINED, dtype=np.int8)
hex_bottom = np.full(HEX_ID_COUNT, NOT_DEFINED, dtype=np.int8)
hex_top = np.full(HEX_ID_COUNT, NOT_DEFINED, dtype=np.int8)
print()
print(f"{hex_status=!s}")
print(f"{hex_bottom=!s}")
print(f"{hex_top=!s}")


# Initial state for cubes and hexagons

def set_cube_in_reserve(cube_color_index, cube_type_index):

    cube_indexes = CUBE_ID_CODOMAIN[(CUBE_COLOR == cube_color_index) &
                               (CUBE_TYPE == cube_type_index) &
                               (cube_status == NOT_DEFINED)]

    assert cube_indexes.size != 0
    cube_index = cube_indexes[0]
    cube_status[cube_index] = CUBE_STATUS_RESERVED


def set_cube_at_position(hex_index, cube_color_index, cube_type_index):

    cube_indexes = CUBE_ID_CODOMAIN[(CUBE_COLOR == cube_color_index) &
                               (CUBE_TYPE == cube_type_index) &
                               (cube_status == NOT_DEFINED)]

    assert cube_indexes.size != 0
    cube_index = cube_indexes[0]
    cube_status[cube_index] = CUBE_STATUS_ACTIVE

    if hex_status[hex_index] == HEX_STATUS_IS_EMPTY:

        hex_bottom[hex_index] = cube_index
        hex_status[hex_index] = HEX_STATUS_HAS_CUBE

        cube_hex[cube_index] = hex_index
        cube_hex_level[cube_index] = HEX_LEVEL_BOTTOM

    elif hex_status[hex_index] == HEX_STATUS_HAS_CUBE:

        hex_top[hex_index] = cube_index
        hex_status[hex_index] = HEX_STATUS_HAS_STACK

        cube_hex[cube_index] = hex_index
        cube_hex_level[cube_index] = HEX_LEVEL_TOP

    else:
        assert hex_status[hex_index] != HEX_STATUS_HAS_STACK


def set_cube_in_reserve_by_key(cube_key):

    cube_ctype_index = np.argwhere(CUBE_CTYPE_DOMAIN == cube_key)[0][0]
    cube_color_index = CUBE_CTYPE_COLOR[cube_ctype_index]
    cube_type_index = CUBE_CTYPE_TYPE[cube_ctype_index]

    set_cube_in_reserve(cube_color_index, cube_type_index)


def set_cube_at_position_by_keys(hex_key, cube_key):

    hex_index = np.argwhere(HEX_ID_DOMAIN == hex_key)[0][0]

    cube_ctype_index = np.argwhere(CUBE_CTYPE_DOMAIN == cube_key)[0][0]
    cube_color_index = CUBE_CTYPE_COLOR[cube_ctype_index]
    cube_type_index = CUBE_CTYPE_TYPE[cube_ctype_index]

    set_cube_at_position(hex_index, cube_color_index, cube_type_index)


# whites
set_cube_at_position_by_keys('b1', 'F')
set_cube_at_position_by_keys('b8', 'F')
set_cube_at_position_by_keys('a4', 'K')

set_cube_at_position_by_keys('b2', 'R')
set_cube_at_position_by_keys('b3', 'P')
set_cube_at_position_by_keys('b4', 'S')
set_cube_at_position_by_keys('b5', 'R')
set_cube_at_position_by_keys('b6', 'P')
set_cube_at_position_by_keys('b7', 'S')

set_cube_at_position_by_keys('a3', 'R')
set_cube_at_position_by_keys('a2', 'S')
set_cube_at_position_by_keys('a1', 'P')
set_cube_at_position_by_keys('a5', 'S')
set_cube_at_position_by_keys('a6', 'R')
set_cube_at_position_by_keys('a7', 'P')

# blacks
set_cube_at_position_by_keys('h1', 'f')
set_cube_at_position_by_keys('h8', 'f')
set_cube_at_position_by_keys('i4', 'k')

set_cube_at_position_by_keys('h7', 'r')
set_cube_at_position_by_keys('h6', 'p')
set_cube_at_position_by_keys('h5', 's')
set_cube_at_position_by_keys('h4', 'r')
set_cube_at_position_by_keys('h3', 'p')
set_cube_at_position_by_keys('h2', 's')

set_cube_at_position_by_keys('i5', 'r')
set_cube_at_position_by_keys('i6', 's')
set_cube_at_position_by_keys('i7', 'p')
set_cube_at_position_by_keys('i3', 's')
set_cube_at_position_by_keys('i2', 'r')
set_cube_at_position_by_keys('i1', 'p')

# white reserve
set_cube_in_reserve_by_key('W')
set_cube_in_reserve_by_key('W')

set_cube_in_reserve_by_key('M')
set_cube_in_reserve_by_key('M')

set_cube_in_reserve_by_key('M')
set_cube_in_reserve_by_key('M')

# black reserve
set_cube_in_reserve_by_key('m')
set_cube_in_reserve_by_key('m')

set_cube_in_reserve_by_key('m')
set_cube_in_reserve_by_key('m')

set_cube_in_reserve_by_key('w')
set_cube_in_reserve_by_key('w')


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