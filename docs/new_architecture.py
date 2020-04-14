#!/usr/bin/en python3

"""New faster architecture for playing the jersi abstract game with an AI."""

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
PIECE_COUNT = COLOR_COUNT*OCC_SUM

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

LOCATION_COUNT = 100
piece_at_location = np.full(LOCATION_COUNT, NOT_AN_INDEX, dtype=int)






PIECE_INITIAL_LOCATIONS = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)

PIECE_RESERVE_LOCATIONS = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)

PIECE_JAIL_LOCATIONS = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)

piece_locations = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)



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


if __name__ == "__main__":
    main()
