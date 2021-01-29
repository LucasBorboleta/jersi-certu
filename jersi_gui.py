#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""jersi_gui.py implements a GUI for the JERSI boardgame."""


_COPYRIGHT_AND_LICENSE = """
JERSI-CERTU implements a GUI and a rule engine for the JERSI boardgame.

Copyright (C) 2020 Lucas Borboleta (lucas.borboleta@free.fr).

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

import tkinter as tk
from tkinter import font
from tkinter import ttk

import numpy as np

_script_home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(_script_home)
import jersi_certu


def rgb_color_as_hexadecimal(rgb_triplet):
    (red, green, blue) = rgb_triplet
    assert 0 <= red <= 255
    assert 0 <= green <= 255
    assert 0 <= red <= 255
    return '#%02x%02x%02x' % (red, green, blue)


class AppConfig:
    # File path containing the icon to be displayed in the title bar of Jersi GUI
    ICON_FILE = os.path.join(_script_home, 'jersi.ico')

    CUBE_FILE_NAMES = {}

    CUBE_FILE_NAMES[(jersi_certu.Player.BLACK, jersi_certu.CubeSort.KING)] = 'king-black.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.BLACK, jersi_certu.CubeSort.WISE)] = 'wise-black.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.BLACK, jersi_certu.CubeSort.FOUL)] = 'foul-black.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.BLACK, jersi_certu.CubeSort.ROCK)] = 'rock-black.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.BLACK, jersi_certu.CubeSort.PAPER)] = 'paper-black.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.BLACK, jersi_certu.CubeSort.SCISSORS)] = 'scissors-black.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.BLACK, jersi_certu.CubeSort.MOUNTAIN)] = 'mountain-black.png'

    CUBE_FILE_NAMES[(jersi_certu.Player.WHITE, jersi_certu.CubeSort.KING)] = 'king-white.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.WHITE, jersi_certu.CubeSort.WISE)] = 'wise-white.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.WHITE, jersi_certu.CubeSort.FOUL)] = 'foul-white.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.WHITE, jersi_certu.CubeSort.ROCK)] = 'rock-white.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.WHITE, jersi_certu.CubeSort.PAPER)] = 'paper-white.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.WHITE, jersi_certu.CubeSort.SCISSORS)] = 'scissors-white.png'
    CUBE_FILE_NAMES[(jersi_certu.Player.WHITE, jersi_certu.CubeSort.MOUNTAIN)] = 'mountain-white.png'

    for (key, file) in CUBE_FILE_NAMES.items():
        CUBE_FILE_NAMES[key] =os.path.join(_script_home, 'pictures', file)


class CanvasConfig:
    # Canvas x-y dimensions in pixels
    RATIO = 1
    HEIGHT = float(600)
    WIDTH = float(HEIGHT*RATIO)

    # Canvas x-y dimensions in hexagon units
    NX = 9 + 2
    NY = 9

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
    CUBE_LINE_WIDTH = float(0.02*HEXA_SIDE)
    HEXA_LINE_WIDTH = float(0.01*HEXA_SIDE)

    # Origin of the orthonormal x-y frame and the oblic u-v frame
    ORIGIN = np.array((WIDTH/2, HEIGHT/2))

    # Unit vectors of the orthonormal x-y frame
    UNIT_X = np.array((1, 0))
    UNIT_Y = np.array((0, -1))

    # Unit vectors of the oblic u-v frame
    UNIT_U = UNIT_X
    UNIT_V = math.cos(HEXA_SIDE_ANGLE)*UNIT_X + math.sin(HEXA_SIDE_ANGLE)*UNIT_Y


class CubeConfig:
    # File path containing the icon to be displayed in the title bar of Jersi GUI

    CUBE_PHOTOS = None



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

        for hexagon in jersi_certu.Hexagon.all:

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


class GameGui(tk.Frame):


    def __init__(self):

        self.__face_drawers = dict()
        self.__face_drawers[jersi_certu.CubeSort.FOUL] = self.__draw_foul_face
        self.__face_drawers[jersi_certu.CubeSort.KING] = self.__draw_king_face
        self.__face_drawers[jersi_certu.CubeSort.PAPER] = self.__draw_paper_face
        self.__face_drawers[jersi_certu.CubeSort.ROCK] = self.__draw_rock_face
        self.__face_drawers[jersi_certu.CubeSort.SCISSORS] = self.__draw_scissors_face
        self.__face_drawers[jersi_certu.CubeSort.MOUNTAIN] = self.__draw_mountain_face
        self.__face_drawers[jersi_certu.CubeSort.WISE] = self.__draw_wise_face


        # Draw faces of cubes ?
        # If 'False' the just display letter representing the sort of the cube
        self.__draw_cube_faces = False

        # Draw reserve ?
        self.__draw_reserve = True

        self.__game_started = False
        self.__game = None
        self.__jersi_state = jersi_certu.JersiState()

        self.__use_white_ia = True
        self.__use_black_ia = True

        self.__master = tk.Tk()

        tk.Tk.iconbitmap(self.__master, default=AppConfig.ICON_FILE)
        tk.Tk.wm_title(self.__master, "jersi-certu : for evaluating AI agents and the jersi rules engine")

        if False:
            # an attempt for increasing the canvas rendering, ... that does not work !
            self.__master.tk.call('tk', 'scaling', '-displayof', '.', 0.75)

        self.__create_widgets()
        self.__draw_state()

        if self.__game_started:
            self.__variable_log.set("jersi started")
        else:
            self.__variable_log.set("jersi stopped")

        self.__master.mainloop()


    def __create_widgets(self):

        searcher_catalog_names = list(jersi_certu.searcher_catalog.keys())
        searcher_catalog_names.sort()
        searcher_catalog_names_width = max(map(len, searcher_catalog_names))

        self.__canvas = tk.Canvas(self.__master,
                                height=CanvasConfig.HEIGHT,
                                width=CanvasConfig.WIDTH)

        self.__progressbar = ttk.Progressbar(self.__master,
                                            orient=tk.HORIZONTAL,
                                            length=300,
                                            maximum=100,
                                            mode='determinate')

        self.__variable_log = tk.StringVar()
        self.__label_log = tk.Label(self.__master,
                                  textvariable=self.__variable_log,
                                  width=90,
                                  foreground='red')

        self.__label_white_player = tk.Label(self.__master, text='White')

        self.__variable_white_ia = tk.BooleanVar()
        self.__variable_white_ia.set(self.__use_white_ia)
        self.__button_white_ia = ttk.Checkbutton (self.__master,
                                       text='IA',
                                       command=self.__command_toggle_white_ia,
                                       variable=self.__variable_white_ia)

        self.__variable_white_player = tk.StringVar()
        self.__combobox_white_player = ttk.Combobox(self.__master,
                                                  width=searcher_catalog_names_width,
                                                  textvariable=self.__variable_white_player,
                                                  values=searcher_catalog_names)
        self.__combobox_white_player.config(state="readonly")
        self.__variable_white_player.set(searcher_catalog_names[0])


        self.__label_black_player = tk.Label(self.__master, text='Black')

        self.__variable_black_ia = tk.BooleanVar()
        self.__variable_black_ia.set(self.__use_black_ia)
        self.__button_black_ia = ttk.Checkbutton (self.__master,
                                       text='IA',
                                       command=self.__command_toggle_black_ia,
                                       variable=self.__variable_black_ia)

        self.__variable_black_player = tk.StringVar()
        self.__combobox_black_player = ttk.Combobox(self.__master,
                                                  width=searcher_catalog_names_width,
                                                  textvariable=self.__variable_black_player,
                                                  values=searcher_catalog_names)
        self.__combobox_black_player.config(state="readonly")
        self.__variable_black_player.set(searcher_catalog_names[0])

        self.__variable_face = tk.BooleanVar()
        self.__variable_face.set(self.__draw_cube_faces)
        self.__button_face = ttk.Checkbutton (self.__master,
                                       text='Icon faces',
                                       command=self.__command_toggle_face,
                                       variable=self.__variable_face)

        self.__variable_reserve = tk.BooleanVar()
        self.__variable_reserve.set(self.__draw_reserve)
        self.__button_reserve = ttk.Checkbutton (self.__master,
                                       text='Reserve',
                                       command=self.__command_toggle_reserve,
                                       variable=self.__variable_reserve)

        self.__button_quit = ttk.Button(self.__master,
                                 text='Quit',
                                 command=self.__master.destroy)

        self.__button_start_stop = ttk.Button(self.__master,
                                  text='Start',
                                  command=self.__command_start_stop)

        # row 0

        self.__button_start_stop.grid(row=0, column=0, sticky=tk.W)

        self.__label_white_player.grid(row=0, column=1)
        self.__button_white_ia.grid(row=0, column=2)
        self.__combobox_white_player.grid(row=0, column=3)

        self.__label_black_player.grid(row=0, column=4)
        self.__button_black_ia.grid(row=0, column=5)
        self.__combobox_black_player.grid(row=0, column=6)

        self.__button_face.grid(row=0, column=7)
        self.__button_reserve.grid(row=0, column=8)

        self.__button_quit.grid(row=0, column=9, sticky=tk.E)

        # row 1
        self.__progressbar.grid(row=1, columnspan=10)

        # row 2
        self.__label_log.grid(row=2, columnspan=10)

        # row 3
        self.__canvas.grid(row=3, columnspan=10)


    def __command_toggle_white_ia(self):
        self.__variable_log.set("toggle white IA ...")

        self.__use_white_ia = self.__variable_white_ia.get()

        if self.__use_white_ia:
           self.__combobox_white_player.config(state="readonly")
        else:
           self.__combobox_white_player.config(state="disabled")

        self.__variable_log.set("toggle white IA done")


    def __command_toggle_black_ia(self):
        self.__variable_log.set("toggle black IA ...")

        self.__use_black_ia = self.__variable_black_ia.get()

        if self.__use_black_ia:
           self.__combobox_black_player.config(state="readonly")
        else:
           self.__combobox_black_player.config(state="disabled")

        self.__variable_log.set("toggle black IA done")


    def __command_toggle_face(self):
        self.__variable_log.set("toggle face ...")

        self.__draw_cube_faces = self.__variable_face.get()
        self.__draw_state()

        self.__variable_log.set("toggle face done")


    def __command_toggle_reserve(self):
        self.__variable_log.set("toggle reserve ...")

        self.__draw_reserve = self.__variable_reserve.get()
        self.__draw_state()

        self.__variable_log.set("toggle reserve done")


    def __command_start_stop(self):

        self.__game_started = not self.__game_started

        if self.__game_started:

           self.__combobox_white_player.config(state="disabled")
           self.__combobox_black_player.config(state="disabled")

           self.__game = jersi_certu.Game()
           self.__game.set_white_player(self.__variable_white_player.get())
           self.__game.set_black_player(self.__variable_black_player.get())
           self.__game.start()

           self.__jersi_state = self.__game.jersi_state
           self.__draw_state()

           self.__variable_log.set("jersi started")
           self.__button_start_stop.configure(text="Stop")

           self.__canvas.after(1000, self.__next_step)

        else:
           self.__combobox_white_player.config(state="readonly")
           self.__combobox_black_player.config(state="readonly")

           self.__variable_log.set("jersi stopped")
           self.__button_start_stop.configure(text="Start")


    def __next_step(self):

        if self.__game.has_next_turn():

            self.__game.next_turn()
            self.__jersi_state = self.__game.jersi_state
            self.__draw_state()

            if self.__game_started:
                self.__canvas.after(1000, self.__next_step)
                self.__variable_log.set(self.__game.get_log())

        else:
           self.__combobox_white_player.config(state="readonly")
           self.__combobox_black_player.config(state="readonly")

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

        for hexagon in jersi_certu.Hexagon.all:

            top_index = hexagon_top[hexagon.index]
            bottom_index = hexagon_bottom[hexagon.index]

            if top_index != jersi_certu.Null.CUBE and bottom_index != jersi_certu.Null.CUBE:

                top = jersi_certu.Cube.all[top_index]
                bottom = jersi_certu.Cube.all[bottom_index]

                self.__draw_cube(name=hexagon.name, config=CubeLocation.TOP,
                               cube_color=top.player, cube_sort=top.sort, cube_label=top.label)

                self.__draw_cube(name=hexagon.name, config=CubeLocation.BOTTOM,
                               cube_color=bottom.player, cube_sort=bottom.sort, cube_label=bottom.label)

            elif top_index != jersi_certu.Null.CUBE:

                top = jersi_certu.Cube.all[top_index]

                self.__draw_cube(name=hexagon.name, config=CubeLocation.MIDDLE,
                               cube_color=top.player, cube_sort=top.sort, cube_label=top.label)

            elif bottom_index != jersi_certu.Null.CUBE:

                bottom = jersi_certu.Cube.all[bottom_index]

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

        if CubeConfig.CUBE_PHOTOS is None:

            CubeConfig.CUBE_PHOTOS = {}

            for (key, file) in AppConfig.CUBE_FILE_NAMES.items():
                cube_photo = Image.open(AppConfig.CUBE_FILE_NAMES[key])
                cube_photo = cube_photo.resize((int(0.70*CanvasConfig.HEXA_SIDE), int(0.70*CanvasConfig.HEXA_SIDE)))
                cube_tk_photo = ImageTk.PhotoImage(cube_photo)
                CubeConfig.CUBE_PHOTOS[key] = cube_tk_photo

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


        if cube_color == jersi_certu.Player.BLACK:
            fill_color = CubeColor.BLACK.value
            face_color = CubeColor.WHITE.value

        elif cube_color == jersi_certu.Player.WHITE:
            fill_color = CubeColor.WHITE.value
            face_color = CubeColor.BLACK.value

        else:
            assert False


        line_color = ''

        cube_vertex_NW = cube_vertices[1]
        cube_vertex_SE = cube_vertices[3]

        self.__canvas.create_rectangle(*cube_vertex_NW, *cube_vertex_SE,
                                fill=fill_color,
                                outline=line_color)


        if True:
            cube_tk_photo = CubeConfig.CUBE_PHOTOS[(cube_color, cube_sort)]
            self.__canvas.create_image(cube_center[0], cube_center[1], image=cube_tk_photo, anchor=tk.CENTER)

        elif self.__draw_cube_faces:
            self.__face_drawers[cube_sort](cube_center, cube_vertices, face_color)

        else:
            face_font = font.Font(family=CanvasConfig.FONT_FAMILY, size=CanvasConfig.FONT_FACE_SIZE, weight='bold')

            self.__canvas.create_text(*cube_center,
                               text=cube_label,
                               justify=tk.CENTER,
                               font=face_font,
                               fill=face_color)

    def __draw_king_face(self, cube_center, cube_vertices, face_color):
        pass


    def __draw_foul_face(self, cube_center, cube_vertices, face_color):


        def rotate_90_degrees(vector):
            """Rotate 90 degrees counter clock"""
            projection_x = np.inner(vector, CanvasConfig.UNIT_X)
            projection_y = np.inner(vector, CanvasConfig.UNIT_Y)
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

        cube_side = np.linalg.norm(face_vertex_NW - face_vertex_NE)

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

    game_gui = GameGui()
    print("Before mainloop")
    #game_gui.mainloop()
    print("After mainloop")

    print("Bye")


if __name__ == "__main__":
    main()