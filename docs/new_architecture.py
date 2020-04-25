#!/usr/bin/en python3

"""New faster architecture for playing the abstract game JERSI with an AI."""

# -*- coding: utf-8 -*-

import numpy as np

NOT_AN_INDEX = -1 

NAME_OF_COLOR = np.array(["black", "white"])
NAME_OF_COLOR.sort()
COLOR_COUNT = NAME_OF_COLOR.size
COLORS = np.arange(COLOR_COUNT)

NAME_OF_TYPE = np.array(["bevri", "cmana", "cukla", "darsi", "kuctai", "kunti", "kurfa"])
NAME_OF_TYPE.sort()
TYPE_COUNT = NAME_OF_TYPE.size
TYPES = np.arange(TYPE_COUNT)

BEVRI = np.argwhere(NAME_OF_TYPE == "bevri")[0][0]
CMANA = np.argwhere(NAME_OF_TYPE == "cmana")[0][0]
CUKLA = np.argwhere(NAME_OF_TYPE == "cukla")[0][0]
DARSI = np.argwhere(NAME_OF_TYPE == "darsi")[0][0]
KUCTAI = np.argwhere(NAME_OF_TYPE == "kuctai")[0][0]
KUNTI = np.argwhere(NAME_OF_TYPE == "kunti")[0][0]
KURFA = np.argwhere(NAME_OF_TYPE == "kurfa")[0][0]

KEY_OF_TYPE = np.full(TYPE_COUNT, "??")
KEY_OF_TYPE[BEVRI] = "BV"
KEY_OF_TYPE[CMANA] = "CM"
KEY_OF_TYPE[CUKLA] = "CK"
KEY_OF_TYPE[DARSI] = "DR"
KEY_OF_TYPE[KUCTAI] = "KC"
KEY_OF_TYPE[KUNTI] = "KN"
KEY_OF_TYPE[KURFA] = "KR"

OCC_OF_TYPE = np.zeros(TYPE_COUNT, dtype=int)
OCC_OF_TYPE[BEVRI] = 2
OCC_OF_TYPE[CMANA] = 4
OCC_OF_TYPE[CUKLA] = 4
OCC_OF_TYPE[DARSI] = 2
OCC_OF_TYPE[KUCTAI] = 4
OCC_OF_TYPE[KUNTI] = 1
OCC_OF_TYPE[KURFA] = 4

assert OCC_OF_TYPE[KUNTI] == 1
MAX_OCC_OF_TYPE = np.max(OCC_OF_TYPE)
SUM_OCC_OF_TYPE = np.sum(OCC_OF_TYPE)

BEATS = np.full((TYPE_COUNT, TYPE_COUNT), False, dtype=bool)

BEATS[CUKLA, KUCTAI] = True
BEATS[KUCTAI, KURFA] = True
BEATS[KURFA, CUKLA] = True

BEATS[CUKLA, DARSI] = True
BEATS[KUCTAI, DARSI] = True
BEATS[KURFA, DARSI] = True

BEATS[DARSI, CUKLA] = True
BEATS[DARSI, KUCTAI] = True
BEATS[DARSI, KURFA] = True
BEATS[DARSI, DARSI] = True

BEATS[CUKLA, BEVRI] = True
BEATS[DARSI, BEVRI] = True
BEATS[KUCTAI, BEVRI] = True
BEATS[KURFA, BEVRI] = True

BEATS[CUKLA, KUNTI] = True
BEATS[DARSI, KUNTI] = True
BEATS[KUCTAI, KUNTI] = True
BEATS[KURFA, KUNTI] = True

PIECE_COUNT_PER_COLOR = SUM_OCC_OF_TYPE
PIECE_COUNT = PIECE_COUNT_PER_COLOR*COLOR_COUNT
PIECES = np.arange(PIECE_COUNT)

COLOR_OF_PIECE = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
TYPE_OF_PIECE = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)

PIECE_FROM_COLOR_TYPE_OCC = np.full((COLOR_COUNT, TYPE_COUNT, MAX_OCC_OF_TYPE), NOT_AN_INDEX, dtype=int)
KUNTI_FROM_COLOR = np.full(COLOR_COUNT, NOT_AN_INDEX, dtype=int)

piece_index = None
for color_index in COLORS:
    for type_index in TYPES:
        for occ_index in range(OCC_OF_TYPE[type_index]):
            if piece_index is None:
                piece_index = 0
            else:
                piece_index += 1
            PIECE_FROM_COLOR_TYPE_OCC[color_index, type_index, occ_index] = piece_index           
            COLOR_OF_PIECE[piece_index] = color_index
            TYPE_OF_PIECE[piece_index] = type_index
            if type_index == KUNTI:
                KUNTI_FROM_COLOR[color_index] = piece_index

#>> The design of the location data must satisfiy the following requirements:
#>> - Any allowed move can be implemented as a series of moves between 
#>>   two locations.
#>> - The state of game can be implemented as a single numy array in order
#>>   to copy such state with high performance.                

