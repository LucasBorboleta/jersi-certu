#!/usr/bin/en python3
# -*- coding: utf-8 -*-

"""New faster architecture for playing the abstract game JERSI with an AI."""

EXAMPLE_OF_LAYOUT = """

        #   #   #   #   #   #   # 
i1      #   #   #   #   #   #   #       i7
      #   #   #   #   #   #   #   # 
h1    #   #   #   #   #   #   #   #     h8
        #   #   #   #   #   #   # 
g1      #   #   #   #   #   #   #       g7
      #   #   #   #   #   #   #   # 
f1    #   #   #   #   #   #   #   #     f8
    #   #   #   #   #   #   #   #   # 
e1  #   #   #   #   #   #   #   #   #   e9
      #   #   #   #   #   #   #   # 
d1    #   #   #   #   #   #   #   #     d8
        #   #   #   #   #   #   # 
c1      #   #   #   #   #   #   #       c7
      #   #   #   #   #   #   #   # 
b1    #   #   #   #   #   #   #   #     b8
        #   #   #   #   #   #   # 
a1      #   #   #   #   #   #   #       a7


"""

EXAMPLE_OF_LAYOUT = """
           _________________________________________
          |     |     |     |     |     |     |     | 
i1        |  p  |  r  |  s  |  k  | r   |  s  |  p  |        i7
        __|_____|_____|_____|_____|_____|_____|_____|__
       |     |     |     |     |     |     |     |     | 
h1     |  f  |  s  |  p  |  r  |  s  |  p  |  r  |  f  |     h8
       |_____|_____|_____|_____|_____|_____|_____|_____|
          |     |     |     |     |     |     |     |
g1        |     |     |     |     |     |     |     |        g7
        __|_____|_____|_____|_____|_____|_____|_____|__
       |     |     |     |     |     |     |     |     | 
f1     |     |     |     |     |     |     |     |     |     f8
     __|_____|_____|_____|_____|_____|_____|_____|_____|__
    |     |     |     |     |     |     |     |     |     |
e1  |     |     |     |     |     |     |     |     |     |  e9
    |_____|_____|_____|_____|_____|_____|_____|_____|_____|
       |     |     |     |     |     |     |     |     | 
d1     |     |     |     |     |     |     |     |     |     d8
       |_____|_____|_____|_____|_____|_____|_____|_____|
          |     |  K  |     |     |     |     |     |
c1        |     |  P  |     |     |     |     |     |        c7
        __|_____|_____|_____|_____|_____|_____|_____|__
       |     |     |     |     |     |     |     |     | 
b1     |  F  |  R  |  P  |  S  |  R  |  P  |  S  |  F  |     b8
       |_____|_____|_____|_____|_____|_____|_____|_____|
          |     |     |     |     |     |     |     |
a1        |  P  |  S  |  R  |  K  |  S  |  R  |  P  |        a7
          |_____|_____|_____|_____|_____|_____|_____|




"""



import numpy as np

NOT_AN_INDEX = -1 

NAME_OF_COLOR = np.array(["black", "white"])
NAME_OF_COLOR.sort()
COLOR_COUNT = NAME_OF_COLOR.size
COLORS = np.arange(COLOR_COUNT)

NAME_OF_TYPE = np.array(["foul", "king", "mountain", "paper", "rock", "scissors", "wise"])
NAME_OF_TYPE.sort()
TYPE_COUNT = NAME_OF_TYPE.size
TYPES = np.arange(TYPE_COUNT)

FOUL = np.argwhere(NAME_OF_TYPE == "foul")[0][0]
KING = np.argwhere(NAME_OF_TYPE == "king")[0][0]
MOUNTAIN = np.argwhere(NAME_OF_TYPE == "mountain")[0][0]
PAPER = np.argwhere(NAME_OF_TYPE == "paper")[0][0]
ROCK = np.argwhere(NAME_OF_TYPE == "rock")[0][0]
SCISSORS = np.argwhere(NAME_OF_TYPE == "scissors")[0][0]
WISE = np.argwhere(NAME_OF_TYPE == "wise")[0][0]

