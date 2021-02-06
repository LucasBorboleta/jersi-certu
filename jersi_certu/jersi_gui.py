#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""jersi_gui.py implements a GUI for the JERSI boardgame."""


_COPYRIGHT_AND_LICENSE = """
JERSI-CERTU implements a GUI and a rule engine for the JERSI boardgame.

Copyright (C) 2019 Lucas Borboleta (lucas.borboleta@free.fr).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""


import enum
import math
import os
import sys

from PIL import Image
from PIL import ImageTk
##TODO: consider removing such PIL dependency

import tkinter as tk
from tkinter import font
from tkinter import ttk

_package_home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(_package_home)
import jersi_rules as rules


def rgb_color_as_hexadecimal(rgb_triplet):
    (red, green, blue) = rgb_triplet
    assert 0 <= red <= 255
    assert 0 <= green <= 255
    assert 0 <= red <= 255
    return '#%02x%02x%02x' % (red, green, blue)


class AppConfig:
    # File path containing the icon to be displayed in the title bar of Jersi GUI
    ICON_FILE = os.path.join(_package_home, 'pictures', 'jersi.ico')


class TinyVector:
    """Lightweight algebra on 2D vectors, inspired by numpy ndarray."""

    __slots__ = ("__x", "__y")

    def __init__(self, xy_pair=None):
        if xy_pair is None:
            self.__x = 0.
            self.__y = 0.

        else:
            self.__x = float(xy_pair[0])
            self.__y = float(xy_pair[1])


    def __repr__(self):
        return str(self)


    def __str__(self):
        return str((self.__x, self.__y))


    def __getitem__(self, key):
        if key == 0:
            return self.__x

        elif key == 1:
            return self.__y

        else:
            raise IndexError()


    def __neg__(self):
        return TinyVector((-self.__x , -self.__y))


    def __pos__(self):
        return TinyVector((self.__x , self.__y))


    def __add__(self, other):
        if isinstance(other, TinyVector):
            return TinyVector((self.__x + other.__x, self.__y + other.__y))

        elif isinstance(other, (int, float)):
            return TinyVector((self.__x + other, self.__y + other))

        else:
            raise NotImplementedError()


    def __sub__(self, other):
        if isinstance(other, TinyVector):
            return TinyVector((self.__x - other.__x, self.__y - other.__y))

        elif isinstance(other, (int, float)):
            return TinyVector((self.__x - other, self.__y - other))

        else:
            raise NotImplementedError()


    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return TinyVector((self.__x*other, self.__y*other))

        else:
            raise NotImplementedError()


    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return TinyVector((self.__x/other, self.__y/other))

        else:
            raise NotImplementedError()


    def __radd__(self, other):
        return self.__add__(other)


    def __rmul__(self, other):
        return self.__mul__(other)


    def __rtruediv__(self, other):
        return self.__div__(other)


    def __rsub__(self, other):
        if isinstance(other, TinyVector):
            return TinyVector((-self.__x + other.__x, -self.__y + other.__y))

        elif isinstance(other, (int, float)):
            return TinyVector((-self.__x + other, -self.__y + other))

        else:
            raise NotImplementedError()


    @staticmethod
    def inner(that, other):
        if isinstance(that, TinyVector) and isinstance(other, TinyVector):
            return (that.__x*other.__x + that.__y*other.__y)

        else:
            raise NotImplementedError()


    @staticmethod
    def norm(that):
        if isinstance(that, TinyVector):
            return math.sqrt(that.__x*that.__x + that.__y*that.__y)

        else:
            raise NotImplementedError()


class CanvasConfig:

    # Canvas x-y dimensions in hexagon units
    NX = 9 + 0.75
    NY = 9

    # Canvas x-y dimensions in pixels
    RATIO = NX/NY
    HEIGHT = 640
    WIDTH = HEIGHT*RATIO

    # Hexagon geometrical data
    HEXA_VERTEX_COUNT = 6
    HEXA_SIDE_ANGLE = 2*math.pi/HEXA_VERTEX_COUNT
    HEXA_WIDTH = min(HEIGHT, WIDTH) / max(NX, NY)
    HEXA_SIDE = HEXA_WIDTH*math.tan(HEXA_SIDE_ANGLE/2)
    HEXA_DELTA_Y = math.sqrt(HEXA_SIDE**2 -(HEXA_WIDTH/2)**2)

    # Cube (square) geometrical data
    CUBE_VERTEX_COUNT = 4
    CUBE_SIDE_ANGLE = math.pi/2

    # Font used for text in the canvas
    FONT_FAMILY = 'Calibri'
    FONT_LABEL_SIZE = int(0.30*HEXA_SIDE) # size for 'e5', 'f5' ...
    FONT_FACE_SIZE = int(0.50*HEXA_SIDE)  # size for 'K', 'F' ...

    # Geometrical line widths
    CUBE_LINE_WIDTH = 1
    HEXA_LINE_WIDTH = 1

    # Origin of the orthonormal x-y frame and the oblic u-v frame
    ORIGIN = TinyVector((WIDTH/2, HEIGHT/2))

    # Unit vectors of the orthonormal x-y frame
    UNIT_X = TinyVector((1, 0))
    UNIT_Y = TinyVector((0, -1))

    # Unit vectors of the oblic u-v frame
    UNIT_U = UNIT_X
    UNIT_V = math.cos(HEXA_SIDE_ANGLE)*UNIT_X + math.sin(HEXA_SIDE_ANGLE)*UNIT_Y


class CubeConfig:
    # File path containing the icon to be displayed in the title bar of Jersi GUI

    __cube_file_name = {}

    __cube_file_name[(rules.Player.BLACK, rules.CubeSort.KING)] = 'king-black.png'
    __cube_file_name[(rules.Player.BLACK, rules.CubeSort.WISE)] = 'wise-black.png'
    __cube_file_name[(rules.Player.BLACK, rules.CubeSort.FOUL)] = 'foul-black.png'
    __cube_file_name[(rules.Player.BLACK, rules.CubeSort.ROCK)] = 'rock-black.png'
    __cube_file_name[(rules.Player.BLACK, rules.CubeSort.PAPER)] = 'paper-black.png'
    __cube_file_name[(rules.Player.BLACK, rules.CubeSort.SCISSORS)] = 'scissors-black.png'
    __cube_file_name[(rules.Player.BLACK, rules.CubeSort.MOUNTAIN)] = 'mountain-black.png'

    __cube_file_name[(rules.Player.WHITE, rules.CubeSort.KING)] = 'king-white.png'
    __cube_file_name[(rules.Player.WHITE, rules.CubeSort.WISE)] = 'wise-white.png'
    __cube_file_name[(rules.Player.WHITE, rules.CubeSort.FOUL)] = 'foul-white.png'
    __cube_file_name[(rules.Player.WHITE, rules.CubeSort.ROCK)] = 'rock-white.png'
    __cube_file_name[(rules.Player.WHITE, rules.CubeSort.PAPER)] = 'paper-white.png'
    __cube_file_name[(rules.Player.WHITE, rules.CubeSort.SCISSORS)] = 'scissors-white.png'
    __cube_file_name[(rules.Player.WHITE, rules.CubeSort.MOUNTAIN)] = 'mountain-white.png'

    CUBE_FILE_PATH = {}

    for (file_key, file_name) in __cube_file_name.items():
        CUBE_FILE_PATH[file_key] =os.path.join(_package_home, 'pictures', file_name)


class CubeLocation(enum.Enum):
    BOTTOM = enum.auto()
    MIDDLE = enum.auto()
    TOP = enum.auto()


@enum.unique
class CubeColor(enum.Enum):
    BLACK = 'black'
    WHITE = 'white'


@enum.unique
class HexagonColor(enum.Enum):
    BORDER = rgb_color_as_hexadecimal((191, 89, 52))
    DARK = rgb_color_as_hexadecimal((166, 109, 60))
    LIGHT = rgb_color_as_hexadecimal((242, 202, 128))
    RESERVE = rgb_color_as_hexadecimal((191, 184, 180))


@enum.unique
class HexagonLineColor(enum.Enum):
    NORMAL = 'black'
    RESERVE = ''


class GraphicalHexagon:

    __all_sorted_hexagons = []
    __init_done = False
    __name_to_hexagon = {}

    all = None


    def __init__(self, hexagon, color, relative_shift_xy=None):

        assert hexagon.name not in GraphicalHexagon.__name_to_hexagon
        assert color in HexagonColor
        assert (relative_shift_xy is not None) == hexagon.reserve

        self.name = hexagon.name
        self.position_uv = hexagon.position_uv
        self.reserve = hexagon.reserve
        self.index = hexagon.index
        self.color = color
        self.__relative_shift_xy = relative_shift_xy

        if relative_shift_xy is not None:
            (shift_x, shift_y) = relative_shift_xy
            self.shift_xy = (shift_x*CanvasConfig.HEXA_WIDTH*CanvasConfig.UNIT_X +
                             shift_y*CanvasConfig.HEXA_DELTA_Y*CanvasConfig.UNIT_Y)
        else:
            self.shift_xy = None

        GraphicalHexagon.__name_to_hexagon[self.name] = self


    def __str__(self):
        return f"GraphicalHexagon({self.name}, {self.position_uv}, {self.reserve}, {self.index}, {self.color}, {self.__relative_shift_xy})"


    @staticmethod
    def get(name):
        return GraphicalHexagon.__name_to_hexagon[name]


    @staticmethod
    def init():
        if not GraphicalHexagon.__init_done:
            GraphicalHexagon.__create_hexagons()
            GraphicalHexagon.__create_all_sorted_hexagons()
            GraphicalHexagon.__init_done = True


    @staticmethod
    def show_all():
        for hexagon in GraphicalHexagon.__all_sorted_hexagons:
            print(hexagon)


    @staticmethod
    def __create_all_sorted_hexagons():
        for name in sorted(GraphicalHexagon.__name_to_hexagon.keys()):
            GraphicalHexagon.__all_sorted_hexagons.append(GraphicalHexagon.__name_to_hexagon[name])

        GraphicalHexagon.all = GraphicalHexagon.__all_sorted_hexagons


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

        for hexagon in rules.Hexagon.all:

            if hexagon.reserve:
                color = HexagonColor.RESERVE

                if hexagon.name == 'a':
                    relative_shift_xy = (0.75, -1.00)

                elif hexagon.name == 'b':
                    relative_shift_xy = (0.25, 0.00)

                elif hexagon.name == 'c':
                    relative_shift_xy = (0.75, 1.00)

                elif hexagon.name == 'g':
                    relative_shift_xy = (-0.75, -1.00)

                elif hexagon.name == 'h':
                    relative_shift_xy = (-0.25, 0.00)

                elif hexagon.name == 'i':
                    relative_shift_xy = (-0.75, 1.00)

                else:
                    assert False

            elif hexagon.name in borders:
                color = HexagonColor.BORDER
                relative_shift_xy = None

            elif hexagon.name in darks:
                color = HexagonColor.DARK
                relative_shift_xy = None
            else:
                color = HexagonColor.LIGHT
                relative_shift_xy = None

            GraphicalHexagon(hexagon, color, relative_shift_xy)


class GameGui(ttk.Frame):


    def __init__(self):

        self.__face_drawers = dict()
        self.__face_drawers[rules.CubeSort.FOUL] = self.__draw_foul_face
        self.__face_drawers[rules.CubeSort.KING] = self.__draw_king_face
        self.__face_drawers[rules.CubeSort.PAPER] = self.__draw_paper_face
        self.__face_drawers[rules.CubeSort.ROCK] = self.__draw_rock_face
        self.__face_drawers[rules.CubeSort.SCISSORS] = self.__draw_scissors_face
        self.__face_drawers[rules.CubeSort.MOUNTAIN] = self.__draw_mountain_face
        self.__face_drawers[rules.CubeSort.WISE] = self.__draw_wise_face

        self.__cube_photos = None


        self.__cube_faces_options = ("faces=letters", "faces=drawings", "faces=pictures")
        self.__cube_faces = self.__cube_faces_options[2]

        self.__draw_reserve = True

        self.__game = None
        self.__game_started = False
        self.__jersi_state = rules.JersiState()
        self.__searcher = [None, None]

        self.__action_input = None
        self.__action_validated = False

        self.__root = tk.Tk()

        try:
            self.__root.title("jersi-certu : for playing the jersi 4.x boardgame and testing AI agents")
            self.__root.iconbitmap(AppConfig.ICON_FILE)
        except:
            pass

        self.__create_widgets()
        self.__draw_state()

        self.__command_update_faces()
        self.__command_update_reserve()
        self.__command_update_players()

        self.__variable_log.set("jersi-certu GUI is ready !")

        self.__root.mainloop()


    def __create_widgets(self):

        searcher_catalog_names = rules.SEARCHER_CATALOG.get_names()
        searcher_catalog_names_width = max(map(len, searcher_catalog_names))

        # Frames

        self.__frame_left = ttk.Frame(self.__root)
        self.__frame_right = ttk.Frame(self.__root)

        self.__frame_left.pack(side=tk.LEFT)
        self.__frame_right.pack(side=tk.TOP)

        self.__frame_commands_and_players = ttk.Frame(self.__frame_right)
        self.__frame_actions = ttk.Frame(self.__frame_right)

        self.__frame_commands_and_players.pack(side=tk.TOP)

        self.__frame_board = ttk.Frame(self.__frame_left, padding=10)

        self.__frame_actions.pack(side=tk.TOP)
        self.__frame_board.pack(side=tk.TOP)

        self.__frame_commands = ttk.Frame(self.__frame_commands_and_players, padding=20)
        self.__frame_players = ttk.Frame(self.__frame_commands_and_players, padding=20)

        self.__frame_commands.pack(side=tk.LEFT)
        self.__frame_players.pack(side=tk.LEFT)

        self.__frame_human_actions = ttk.Frame(self.__frame_actions, padding=10)
        self.__frame_text_actions = ttk.Frame(self.__frame_actions)

        # In __frame_commands

        self.__button_quit = ttk.Button(self.__frame_commands,
                                 text='Quit',
                                 command=self.__root.destroy)

        self.__button_start_stop = ttk.Button(self.__frame_commands,
                                  text='Start',
                                  command=self.__command_start_stop)


        self.__variable_reserve = tk.BooleanVar()
        self.__variable_reserve.set(self.__draw_reserve)
        self.__button_reserve = ttk.Checkbutton (self.__frame_commands,
                                       text='Show reserve',
                                       command=self.__command_update_reserve,
                                       variable=self.__variable_reserve)

        self.__variable_faces = tk.StringVar()
        self.__combobox_button_faces = ttk.Combobox(self.__frame_commands,
                                                  width=max(map(len, self.__cube_faces_options)),
                                                  textvariable=self.__variable_faces,
                                                  values=self.__cube_faces_options)
        self.__combobox_button_faces.set(self.__cube_faces_options[2])
        self.__variable_faces.trace_add('write', self.__command_update_faces)

        self.__button_start_stop.grid(row=0, column=0)
        self.__button_quit.grid(row=0, column=1)

        self.__button_reserve.grid(row=1, column=0)
        self.__combobox_button_faces.grid(row=1, column=1)

        self.__frame_commands.rowconfigure(0, pad=5)
        self.__frame_commands.rowconfigure(1, pad=5)
        self.__frame_commands.columnconfigure(0, pad=5)
        self.__frame_commands.columnconfigure(1, pad=5)

        # In __frame_players

        self.__label_white_player = ttk.Label(self.__frame_players, text='White :')

        self.__variable_white_player = tk.StringVar()
        self.__combobox_white_player = ttk.Combobox(self.__frame_players,
                                                  width=searcher_catalog_names_width,
                                                  textvariable=self.__variable_white_player,
                                                  values=searcher_catalog_names)
        self.__combobox_white_player.config(state="readonly")
        self.__variable_white_player.set(searcher_catalog_names[0])


        self.__label_black_player = ttk.Label(self.__frame_players, text='Black :')

        self.__variable_black_player = tk.StringVar()
        self.__combobox_black_player = ttk.Combobox(self.__frame_players,
                                                  width=searcher_catalog_names_width,
                                                  textvariable=self.__variable_black_player,
                                                  values=searcher_catalog_names)
        self.__combobox_black_player.config(state="readonly")
        self.__variable_black_player.set(searcher_catalog_names[0])


        self.__progressbar = ttk.Progressbar(self.__frame_players,
                                            orient=tk.HORIZONTAL,
                                            length=300,
                                            maximum=100,
                                            mode='determinate')

        self.__label_white_player.grid(row=0, column=0)
        self.__combobox_white_player.grid(row=0, column=1)

        self.__label_black_player.grid(row=0, column=2)
        self.__combobox_black_player.grid(row=0, column=3)

        self.__progressbar.grid(row=1, columnspan=4)

        self.__frame_players.rowconfigure(0, pad=5)
        self.__frame_players.rowconfigure(1, pad=5)

        self.__variable_white_player.trace_add('write', self.__command_update_players)
        self.__variable_black_player.trace_add('write', self.__command_update_players)

        # In __frame_board

        self.__canvas = tk.Canvas(self.__frame_board,
                                height=CanvasConfig.HEIGHT,
                                width=CanvasConfig.WIDTH)
        self.__canvas.pack(side=tk.TOP)

       # In __frame_actions

        self.__variable_log = tk.StringVar()
        self.__label_log = ttk.Label(self.__frame_actions,
                                  textvariable=self.__variable_log,
                                  width=90,
                                  padding=5,
                                  foreground='red',
                                  borderwidth=2, relief="groove")

        self.__variable_summary = tk.StringVar()
        self.__label_summary = ttk.Label(self.__frame_actions,
                                  textvariable=self.__variable_summary,
                                  width=90,
                                  padding=5,
                                  foreground='black',
                                  borderwidth=2, relief="groove")

       # In __frame_human_actions

        self.__label_action = ttk.Label(self.__frame_human_actions, text='Action (without any !) :')

        self.__variable_action = tk.StringVar()
        self.__entry_action = ttk.Entry(self.__frame_human_actions, textvariable=self.__variable_action)

        self.__button_action_confirm = ttk.Button(self.__frame_human_actions,
                                  text='OK',
                                  command=self.__command_action_confirm)
       # In __frame_text_actions

        self.__text_actions = tk.Text(self.__frame_text_actions,
                                  width=60,
                                  background='lightgrey',
                                  borderwidth=2, relief="groove")

        self.__scrollbar_actions = ttk.Scrollbar(self.__frame_text_actions, orient = 'vertical')

        self.__text_actions.config(yscrollcommand=self.__scrollbar_actions.set)
        self.__scrollbar_actions.config(command=self.__text_actions.yview)

        self.__label_log.pack(side=tk.TOP)
        self.__label_summary.pack(side=tk.TOP, pady=10)

        self.__frame_human_actions.pack(side=tk.TOP)
        self.__label_action.pack(side=tk.LEFT)
        self.__entry_action.pack(side=tk.LEFT)
        self.__button_action_confirm.pack(side=tk.LEFT)

        self.__frame_text_actions.pack(side=tk.TOP)
        self.__scrollbar_actions.pack(side=tk.LEFT, fill=tk.Y)
        self.__text_actions.pack(side=tk.LEFT)

        self.__entry_action.config(state="disabled")
        self.__button_action_confirm.config(state="disabled")
        self.__text_actions.config(state="disabled")


    def __create_cube_photos(self):
        if self.__cube_photos is None:

            cube_photo_width = int(CanvasConfig.HEXA_SIDE*math.cos(math.pi/4))

            self.__cube_photos = {}

            for (key, file) in CubeConfig.CUBE_FILE_PATH.items():
                cube_photo = Image.open(CubeConfig.CUBE_FILE_PATH[key])
                cube_photo = cube_photo.resize((cube_photo_width, cube_photo_width))
                cube_tk_photo = ImageTk.PhotoImage(cube_photo)
                self.__cube_photos[key] = cube_tk_photo


    def __command_update_faces(self, *_):
        self.__cube_faces = self.__variable_faces.get()
        self.__draw_state()


    def __command_update_reserve(self):
        self.__draw_reserve = self.__variable_reserve.get()
        self.__draw_state()


    def __command_update_players(self, *_):
        self.__searcher[rules.Player.WHITE] = rules.SEARCHER_CATALOG.get(self.__variable_white_player.get())
        self.__searcher[rules.Player.BLACK] = rules.SEARCHER_CATALOG.get(self.__variable_black_player.get())


    def __command_action_confirm(self):
        self.__action_input = self.__variable_action.get()

        (self.__action_validated,
         message) = rules.Notation.validate_simple_notation(self.__action_input,
                                                                  self.__jersi_state.get_action_simple_names())

        if self.__action_validated:
            self.__variable_log.set(message)
            self.__variable_action.set("")

        else:
            self.__variable_log.set(message)


    def __command_start_stop(self):

        self.__entry_action.config(state="disabled")
        self.__button_action_confirm.config(state="disabled")

        self.__game_started = not self.__game_started

        if self.__game_started:

           self.__game = rules.Game()
           self.__game.set_white_searcher(self.__searcher[rules.Player.WHITE])
           self.__game.set_black_searcher(self.__searcher[rules.Player.BLACK])
           self.__game.start()

           self.__jersi_state = self.__game.get_state()
           self.__draw_state()

           self.__button_start_stop.configure(text="Stop")

           self.__variable_log.set(self.__game.get_log())
           self.__variable_summary.set(self.__game.get_summary())
           self.__progressbar['value'] = 50.

           self.__combobox_white_player.config(state="disabled")
           self.__combobox_black_player.config(state="disabled")

           self.__text_actions.config(state="normal")
           self.__text_actions.delete('1.0', tk.END)
           self.__text_actions.config(state="disabled")

           self.__canvas.after(500, self.__command_next_turn)

        else:
           self.__combobox_white_player.config(state="readonly")
           self.__combobox_black_player.config(state="readonly")

           self.__entry_action.config(state="enabled")
           self.__variable_action.set("")
           self.__entry_action.config(state="disabled")
           self.__button_action_confirm.config(state="disabled")

           self.__variable_log.set("jersi stopped")
           self.__button_start_stop.configure(text="Start")
           self.__progressbar['value'] = 0.


    def __command_next_turn(self):

        if self.__game_started and self.__game.has_next_turn():

            self.__jersi_state = self.__game.get_state()
            player = self.__jersi_state.get_current_player()
            searcher = self.__searcher[player]

            self.__progressbar['value'] = 50.

            ready_for_next_turn = False

            if searcher.is_interactive():
                self.__entry_action.config(state="enabled")
                self.__button_action_confirm.config(state="enabled")
                self.__progressbar['value'] = 0.

                if self.__action_validated and self.__action_input is not None:
                    ready_for_next_turn = True

                    searcher.set_action_simple_name(self.__action_input)

                    self.__action_input = None
                    self.__action_validated = False
                    self.__entry_action.config(state="disabled")
                    self.__button_action_confirm.config(state="disabled")

            else:
                ready_for_next_turn = True

            if ready_for_next_turn:
                self.__progressbar['value'] = 50.
                self.__game.next_turn()
                self.__jersi_state = self.__game.get_state()
                self.__draw_state()

                self.__variable_summary.set(self.__game.get_summary())
                self.__variable_log.set(self.__game.get_log())

                self.__text_actions.config(state="normal")

                turn = self.__game.get_turn()
                notation = str(turn).rjust(4) + " " + self.__game.get_last_action().ljust(16)
                if turn % 2 == 0:
                    notation = ' '*2 + notation + "\n"

                self.__text_actions.insert(tk.END, notation)
                self.__text_actions.see(tk.END)
                self.__text_actions.config(state="disabled")

            self.__canvas.after(500, self.__command_next_turn)

        else:
           self.__combobox_white_player.config(state="readonly")
           self.__combobox_black_player.config(state="readonly")

           self.__progressbar['value'] = 0.

           self.__game_started = False
           self.__button_start_stop.configure(text="Start")


    ### Drawer iterators

    def __draw_state(self):

        self.__canvas.delete('all')
        self.__draw_all_hexagons()
        self.__draw_all_cubes()


    def __draw_all_cubes(self):

        hexagon_top =  self.__jersi_state.get_hexagon_top()
        hexagon_bottom =  self.__jersi_state.get_hexagon_bottom()

        for hexagon in rules.Hexagon.all:

            top_index = hexagon_top[hexagon.index]
            bottom_index = hexagon_bottom[hexagon.index]

            if top_index != rules.Null.CUBE and bottom_index != rules.Null.CUBE:

                top = rules.Cube.all[top_index]
                bottom = rules.Cube.all[bottom_index]

                self.__draw_cube(name=hexagon.name, config=CubeLocation.TOP,
                               cube_color=top.player, cube_sort=top.sort, cube_label=top.label)

                self.__draw_cube(name=hexagon.name, config=CubeLocation.BOTTOM,
                               cube_color=bottom.player, cube_sort=bottom.sort, cube_label=bottom.label)

            elif top_index != rules.Null.CUBE:

                top = rules.Cube.all[top_index]

                self.__draw_cube(name=hexagon.name, config=CubeLocation.MIDDLE,
                               cube_color=top.player, cube_sort=top.sort, cube_label=top.label)

            elif bottom_index != rules.Null.CUBE:

                bottom = rules.Cube.all[bottom_index]

                self.__draw_cube(name=hexagon.name, config=CubeLocation.MIDDLE,
                               cube_color=bottom.player, cube_sort=bottom.sort, cube_label=bottom.label)

            else:
                pass


    def __draw_all_hexagons(self):

        for hexagon in GraphicalHexagon.all:

            self.__draw_hexagon(position_uv=hexagon.position_uv,
                         fill_color=hexagon.color.value,
                         label=hexagon.name,
                         reserve=hexagon.reserve,
                         shift_xy=hexagon.shift_xy)


    ### Drawer primitives

    def __draw_hexagon(self, position_uv, fill_color='', label='', reserve=False, shift_xy=None):

        if reserve and not self.__draw_reserve:
            return

        (u, v) = position_uv

        hexagon_center = CanvasConfig.ORIGIN + CanvasConfig.HEXA_WIDTH*(u*CanvasConfig.UNIT_U + v*CanvasConfig.UNIT_V)

        if shift_xy is not None:
            hexagon_center = hexagon_center + shift_xy

        hexagon_data = list()

        for vertex_index in range(CanvasConfig.HEXA_VERTEX_COUNT):
            vertex_angle = (1/2 + vertex_index)*CanvasConfig.HEXA_SIDE_ANGLE

            hexagon_vertex = hexagon_center
            hexagon_vertex = hexagon_vertex + CanvasConfig.HEXA_SIDE*math.cos(vertex_angle)*CanvasConfig.UNIT_X
            hexagon_vertex = hexagon_vertex + CanvasConfig.HEXA_SIDE*math.sin(vertex_angle)*CanvasConfig.UNIT_Y

            hexagon_data.append(hexagon_vertex[0])
            hexagon_data.append(hexagon_vertex[1])

            if vertex_index == 3:
                label_position = (hexagon_vertex +
                                  0.25*CanvasConfig.HEXA_SIDE*(CanvasConfig.UNIT_X + 0.75*CanvasConfig.UNIT_Y))


        if reserve:
            polygon_line_color = HexagonLineColor.RESERVE.value
        else:
            polygon_line_color = HexagonLineColor.NORMAL.value

        self.__canvas.create_polygon(hexagon_data,
                              fill=fill_color,
                              outline=polygon_line_color,
                              width=CanvasConfig.HEXA_LINE_WIDTH,
                              joinstyle=tk.MITER)

        if label and not reserve:
            label_font = font.Font(family=CanvasConfig.FONT_FAMILY, size=CanvasConfig.FONT_LABEL_SIZE, weight='bold')

            self.__canvas.create_text(*label_position, text=label, justify=tk.CENTER, font=label_font)


    def __draw_cube(self, name, config, cube_color, cube_sort, cube_label):

        hexagon = GraphicalHexagon.get(name)

        if hexagon.reserve and not self.__draw_reserve:
            return

        (u, v) = hexagon.position_uv

        hexagon_center = CanvasConfig.ORIGIN + CanvasConfig.HEXA_WIDTH*(u*CanvasConfig.UNIT_U + v*CanvasConfig.UNIT_V)

        if hexagon.shift_xy is not None:
            hexagon_center = hexagon_center + hexagon.shift_xy

        cube_vertices = list()

        for vertex_index in range(CanvasConfig.CUBE_VERTEX_COUNT):
            vertex_angle = (1/2 + vertex_index)*CanvasConfig.CUBE_SIDE_ANGLE

            if config == CubeLocation.MIDDLE:
                cube_center = hexagon_center

            elif config == CubeLocation.BOTTOM:
                cube_center = hexagon_center - 0.40*CanvasConfig.HEXA_SIDE*CanvasConfig.UNIT_Y

            elif config == CubeLocation.TOP:
                cube_center = hexagon_center + 0.40*CanvasConfig.HEXA_SIDE*CanvasConfig.UNIT_Y

            cube_vertex = cube_center
            cube_vertex = cube_vertex + 0.5*CanvasConfig.HEXA_SIDE*math.cos(vertex_angle)*CanvasConfig.UNIT_X
            cube_vertex = cube_vertex + 0.5*CanvasConfig.HEXA_SIDE*math.sin(vertex_angle)*CanvasConfig.UNIT_Y

            cube_vertices.append(cube_vertex)


        if cube_color == rules.Player.BLACK:
            fill_color = CubeColor.BLACK.value
            face_color = CubeColor.WHITE.value

        elif cube_color == rules.Player.WHITE:
            fill_color = CubeColor.WHITE.value
            face_color = CubeColor.BLACK.value

        else:
            assert False


        line_color = ''

        cube_vertex_NW = cube_vertices[1]
        cube_vertex_SE = cube_vertices[3]

        if self.__cube_faces == 'faces=pictures':

            if self.__cube_photos is None:
                self.__create_cube_photos()

            cube_tk_photo = self.__cube_photos[(cube_color, cube_sort)]
            self.__canvas.create_image(cube_center[0], cube_center[1], image=cube_tk_photo, anchor=tk.CENTER)

        elif self.__cube_faces == 'faces=drawings':

            self.__canvas.create_rectangle(*cube_vertex_NW, *cube_vertex_SE,
                                fill=fill_color,
                                outline=line_color)
            self.__face_drawers[cube_sort](cube_center, cube_vertices, face_color)

        elif self.__cube_faces == 'faces=letters':

            self.__canvas.create_rectangle(*cube_vertex_NW, *cube_vertex_SE,
                                fill=fill_color,
                                outline=line_color)

            face_font = font.Font(family=CanvasConfig.FONT_FAMILY, size=CanvasConfig.FONT_FACE_SIZE, weight='bold')

            self.__canvas.create_text(*cube_center,
                               text=cube_label,
                               justify=tk.CENTER,
                               font=face_font,
                               fill=face_color)
        else:
            assert False

    def __draw_king_face(self, cube_center, cube_vertices, face_color):
        pass


    def __draw_foul_face(self, cube_center, cube_vertices, face_color):


        def rotate_90_degrees(vector):
            """Rotate 90 degrees counter clock"""
            projection_x = TinyVector.inner(vector, CanvasConfig.UNIT_X)
            projection_y = TinyVector.inner(vector, CanvasConfig.UNIT_Y)
            rotated_unit_x = CanvasConfig.UNIT_Y
            rotated_unit_y = -CanvasConfig.UNIT_X
            return projection_x*rotated_unit_x + projection_y*rotated_unit_y


        def square_for_circle_by_two_points(point_1, point_2):
            """Return two points of the square enclosing the circle passing by to given points"""
            square_center = 0.5*(point_1 + point_2)
            square_point_1 = point_1 + rotate_90_degrees(point_1 - square_center)
            square_point_2 = point_2 + rotate_90_degrees(point_2 - square_center)
            return (square_point_1, square_point_2)


        face_vertex_NE = 0.5*cube_center + 0.5*cube_vertices[0]
        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SW = 0.5*cube_center + 0.5*cube_vertices[2]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        face_vertex_N = 0.5*(face_vertex_NW + face_vertex_NE)
        face_vertex_S = 0.5*(face_vertex_SW + face_vertex_SE)

        face_vertex_NC = 0.5*(face_vertex_N + cube_center)
        face_vertex_SC = 0.5*(face_vertex_S + cube_center)

        cube_side = TinyVector.norm(face_vertex_NW - face_vertex_NE)

        # little angular overlap to ensure coninuity bewteen arcs
        angle_epsilon = 0.01*180

        (p1, p2) = square_for_circle_by_two_points(cube_center, face_vertex_SC)
        self.__canvas.create_arc(*p1, *p2,
                          start=90,
                          extent=180,
                          fill='',
                          outline=face_color,
                          style=tk.ARC,
                          width=CanvasConfig.CUBE_LINE_WIDTH)

        (p1, p2) = square_for_circle_by_two_points(face_vertex_NC, face_vertex_SC)
        self.__canvas.create_arc(*p1, *p2,
                          start=-90 - angle_epsilon,
                          extent=180 + angle_epsilon,
                          fill='',
                          outline=face_color,
                          style=tk.ARC,
                          width=CanvasConfig.CUBE_LINE_WIDTH)

        (p1, p2) = square_for_circle_by_two_points(face_vertex_NC, face_vertex_S)
        self.__canvas.create_arc(*p1, *p2,
                          start=90 - angle_epsilon,
                          extent=180 + angle_epsilon,
                          fill='',
                          outline=face_color,
                          style=tk.ARC,
                          width=CanvasConfig.CUBE_LINE_WIDTH)

        (p1, p2) = square_for_circle_by_two_points(face_vertex_N, face_vertex_S)
        self.__canvas.create_arc(*p1, *p2,
                          start=-90 - angle_epsilon,
                          extent=180 + 45 + angle_epsilon,
                          fill='',
                          outline=face_color,
                          style=tk.ARC,
                          width=CanvasConfig.CUBE_LINE_WIDTH)

        # >> canvas doesn't provide rounded capstype for arc
        # >> so let add one small circle at each edge of the spiral

        # add small circle at the inner edge of the spiral

        inner_edge_top = cube_center + CanvasConfig.CUBE_LINE_WIDTH*0.5*CanvasConfig.UNIT_Y
        edge_edge_bottom = cube_center - CanvasConfig.CUBE_LINE_WIDTH*0.5*CanvasConfig.UNIT_Y

        (p1, p2) = square_for_circle_by_two_points(inner_edge_top, edge_edge_bottom)
        self.__canvas.create_oval(*p1, *p2,
                           fill=face_color,
                           outline='')

        # add small circle at the outer edge of the spiral

        outer_edge_middle = cube_center + cube_side/2*(CanvasConfig.UNIT_Y - CanvasConfig.UNIT_X)/math.sqrt(2)

        outer_edge_top = outer_edge_middle + CanvasConfig.CUBE_LINE_WIDTH*0.5*CanvasConfig.UNIT_Y
        outer_edge_bottom = outer_edge_middle - CanvasConfig.CUBE_LINE_WIDTH*0.5*CanvasConfig.UNIT_Y

        (p1, p2) = square_for_circle_by_two_points(outer_edge_top, outer_edge_bottom)
        self.__canvas.create_oval(*p1, *p2,
                           fill=face_color,
                           outline='')


    def __draw_paper_face(self, cube_center, cube_vertices, face_color):

        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        self.__canvas.create_rectangle(*face_vertex_NW, *face_vertex_SE,
                                fill='',
                                outline=face_color,
                                width=CanvasConfig.CUBE_LINE_WIDTH)


    def __draw_rock_face(self, cube_center, cube_vertices, face_color):

        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        self.__canvas.create_oval(*face_vertex_NW, *face_vertex_SE,
                           fill='',
                           outline=face_color,
                           width=CanvasConfig.CUBE_LINE_WIDTH)


    def __draw_scissors_face(self, cube_center, cube_vertices, face_color):

        face_vertex_NE = 0.5*cube_center + 0.5*cube_vertices[0]
        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SW = 0.5*cube_center + 0.5*cube_vertices[2]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        self.__canvas.create_line(*face_vertex_NE, *face_vertex_SW,
                           fill=face_color,
                           width=CanvasConfig.CUBE_LINE_WIDTH,
                           capstyle=tk.ROUND)

        self.__canvas.create_line(*face_vertex_NW, *face_vertex_SE,
                           fill=face_color,
                           width=CanvasConfig.CUBE_LINE_WIDTH,
                           capstyle=tk.ROUND)


    def __draw_mountain_face(self, cube_center, cube_vertices, face_color):

        face_vertex_NE = 0.5*cube_center + 0.5*cube_vertices[0]
        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SW = 0.5*cube_center + 0.5*cube_vertices[2]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        face_N = 0.5*(face_vertex_NW + face_vertex_NE)
        face_S = 0.5*(face_vertex_SW + face_vertex_SE)

        face_W = 0.5*(face_vertex_NW + face_vertex_SW)
        face_E = 0.5*(face_vertex_NE + face_vertex_SE)

        face_data = [*face_N, *face_W, *face_E]

        self.__canvas.create_polygon(face_data,
                              fill='',
                              outline=face_color,
                              width=CanvasConfig.CUBE_LINE_WIDTH,
                              joinstyle=tk.ROUND)

        face_data = [*face_S, *face_W, *face_E]

        self.__canvas.create_polygon(face_data,
                              fill='',
                              outline=face_color,
                              width=CanvasConfig.CUBE_LINE_WIDTH,
                              joinstyle=tk.ROUND)


    def __draw_wise_face(self, cube_center, cube_vertices, face_color):

        draw_lemniscate = True

        face_vertex_NE = 0.5*cube_center + 0.5*cube_vertices[0]
        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SW = 0.5*cube_center + 0.5*cube_vertices[2]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        face_vertex_W = 0.5*(face_vertex_NW + face_vertex_SW)

        wise_data = list()

        if draw_lemniscate:

            # -- Equation retrieve from my GeoGebra drawings --
            # Curve(x(C) + (x(C) - x(W)) cos(t) / (1 + sin²(t)),
            #        y(C) + (x(C) - x(W)) cos(t) sin(t) / (1 + sin²(t)),
            #        t, 0, 2π)
            # C : cube_center
            # W : face_vertex_W

            delta = cube_center[0] - face_vertex_W[0]

            angle_count = 20
            for angle_index in range(angle_count):
                angle_value = angle_index*2*math.pi/angle_count

                angle_sinus = math.sin(angle_value)
                angle_cosinus = math.cos(angle_value)

                x = cube_center[0] + delta*angle_cosinus/(1 + angle_sinus**2)
                y = cube_center[1] + delta*angle_cosinus*angle_sinus/(1 + angle_sinus**2)

                wise_data.append(x)
                wise_data.append(y)

        else:
            wise_data.extend(face_vertex_NW)
            wise_data.extend(face_vertex_SE)
            wise_data.extend(face_vertex_NE)
            wise_data.extend(face_vertex_SW)

        self.__canvas.create_polygon(wise_data,
                              fill='',
                              outline=face_color,
                              width=CanvasConfig.CUBE_LINE_WIDTH,
                              joinstyle=tk.ROUND,
                              smooth=True)



GraphicalHexagon.init()


def main():
    print("Hello")
    print(_COPYRIGHT_AND_LICENSE)

    _ = GameGui()

    print("Bye")


if __name__ == "__main__":
    main()