FIELD_CELL_COUNT = 69
STACK_SIZE_MAX = 2

RESERVE_CELL_COUNT_PER_COLOR = OCC_OF_TYPE[BEVRI] + OCC_OF_TYPE[CMANA]
RESERVE_CELL_COUNT = RESERVE_CELL_COUNT_PER_COLOR*COLOR_COUNT

JAIL_CELL_COUNT_PER_COLOR = PIECE_COUNT_PER_COLOR
JAIL_CELL_COUNT = JAIL_CELL_COUNT_PER_COLOR*COLOR_COUNT

LOCATION_COUNT = 0
LOCATION_COUNT += FIELD_CELL_COUNT*STACK_SIZE_MAX
LOCATION_COUNT += RESERVE_CELL_COUNT
LOCATION_COUNT += JAIL_CELL_COUNT

LOCATIONS = np.arange(LOCATION_COUNT)

piece_from_location = np.full(LOCATION_COUNT, NOT_AN_INDEX, dtype=int)
location_from_piece = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)

PIECE_RESERVE_LOCATIONS = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
PIECE_JAIL_LOCATIONS = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)



def test_locations_and_pieces_recovery():
    """This function shows, using a small example, that if one wants
    to minimize the number of arrays, then it is better to keep
    the array "location_from_piece" than the array "piece_from_location".
    """
    
    print()
    print("-- test_locations_and_pieces_recovery -- BEGIN")

    LOCATION_COUNT = 10
    PIECE_COUNT = 3
    PIECES = np.arange(PIECE_COUNT)
    LOCATIONS = np.arange(LOCATION_COUNT)
    
    print()
    print("-- Define location_from_piece and deduce piece_from_location")

    location_from_piece = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
    location_from_piece[0] = 7
    location_from_piece[1] = 2
    location_from_piece[2] = 5
    print("location_from_piece:", location_from_piece)

    piece_from_location = np.full(LOCATION_COUNT, NOT_AN_INDEX, dtype=int)
    piece_from_location[location_from_piece] = PIECES
    print("piece_from_location:", piece_from_location)

    print()
    print("-- Use piece_from_location and deduce location_from_piece")
    
    location_from_piece = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
    print("location_from_piece (after reset):", location_from_piece)
    print("piece_from_location:", piece_from_location)
    
    selector = (piece_from_location != NOT_AN_INDEX)
    print()
    print("selector:", selector)
    
    location_from_selector = LOCATIONS[selector]
    print("location_from_selector:", location_from_selector)

    piece_from_selector = piece_from_location[selector]
    print("piece_from_selector:", piece_from_selector)

    location_from_piece[piece_from_selector] = location_from_selector
    print()
    print("location_from_piece:", location_from_piece)
    
    print()
    print("-- test_locations_and_pieces_recovery -- END")


def main():
    """Start JERSI."""
    print("NAME_OF_COLOR:", NAME_OF_COLOR)
    print("COLOR_COUNT:", COLOR_COUNT)
    print("COLORS:", COLORS)
    print()
    print("NAME_OF_TYPE:", NAME_OF_TYPE)
    print("KEY_OF_TYPE:", KEY_OF_TYPE)
    print("TYPE_COUNT:", TYPE_COUNT)
    print("TYPES:", TYPES)
    print()
    print("BEATS:", BEATS)
    for type_i in TYPES:
        for type_j in TYPES:
            if BEATS[type_i, type_j]:
                print("%s > %s" % (NAME_OF_TYPE[type_i], NAME_OF_TYPE[type_j]))

    print()
    print("OCC_OF_TYPE:", OCC_OF_TYPE)
    print("PIECE_COUNT:", PIECE_COUNT)
    print()
    print("COLOR_OF_PIECE:", COLOR_OF_PIECE)
    print()
    print("TYPE_OF_PIECE:", TYPE_OF_PIECE)
    print()
    print("MAX_OCC_OF_TYPE:", MAX_OCC_OF_TYPE)
    print("SUM_OCC_OF_TYPE:", SUM_OCC_OF_TYPE)
    print("PIECE_COUNT:", PIECE_COUNT)
    print()
    print("PIECE_FROM_COLOR_TYPE_OCC:", PIECE_FROM_COLOR_TYPE_OCC)
    print()
    print("COLOR_OF_PIECE:", COLOR_OF_PIECE)
    print()
    print("TYPE_OF_PIECE:", TYPE_OF_PIECE)
    print()
    print("KUNTI_FROM_COLOR:", KUNTI_FROM_COLOR)
    print()
    print("LOCATION_COUNT:", LOCATION_COUNT)
    print()
    print("PIECE_COUNT:", PIECE_COUNT)
    print()
    
    
    test_locations_and_pieces_recovery()


if __name__ == "__main__":
    main()