KEY_OF_TYPE = np.full(TYPE_COUNT, "?")
KEY_OF_TYPE[FOUL] = "F"
KEY_OF_TYPE[KING] = "K"
KEY_OF_TYPE[MOUNTAIN] = "M"
KEY_OF_TYPE[PAPER] = "P"
KEY_OF_TYPE[ROCK] = "R"
KEY_OF_TYPE[SCISSORS] = "S"
KEY_OF_TYPE[WISE] = "W"

OCC_OF_TYPE = np.zeros(TYPE_COUNT, dtype=int)
OCC_OF_TYPE[FOUL] = 2
OCC_OF_TYPE[KING] = 1
OCC_OF_TYPE[MOUNTAIN] = 4
OCC_OF_TYPE[PAPER] = 4
OCC_OF_TYPE[ROCK] = 4
OCC_OF_TYPE[SCISSORS] = 4
OCC_OF_TYPE[WISE] = 2

assert OCC_OF_TYPE[KING] == 1
MAX_OCC_OF_TYPE = np.max(OCC_OF_TYPE)
SUM_OCC_OF_TYPE = np.sum(OCC_OF_TYPE)

BEATS = np.full((TYPE_COUNT, TYPE_COUNT), False, dtype=bool)

BEATS[ROCK, SCISSORS] = True
BEATS[SCISSORS, PAPER] = True
BEATS[PAPER, ROCK] = True

BEATS[ROCK, FOUL] = True
BEATS[PAPER, FOUL] = True
BEATS[SCISSORS, FOUL] = True

BEATS[FOUL, ROCK] = True
BEATS[FOUL, PAPER] = True
BEATS[FOUL, SCISSORS] = True
BEATS[FOUL, FOUL] = True

BEATS[ROCK, WISE] = True
BEATS[PAPER, WISE] = True
BEATS[SCISSORS, WISE] = True
BEATS[FOUL, WISE] = True

BEATS[ROCK, KING] = True
BEATS[PAPER, KING] = True
BEATS[SCISSORS, KING] = True
BEATS[FOUL, KING] = True

PIECE_COUNT_PER_COLOR = SUM_OCC_OF_TYPE
PIECE_COUNT = PIECE_COUNT_PER_COLOR*COLOR_COUNT
PIECES = np.arange(PIECE_COUNT)

COLOR_OF_PIECE = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
TYPE_OF_PIECE = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)

PIECE_FROM_COLOR_TYPE_OCC = np.full((COLOR_COUNT, TYPE_COUNT, MAX_OCC_OF_TYPE), NOT_AN_INDEX, dtype=int)
KING_FROM_COLOR = np.full(COLOR_COUNT, NOT_AN_INDEX, dtype=int)
PIECE_FROM_COLOR_OCC = np.full((COLOR_COUNT, PIECE_COUNT_PER_COLOR), NOT_AN_INDEX, dtype=int)

piece_index = -1
for color_index in COLORS:
    color_occ = -1

    for type_index in TYPES:
        for type_occ in range(OCC_OF_TYPE[type_index]):
            piece_index += 1
                
            PIECE_FROM_COLOR_TYPE_OCC[color_index, type_index, type_occ] = piece_index           
            COLOR_OF_PIECE[piece_index] = color_index
            TYPE_OF_PIECE[piece_index] = type_index
            
            if type_index == KING:
                KING_FROM_COLOR[color_index] = piece_index
                
            color_occ += 1
            PIECE_FROM_COLOR_OCC[color_index, color_occ] = piece_index           


#>> The design of the location data must satisfiy the following requirements:
#>> - Any allowed move can be implemented as a series of moves between 
#>>   two locations.
#>> - The state of game can be implemented as a single numy array in order
#>>   to copy such state with high performance.                

FIELD_CELL_COUNT = 69
FIELD_LAYER_COUNT = 2
FIELD_LOC_COUNT = FIELD_LAYER_COUNT*FIELD_CELL_COUNT

