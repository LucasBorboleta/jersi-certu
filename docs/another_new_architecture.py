# -*- coding: utf-8 -*-
"""
Data structure for "jersi" game : simple, fast and universal.

Universal means: can be translated to javascript
Fast means: relies mostly on array containers
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
CUBE_TYPE_KEY = np.vectorize(lambda x:x[0])(CUBE_TYPE_DOMAIN)

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

# Define cube elevation domain

CUBE_ELEVATION_DOMAIN = np.array(["BOTTOM", "TOP"])
CUBE_ELEVATION_COUNT = CUBE_ELEVATION_DOMAIN.size
CUBE_ELEVATION_CODOMAIN = np.arange(CUBE_ELEVATION_COUNT, dtype=np.int8)

assert np.unique(CUBE_ELEVATION_DOMAIN).size == CUBE_ELEVATION_COUNT

print()
print(f"{CUBE_ELEVATION_DOMAIN=!s}")
print(f"{CUBE_ELEVATION_CODOMAIN=!s}")

CUBE_ELEVATION_BOTTOM = np.argwhere(CUBE_ELEVATION_DOMAIN == "BOTTOM")[0][0]
CUBE_ELEVATION_TOP = np.argwhere(CUBE_ELEVATION_DOMAIN == "TOP")[0][0]

print(f"{CUBE_ELEVATION_BOTTOM=!s}")
print(f"{CUBE_ELEVATION_TOP=!s}")

# Define cube identifiers and assign colors and types

CUBE_ID_COUNT = CUBE_COLOR_COUNT*CUBE_TYPE_MULTIPLICITY_SUM
CUBE_ID_CODOMAIN = np.arange(CUBE_ID_COUNT, dtype=np.int8)

CUBE_COLOR = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)
CUBE_TYPE = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)

cube_id_list = list()
cube_index = 0

for cube_color_index in CUBE_COLOR_CODOMAIN:
    cube_color_fun = CUBE_COLOR_FUN[cube_color_index]

    for (cube_type_index, cube_type_key) in enumerate(CUBE_TYPE_KEY):

        for cube_type_occurrence in range(CUBE_TYPE_MULTIPLICITY[cube_type_index]):
            cube_id = "%s%d" % (cube_color_fun(cube_type_key), cube_type_occurrence)
            cube_id_list.append(cube_id)

            CUBE_COLOR[cube_index] = cube_color_index
            CUBE_TYPE[cube_index] = cube_type_index
            cube_index += 1

CUBE_ID_DOMAIN = np.array(cube_id_list)
assert CUBE_ID_DOMAIN.size == CUBE_ID_COUNT
assert np.unique(CUBE_ID_DOMAIN).size == CUBE_ID_COUNT

print()
print(f"{CUBE_ID_COUNT=!s}")
print(f"{CUBE_ID_DOMAIN=!s}")
print(f"{CUBE_ID_CODOMAIN=!s}")
print(f"{CUBE_COLOR=!s}")
print(f"{CUBE_TYPE=!s}")

# Define cell direction domain

CELL_DIRECTION_DOMAIN = np.array(["12h", "02h", "04h", "06h", "08h", "10h"])
CUBE_DIRECTION_COUNT = CELL_DIRECTION_DOMAIN.size
CELL_DIRECTION_CODOMAIN = np.arange(CUBE_DIRECTION_COUNT, dtype=np.int8)

assert np.unique(CELL_DIRECTION_DOMAIN).size == CUBE_DIRECTION_COUNT

print()
print(f"{CELL_DIRECTION_DOMAIN=!s}")
print(f"{CELL_DIRECTION_CODOMAIN=!s}")
print(f"{CUBE_DIRECTION_COUNT=!s}")

# Define cell status domain

CELL_STATUS_DOMAIN = np.array(["HAS_CUBE", "IS_EMPTY", "HAS_STACK"])
CUBE_STATUS_COUNT = CELL_STATUS_DOMAIN.size
CELL_STATUS_CODOMAIN = np.arange(CUBE_STATUS_COUNT, dtype=np.int8)

print()
print(f"{CELL_STATUS_DOMAIN=!s}")
print(f"{CELL_STATUS_CODOMAIN=!s}")

assert np.unique(CELL_STATUS_DOMAIN).size == CUBE_STATUS_COUNT

CELL_STATUS_HAS_CUBE = np.argwhere(CELL_STATUS_DOMAIN == "HAS_CUBE")[0][0]
CELL_STATUS_IS_EMPTY = np.argwhere(CELL_STATUS_DOMAIN == "IS_EMPTY")[0][0]
CELL_STATUS_HAS_STACK = np.argwhere(CELL_STATUS_DOMAIN == "HAS_STACK")[0][0]

print(f"{CELL_STATUS_HAS_CUBE=!s}")
print(f"{CELL_STATUS_IS_EMPTY=!s}")
print(f"{CELL_STATUS_HAS_STACK=!s}")


# Define cell identifiers

CELL_ID_COUNT = 69
CELL_ID_CODOMAIN = np.arange(CELL_ID_COUNT, dtype=np.int8)

# Define cells by one or two steps toward a given direction

CELL_NEXT_FST = np.full((CELL_ID_COUNT, CUBE_DIRECTION_COUNT), NOT_DEFINED, dtype=np.int8)
CELL_NEXT_SND = np.full((CELL_ID_COUNT, CUBE_DIRECTION_COUNT), NOT_DEFINED, dtype=np.int8)
print()
print(f"{CELL_NEXT_FST=!s}")
print(f"{CELL_NEXT_SND=!s}")


# Define cube variables properties

cube_status = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)
cube_cell = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)
cube_elevation = np.full(CUBE_ID_COUNT, NOT_DEFINED, dtype=np.int8)
print()
print(f"{cube_status=!s}")
print(f"{cube_cell=!s}")
print(f"{cube_elevation=!s}")


# Define cell variables properties

cell_status = np.full(CELL_ID_COUNT, NOT_DEFINED, dtype=np.int8)
cell_bottom = np.full(CELL_ID_COUNT, NOT_DEFINED, dtype=np.int8)
cell_top = np.full(CELL_ID_COUNT, NOT_DEFINED, dtype=np.int8)
print()
print(f"{cell_status=!s}")
print(f"{cell_bottom=!s}")
print(f"{cell_top=!s}")


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