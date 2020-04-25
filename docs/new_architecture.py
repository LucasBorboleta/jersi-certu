#!/usr/bin/en python3

"""New faster architecture for playing the abstract game JERSI with an AI."""

# -*- coding: utf-8 -*-

import numpy as np

NOT_AN_INDEX = -1 

COLOR_NAMES = np.array(["black", "white"])
COLOR_NAMES.sort()
COLOR_COUNT = COLOR_NAMES.size
COLORS = np.arange(COLOR_COUNT)

TYPE_NAMES = np.array(["bevri", "cmana", "cukla", "darsi", "kuctai", "kunti", "kurfa"])
TYPE_NAMES.sort()
TYPE_COUNT = TYPE_NAMES.size
TYPES = np.arange(TYPE_COUNT)

BEVRI = np.argwhere(TYPE_NAMES == "bevri")[0][0]
CMANA = np.argwhere(TYPE_NAMES == "cmana")[0][0]
CUKLA = np.argwhere(TYPE_NAMES == "cukla")[0][0]
DARSI = np.argwhere(TYPE_NAMES == "darsi")[0][0]
KUCTAI = np.argwhere(TYPE_NAMES == "kuctai")[0][0]
KUNTI = np.argwhere(TYPE_NAMES == "kunti")[0][0]
KURFA = np.argwhere(TYPE_NAMES == "kurfa")[0][0]

TYPE_KEYS = np.full(TYPE_COUNT, "??")
TYPE_KEYS[BEVRI] = "BV"
TYPE_KEYS[CMANA] = "CM"
TYPE_KEYS[CUKLA] = "CK"
TYPE_KEYS[DARSI] = "DR"
TYPE_KEYS[KUCTAI] = "KC"
TYPE_KEYS[KUNTI] = "KN"
TYPE_KEYS[KURFA] = "KR"

OCCS = np.zeros(TYPE_COUNT, dtype=int)
OCCS[BEVRI] = 2
OCCS[CMANA] = 4
OCCS[CUKLA] = 4
OCCS[DARSI] = 2
OCCS[KUCTAI] = 4
OCCS[KUNTI] = 1
OCCS[KURFA] = 4

assert OCCS[KUNTI] == 1
OCC_MAX = np.max(OCCS)
OCC_SUM = np.sum(OCCS)

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

PIECE_COUNT_PER_COLOR = OCC_SUM
PIECE_COUNT = PIECE_COUNT_PER_COLOR*COLOR_COUNT
PIECE_COLORS = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
PIECE_TYPES = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)

PIECE_BY_COLOR_TYPE_OCC = np.full((COLOR_COUNT, TYPE_COUNT, OCC_MAX), NOT_AN_INDEX, dtype=int)

KUNTI_PER_COLOR = np.full(COLOR_COUNT, NOT_AN_INDEX, dtype=int)

piece_index = None
for color_index in COLORS:
    for type_index in TYPES:
        for occ_index in range(OCCS[type_index]):
            if piece_index is None:
                piece_index = 0
            else:
                piece_index += 1
            PIECE_BY_COLOR_TYPE_OCC[color_index, type_index, occ_index] = piece_index
            PIECE_COLORS[piece_index] = color_index
            PIECE_TYPES[piece_index] = type_index
            if type_index == KUNTI:
                KUNTI_PER_COLOR[color_index] = piece_index

#>> The design of the location data must satisfiy the following requirements:
#>> - Any allowed move can be implemented as a series of moves between 
#>>   two locations.
#>> - The state of game can be implemented as a single numy array in order
#>>   to copy such state with high performance.                

FIELD_CELL_COUNT = 69
STACK_SIZE_MAX = 2

RESERVE_CELL_COUNT_PER_COLOR = OCCS[BEVRI] + OCCS[CMANA]
RESERVE_CELL_COUNT = RESERVE_CELL_COUNT_PER_COLOR*COLOR_COUNT

JAIL_CELL_COUNT_PER_COLOR = PIECE_COUNT_PER_COLOR
JAIL_CELL_COUNT = JAIL_CELL_COUNT_PER_COLOR*COLOR_COUNT

LOCATION_COUNT = 0
LOCATION_COUNT += FIELD_CELL_COUNT*STACK_SIZE_MAX
LOCATION_COUNT += RESERVE_CELL_COUNT
LOCATION_COUNT += JAIL_CELL_COUNT

location_hosts = np.full(LOCATION_COUNT, NOT_AN_INDEX, dtype=int)
PIECE_INITIAL_LOCATIONS = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
PIECE_RESERVE_LOCATIONS = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
PIECE_JAIL_LOCATIONS = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
piece_locations = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)

#-- Construct location_hosts from piece_locations
location_hosts = np.full(LOCATION_COUNT, NOT_AN_INDEX, dtype=int)
location_hosts[piece_locations] = np.arange(PIECE_COUNT)

LOCATION_COUNT = 10
PIECE_COUNT = 3
piece_locations = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
piece_locations[0] = 7
piece_locations[1] = 2
piece_locations[2] = 5
location_hosts = np.full(LOCATION_COUNT, NOT_AN_INDEX, dtype=int)
location_hosts[piece_locations] = np.arange(PIECE_COUNT)

#-- Back to piece_locations
back_piece_locations = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
query_locations = np.arange(LOCATION_COUNT)[location_hosts != NOT_AN_INDEX]
query_pieces = location_hosts[location_hosts != NOT_AN_INDEX]
back_piece_locations[query_pieces] = query_locations


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
    print("COLOR_NAMES:", COLOR_NAMES)
    print("COLOR_COUNT:", COLOR_COUNT)
    print("COLORS:", COLORS)
    print()
    print("TYPE_NAMES:", TYPE_NAMES)
    print("TYPE_KEYS:", TYPE_KEYS)
    print("TYPE_COUNT:", TYPE_COUNT)
    print("TYPES:", TYPES)
    print()
    print("BEATS:", BEATS)
    for type_i in TYPES:
        for type_j in TYPES:
            if BEATS[type_i, type_j]:
                print("%s > %s" % (TYPE_NAMES[type_i], TYPE_NAMES[type_j]))

    print()
    print("OCCS:", OCCS)
    print("PIECE_COUNT:", PIECE_COUNT)
    print()
    print("PIECE_COLORS:", PIECE_COLORS)
    print()
    print("PIECE_TYPES:", PIECE_TYPES)
    print()
    print("OCC_MAX:", OCC_MAX)
    print("OCC_SUM:", OCC_SUM)
    print("PIECE_COUNT:", PIECE_COUNT)
    print()
    print("PIECE_BY_COLOR_TYPE_OCC:", PIECE_BY_COLOR_TYPE_OCC)
    print()
    print("PIECE_COLORS:", PIECE_COLORS)
    print()
    print("PIECE_TYPES:", PIECE_TYPES)
    print()
    print("KUNTI_PER_COLOR:", KUNTI_PER_COLOR)
    print()
    print("LOCATION_COUNT:", LOCATION_COUNT)
    print()
    print("PIECE_COUNT:", PIECE_COUNT)
    print()
    
    
    test_locations_and_pieces_recovery()


if __name__ == "__main__":
    main()