RESERVE_LOC_COUNT_PER_COLOR = OCC_OF_TYPE[WISE] + OCC_OF_TYPE[MOUNTAIN]
RESERVE_LOC_COUNT = COLOR_COUNT*RESERVE_LOC_COUNT_PER_COLOR

JAIL_LOC_COUNT_PER_COLOR = PIECE_COUNT_PER_COLOR
JAIL_LOC_COUNT = COLOR_COUNT*JAIL_LOC_COUNT_PER_COLOR

LOBBY_LOC_COUNT_PER_COLOR = OCC_OF_TYPE[KING]
LOBBY_LOC_COUNT = COLOR_COUNT*LOBBY_LOC_COUNT_PER_COLOR

LOC_COUNT = 0
LOC_COUNT += FIELD_LOC_COUNT
LOC_COUNT += RESERVE_LOC_COUNT
LOC_COUNT += JAIL_LOC_COUNT
LOC_COUNT += LOBBY_LOC_COUNT

LOCS = np.arange(LOC_COUNT)

piece_from_location = np.full(LOC_COUNT, NOT_AN_INDEX, dtype=int)
location_from_piece = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)


#-- Auxiliary indexes for locations
FIELD_LOCS = np.arange(FIELD_LOC_COUNT)
FIELD_LOCS = FIELD_LOCS.reshape((FIELD_LAYER_COUNT, FIELD_CELL_COUNT))

RESERVE_LOCS = np.arange(RESERVE_LOC_COUNT)
RESERVE_LOCS += FIELD_LOCS.max()
RESERVE_LOCS = RESERVE_LOCS.reshape((COLOR_COUNT, RESERVE_LOC_COUNT_PER_COLOR))

JAIL_LOCS = np.arange(JAIL_LOC_COUNT)
JAIL_LOCS += RESERVE_LOCS.max()
JAIL_LOCS = JAIL_LOCS.reshape((COLOR_COUNT, JAIL_LOC_COUNT_PER_COLOR))

LOBBY_LOCS = np.arange(LOBBY_LOC_COUNT)
LOBBY_LOCS += JAIL_LOCS.max()
LOBBY_LOCS = LOBBY_LOCS.reshape((COLOR_COUNT, LOBBY_LOC_COUNT_PER_COLOR))




#-- How to loop on alive pieces of a given color ?


def test_locations_and_pieces_recovery():
    """This function shows, using a small example, that if one wants
    to minimize the number of arrays, then it is better to keep
    the array "location_from_piece" than the array "piece_from_location".
    """
    
    print()
    print("-- test_locations_and_pieces_recovery -- BEGIN")

    LOC_COUNT = 10
    PIECE_COUNT = 3
    PIECES = np.arange(PIECE_COUNT)
    LOCS = np.arange(LOC_COUNT)
    
    print()
    print("-- Define location_from_piece and deduce piece_from_location")

    location_from_piece = np.full(PIECE_COUNT, NOT_AN_INDEX, dtype=int)
    location_from_piece[0] = 7
    location_from_piece[1] = 2
    location_from_piece[2] = 5
    print("location_from_piece:", location_from_piece)

    piece_from_location = np.full(LOC_COUNT, NOT_AN_INDEX, dtype=int)
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
    
    location_from_selector = LOCS[selector]
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
    print("KING_FROM_COLOR:", KING_FROM_COLOR)
    print()
    print("LOC_COUNT:", LOC_COUNT)
    print()
    print("PIECE_COUNT:", PIECE_COUNT)
    print()
    print("FIELD_LOCS:", FIELD_LOCS)
    print()
    print("FIELD_LOCS[0, :]:", FIELD_LOCS[0,:])
    print()
    print("FIELD_LOCS[1, :]:", FIELD_LOCS[1,:])
    print()
    print("RESERVE_LOCS:", RESERVE_LOCS)
    print()
    print("JAIL_LOCS:", JAIL_LOCS)
    print()
    print("LOBBY_LOCS:", LOBBY_LOCS)
    print()
    
    
    test_locations_and_pieces_recovery()


if __name__ == "__main__":
    main()
