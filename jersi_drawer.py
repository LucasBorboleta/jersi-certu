# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 15:03:54 2020

@author: Lucas Borboleta
"""

_COPYRIGHT_AND_LICENSE = """
JERSI-DRAWER draws a vectorial picture of JERSI boardgame state from an abstract state.

Copyright (C) 2020 Lucas Borboleta (lucas.borboleta@free.fr).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""


import enum
import math
import os
import sys

JERSI_HOME = os.path.abspath(os.path.dirname(__file__))
sys.path.append(JERSI_HOME)

import jersi_certu

import tkinter as tk
from tkinter import font
from tkinter import ttk

import numpy as np


class JersiError(Exception):
    """Customized exception dedicated to all classes of JERSI"""

    def __init__(self, message):
        """JERSI exception records an explaining text message"""
        Exception.__init__(self)
        self.message = message


def jersi_assert(condition, message):
    """If condition fails (is False) then raise a JERSI exception
    together with the explaining message"""
    if not condition:
        raise JersiError(message)


# File path containing the icon to be displayed in the title bar of Jersi GUI
JERSI_ICON_FILE = os.path.join(JERSI_HOME, 'jersi.ico')

# Canvas x-y dimensions in pixels
CANVAS_RATIO = 1
CANVAS_HEIGHT = 600
CANVAS_WIDTH = int(CANVAS_HEIGHT * CANVAS_RATIO)

# Canvas x-y dimensions in hexagon units
NX = 9 + 2
NY = 9

# Hexagon geometrical data
HEXA_VERTEX_COUNT = 6
HEXA_SIDE_ANGLE = 2*math.pi/HEXA_VERTEX_COUNT
HEXA_WIDTH = min(CANVAS_HEIGHT, CANVAS_WIDTH) / max(NX, NY)
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
CUBE_LINE_WIDTH = int(0.05*HEXA_SIDE)
HEXA_LINE_WIDTH = int(0.02*HEXA_SIDE)

# Origin of the orthonormal x-y frame and the oblic u-v frame
ORIGIN = np.array((CANVAS_WIDTH/2, CANVAS_HEIGHT/2))

# Unit vectors of the orthonormal x-y frame
UNIT_X = np.array((1, 0))
UNIT_Y = np.array((0, -1))

# Unit vectors of the oblic u-v frame
UNIT_U = UNIT_X
UNIT_V = math.cos(HEXA_SIDE_ANGLE)*UNIT_X + math.sin(HEXA_SIDE_ANGLE)*UNIT_Y


def rgb_color_as_hexadecimal(rgb):
    (red, green, blue) = rgb
    return '#%02x%02x%02x' % (red, green, blue)


class HexagonColor(enum.Enum):
    INNER = rgb_color_as_hexadecimal((166, 109, 60))
    MAIN = rgb_color_as_hexadecimal((242, 202, 128))
    OUTER = rgb_color_as_hexadecimal((191, 89, 52))
    RESERVE = rgb_color_as_hexadecimal((191, 184, 180))


class CubeColor(enum.Enum):
    BLACK = enum.auto()
    WHITE = enum.auto()


class CubeConfig(enum.Enum):
    BOTTOM = enum.auto()
    SINGLE = enum.auto()
    TOP = enum.auto()


class CubeSort(enum.Enum):
    KING = 'K'
    FOUL = 'F'
    PAPER = 'P'
    ROCK = 'R'
    SCISSORS = 'S'
    MOUNTAIN = 'M'
    WISE = 'W'


def make_cube_colored_sorts():

    CUBE_COLORED_SORTS = dict()

    CUBE_COLORED_SORTS['K'] = (CubeSort.KING, CubeColor.WHITE)
    CUBE_COLORED_SORTS['F'] = (CubeSort.FOUL, CubeColor.WHITE)
    CUBE_COLORED_SORTS['R'] = (CubeSort.ROCK, CubeColor.WHITE)
    CUBE_COLORED_SORTS['P'] = (CubeSort.PAPER, CubeColor.WHITE)
    CUBE_COLORED_SORTS['S'] = (CubeSort.SCISSORS, CubeColor.WHITE)
    CUBE_COLORED_SORTS['M'] = (CubeSort.MOUNTAIN, CubeColor.WHITE)
    CUBE_COLORED_SORTS['W'] = (CubeSort.WISE, CubeColor.WHITE)

    CUBE_COLORED_SORTS['k'] = (CubeSort.KING, CubeColor.BLACK)
    CUBE_COLORED_SORTS['f'] = (CubeSort.FOUL, CubeColor.BLACK)
    CUBE_COLORED_SORTS['r'] = (CubeSort.ROCK, CubeColor.BLACK)
    CUBE_COLORED_SORTS['p'] = (CubeSort.PAPER, CubeColor.BLACK)
    CUBE_COLORED_SORTS['s'] = (CubeSort.SCISSORS, CubeColor.BLACK)
    CUBE_COLORED_SORTS['m'] = (CubeSort.MOUNTAIN, CubeColor.BLACK)
    CUBE_COLORED_SORTS['w'] = (CubeSort.WISE, CubeColor.BLACK)

    return CUBE_COLORED_SORTS

CUBE_COLORED_SORTS = make_cube_colored_sorts()



class Hexagon:

    alls = dict()

    def __init__(self, label, position_uv, color, in_reserve=False, reserve_shift=None):
        jersi_assert(in_reserve == (reserve_shift is not None),
                     "in_reserve and reserve_shift not consisten for label '%s'" % label)

        self.label = label
        self.position_uv = position_uv
        self.color = color
        self.in_reserve = in_reserve
        self.reserve_shift = reserve_shift

    @staticmethod
    def add(label, position_uv, color, in_reserve=False, reserve_shift=None):
        jersi_assert(label not in Hexagon.alls,
                     "no hexagon with label '%s'" % label)

        Hexagon.alls[label] = Hexagon(label, position_uv, color, in_reserve, reserve_shift)

    @staticmethod
    def create_all_hexagons():

        # Row "a"
        Hexagon.add('a1', (-1, -4), HexagonColor.OUTER.value)
        Hexagon.add('a2', (-0, -4), HexagonColor.OUTER.value)
        Hexagon.add('a3', (1, -4), HexagonColor.OUTER.value)
        Hexagon.add('a4', (2, -4), HexagonColor.OUTER.value)
        Hexagon.add('a5', (3, -4), HexagonColor.OUTER.value)
        Hexagon.add('a6', (4, -4), HexagonColor.OUTER.value)
        Hexagon.add('a7', (5, -4), HexagonColor.OUTER.value)

        Hexagon.add('a', (6, -4), HexagonColor.RESERVE.value, in_reserve=True,
                    reserve_shift=0.75*HEXA_WIDTH*UNIT_X - HEXA_DELTA_Y*UNIT_Y)

        # Row "b"
        Hexagon.add('b1', (-2, -3), HexagonColor.OUTER.value)
        Hexagon.add('b2', (-1, -3), HexagonColor.MAIN.value)
        Hexagon.add('b3', (0, -3), HexagonColor.MAIN.value)
        Hexagon.add('b4', (1, -3), HexagonColor.MAIN.value)
        Hexagon.add('b5', (2, -3), HexagonColor.MAIN.value)
        Hexagon.add('b6', (3, -3), HexagonColor.MAIN.value)
        Hexagon.add('b7', (4, -3), HexagonColor.MAIN.value)
        Hexagon.add('b8', (5, -3), HexagonColor.OUTER.value)

        Hexagon.add('b', (6, -3), HexagonColor.RESERVE.value, in_reserve=True,
                    reserve_shift=0.25*HEXA_WIDTH*UNIT_X)

        # Row "c"
        Hexagon.add('c1', (-2, -2), HexagonColor.OUTER.value)
        Hexagon.add('c2', (-1, -2), HexagonColor.MAIN.value)
        Hexagon.add('c3', (0, -2), HexagonColor.INNER.value)
        Hexagon.add('c4', (1, -2), HexagonColor.INNER.value)
        Hexagon.add('c5', (2, -2), HexagonColor.INNER.value)
        Hexagon.add('c6', (3, -2), HexagonColor.MAIN.value)
        Hexagon.add('c7', (4, -2), HexagonColor.OUTER.value)

        Hexagon.add('c', (5, -2), HexagonColor.RESERVE.value, in_reserve=True,
                    reserve_shift=0.75*HEXA_WIDTH*UNIT_X + HEXA_DELTA_Y*UNIT_Y)

        # Row "d"
        Hexagon.add('d1', (-3, -1), HexagonColor.OUTER.value)
        Hexagon.add('d2', (-2, -1), HexagonColor.MAIN.value)
        Hexagon.add('d3', (-1, -1), HexagonColor.INNER.value)
        Hexagon.add('d4', (0, -1), HexagonColor.MAIN.value)
        Hexagon.add('d5', (1, -1), HexagonColor.MAIN.value)
        Hexagon.add('d6', (2, -1), HexagonColor.INNER.value)
        Hexagon.add('d7', (3, -1), HexagonColor.MAIN.value)
        Hexagon.add('d8', (4, -1), HexagonColor.OUTER.value)

        # Row "e"
        Hexagon.add('e1', (-4, 0), HexagonColor.OUTER.value)
        Hexagon.add('e2', (-3, 0), HexagonColor.MAIN.value)
        Hexagon.add('e3', (-2, 0), HexagonColor.INNER.value)
        Hexagon.add('e4', (-1, 0), HexagonColor.MAIN.value)
        Hexagon.add('e5', (0, 0), HexagonColor.INNER.value)
        Hexagon.add('e6', (1, 0), HexagonColor.MAIN.value)
        Hexagon.add('e7', (2, 0), HexagonColor.INNER.value)
        Hexagon.add('e8', (3, 0), HexagonColor.MAIN.value)
        Hexagon.add('e9', (4, 0), HexagonColor.OUTER.value)

        # Row "f"
        Hexagon.add('f1', (-4, 1), HexagonColor.OUTER.value)
        Hexagon.add('f2', (-3, 1), HexagonColor.MAIN.value)
        Hexagon.add('f3', (-2, 1), HexagonColor.INNER.value)
        Hexagon.add('f4', (-1, 1), HexagonColor.MAIN.value)
        Hexagon.add('f5', (0, 1), HexagonColor.MAIN.value)
        Hexagon.add('f6', (1, 1), HexagonColor.INNER.value)
        Hexagon.add('f7', (2, 1), HexagonColor.MAIN.value)
        Hexagon.add('f8', (3, 1), HexagonColor.OUTER.value)

        # Row "g"
        Hexagon.add('g', (-5, 2), HexagonColor.RESERVE.value, in_reserve=True,
                                reserve_shift=-0.75*HEXA_WIDTH*UNIT_X - HEXA_DELTA_Y*UNIT_Y)

        Hexagon.add('g1', (-4, 2), HexagonColor.OUTER.value)
        Hexagon.add('g2', (-3, 2), HexagonColor.MAIN.value)
        Hexagon.add('g3', (-2, 2), HexagonColor.INNER.value)
        Hexagon.add('g4', (-1, 2), HexagonColor.INNER.value)
        Hexagon.add('g5', (0, 2), HexagonColor.INNER.value)
        Hexagon.add('g6', (1, 2), HexagonColor.MAIN.value)
        Hexagon.add('g7', (2, 2), HexagonColor.OUTER.value)

        # Row "h"
        Hexagon.add('h', (-6, 3), HexagonColor.RESERVE.value, in_reserve=True,
                                reserve_shift=-0.25*HEXA_WIDTH*UNIT_X)

        Hexagon.add('h1', (-5, 3), HexagonColor.OUTER.value)
        Hexagon.add('h2', (-4, 3), HexagonColor.MAIN.value)
        Hexagon.add('h3', (-3, 3), HexagonColor.MAIN.value)
        Hexagon.add('h4', (-2, 3), HexagonColor.MAIN.value)
        Hexagon.add('h5', (-1, 3), HexagonColor.MAIN.value)
        Hexagon.add('h6', (0, 3), HexagonColor.MAIN.value)
        Hexagon.add('h7', (1, 3), HexagonColor.MAIN.value)
        Hexagon.add('h8', (2, 3), HexagonColor.OUTER.value)

        # Row "i"
        Hexagon.add('i', (-6, 4), HexagonColor.RESERVE.value, in_reserve=True,
                                reserve_shift=-0.75*HEXA_WIDTH*UNIT_X + HEXA_DELTA_Y*UNIT_Y)

        Hexagon.add('i1', (-5, 4), HexagonColor.OUTER.value)
        Hexagon.add('i2', (-4, 4), HexagonColor.OUTER.value)
        Hexagon.add('i3', (-3, 4), HexagonColor.OUTER.value)
        Hexagon.add('i4', (-2, 4), HexagonColor.OUTER.value)
        Hexagon.add('i5', (-1, 4), HexagonColor.OUTER.value)
        Hexagon.add('i6', (0, 4), HexagonColor.OUTER.value)
        Hexagon.add('i7', (1, 4), HexagonColor.OUTER.value)

Hexagon.create_all_hexagons()


class JersiGui(tk.Frame):


    def __init__(self):

        self.face_drawers = dict()
        self.face_drawers[CubeSort.FOUL] = self.draw_foul_face
        self.face_drawers[CubeSort.KING] = self.draw_king_face
        self.face_drawers[CubeSort.PAPER] = self.draw_paper_face
        self.face_drawers[CubeSort.ROCK] = self.draw_rock_face
        self.face_drawers[CubeSort.SCISSORS] = self.draw_scissors_face
        self.face_drawers[CubeSort.MOUNTAIN] = self.draw_mountain_face
        self.face_drawers[CubeSort.WISE] = self.draw_wise_face


        # Draw faces of cubes ?
        # If 'False' the just display letter representing the sort of the cube
        self.draw_cube_faces = True

        # Draw reserve ?
        self.draw_reserve = True

        self.simulation_started = False
        self.simulation = None
        self.state = JersiState()

        self.master = tk.Tk()
        super().__init__(self.master)

        tk.Tk.iconbitmap(self.master, default=JERSI_ICON_FILE)
        tk.Tk.wm_title(self.master, "jersi-certu : for evaluating AI agents and efficiency of the jersi rules engine")

        self.create_widgets()

        self.draw_state()

        if self.simulation_started:
            self.variable_log.set("jersi started")
        else:
            self.variable_log.set("jersi stopped")


    def create_widgets(self):

        searcher_catalog_names = list(jersi_certu.searcher_catalog.keys())
        searcher_catalog_names.sort()
        searcher_catalog_names_width = max(map(len, searcher_catalog_names))

        self.canvas = tk.Canvas(self.master,
                                height=CANVAS_HEIGHT,
                                width=CANVAS_WIDTH)

        self.progressbar = ttk.Progressbar(self.master,
                                            orient=tk.HORIZONTAL,
                                            length=300,
                                            maximum=100,
                                            mode='determinate')

        self.variable_log = tk.StringVar()
        self.label_log = tk.Label(self.master,
                                  textvariable=self.variable_log,
                                  width=90,
                                  foreground='red')

        self.label_white_player = tk.Label(self.master, text='white')
        self.variable_white_player = tk.StringVar()
        self.combobox_white_player = ttk.Combobox(self.master,
                                                  width=searcher_catalog_names_width,
                                                  textvariable=self.variable_white_player,
                                                  values=searcher_catalog_names)
        self.combobox_white_player.config(state="readonly")
        self.variable_white_player.set(searcher_catalog_names[0])


        self.label_black_player = tk.Label(self.master, text='black')
        self.variable_black_player = tk.StringVar()
        self.combobox_black_player = ttk.Combobox(self.master,
                                                  width=searcher_catalog_names_width,
                                                  textvariable=self.variable_black_player,
                                                  values=searcher_catalog_names)
        self.combobox_black_player.config(state="readonly")
        self.variable_black_player.set(searcher_catalog_names[0])

        self.variable_face = tk.BooleanVar()
        self.variable_face.set(self.draw_cube_faces)
        self.button_face = ttk.Checkbutton (self.master,
                                       text='Icon faces',
                                       command=self.command_toggle_face,
                                       variable=self.variable_face)

        self.variable_reserve = tk.BooleanVar()
        self.variable_reserve.set(self.draw_reserve)
        self.button_reserve = ttk.Checkbutton (self.master,
                                       text='Reserve',
                                       command=self.command_toggle_reserve,
                                       variable=self.variable_reserve)

        self.button_quit = ttk.Button(self.master,
                                 text='Quit',
                                 command=self.master.destroy)

        self.button_start_stop = ttk.Button(self.master,
                                  text='Start',
                                  command=self.command_start_stop)

        # row 0

        self.button_start_stop.grid(row=0, column=0, sticky=tk.W)

        self.label_white_player.grid(row=0, column=1)
        self.combobox_white_player.grid(row=0, column=2)

        self.label_black_player.grid(row=0, column=3)
        self.combobox_black_player.grid(row=0, column=4)

        self.button_face.grid(row=0, column=5)
        self.button_reserve.grid(row=0, column=6)

        self.button_quit.grid(row=0, column=7, sticky=tk.E)

        # row 1
        self.progressbar.grid(row=1, columnspan=8)

        # row 2
        self.label_log.grid(row=2, columnspan=8)

        # row 3
        self.canvas.grid(row=3, columnspan=8)


    def command_toggle_face(self):
        self.variable_log.set("toggle face ...")

        self.draw_cube_faces = self.variable_face.get()
        self.draw_state()

        self.variable_log.set("toggle face done")


    def command_toggle_reserve(self):
        self.variable_log.set("toggle reserve ...")

        self.draw_reserve = self.variable_reserve.get()
        self.draw_state()

        self.variable_log.set("toggle reserve done")


    def command_start_stop(self):

        self.simulation_started = not self.simulation_started

        if self.simulation_started:

           self.combobox_white_player.config(state="disabled")
           self.combobox_black_player.config(state="disabled")

           self.simulation = jersi_certu.Simulation()
           self.simulation.set_white_player(self.variable_white_player.get())
           self.simulation.set_black_player(self.variable_black_player.get())
           self.simulation.start()

           self.state = JersiState(self.simulation)
           self.draw_state()

           self.variable_log.set("jersi started")
           self.button_start_stop.configure(text="Stop")

           self.canvas.after(1000, self.next_step)

        else:
           self.combobox_white_player.config(state="readonly")
           self.combobox_black_player.config(state="readonly")

           self.variable_log.set("jersi stopped")
           self.button_start_stop.configure(text="Start")


    def next_step(self):

        if self.simulation.has_next_turn():

            self.simulation.next_turn()
            self.state.update(self.simulation)
            self.draw_state()

            if self.simulation_started:
                self.canvas.after(1000, self.next_step)
                self.variable_log.set(self.simulation.get_log())

        else:
           self.combobox_white_player.config(state="readonly")
           self.combobox_black_player.config(state="readonly")

           self.simulation_started = False
           self.button_start_stop.configure(text="Start")


    def draw_king_face(self, cube_center, cube_vertices, face_color):
        pass


    def draw_foul_face(self, cube_center, cube_vertices, face_color):


        def rotate_90_degrees(vector):
            """Rotate 90 degrees counter clock"""
            projection_x = np.inner(vector, UNIT_X)
            projection_y = np.inner(vector, UNIT_Y)
            rotated_unit_x = UNIT_Y
            rotated_unit_y = -UNIT_X
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
        self.canvas.create_arc(*p1, *p2,
                          start=90,
                          extent=180,
                          fill='',
                          outline=face_color,
                          style=tk.ARC,
                          width=CUBE_LINE_WIDTH)

        (p1, p2) = square_for_circle_by_two_points(face_vertex_NC, face_vertex_SC)
        self.canvas.create_arc(*p1, *p2,
                          start=-90 - angle_epsilon,
                          extent=180 + angle_epsilon,
                          fill='',
                          outline=face_color,
                          style=tk.ARC,
                          width=CUBE_LINE_WIDTH)

        (p1, p2) = square_for_circle_by_two_points(face_vertex_NC, face_vertex_S)
        self.canvas.create_arc(*p1, *p2,
                          start=90 - angle_epsilon,
                          extent=180 + angle_epsilon,
                          fill='',
                          outline=face_color,
                          style=tk.ARC,
                          width=CUBE_LINE_WIDTH)

        (p1, p2) = square_for_circle_by_two_points(face_vertex_N, face_vertex_S)
        self.canvas.create_arc(*p1, *p2,
                          start=-90 - angle_epsilon,
                          extent=180 + 45 + angle_epsilon,
                          fill='',
                          outline=face_color,
                          style=tk.ARC,
                          width=CUBE_LINE_WIDTH)

        # >> canvas doesn't provide rounded capstype for arc
        # >> so let add one small circle at each edge of the spiral

        # add small circle at the inner edge of the spiral

        inner_edge_top = cube_center + CUBE_LINE_WIDTH*0.5*UNIT_Y
        edge_edge_bottom = cube_center - CUBE_LINE_WIDTH*0.5*UNIT_Y

        (p1, p2) = square_for_circle_by_two_points(inner_edge_top, edge_edge_bottom)
        self.canvas.create_oval(*p1, *p2,
                           fill=face_color,
                           outline='')

        # add small circle at the outer edge of the spiral

        outer_edge_middle = cube_center + cube_side/2*(UNIT_Y - UNIT_X)/math.sqrt(2)

        outer_edge_top = outer_edge_middle + CUBE_LINE_WIDTH*0.5*UNIT_Y
        outer_edge_bottom = outer_edge_middle - CUBE_LINE_WIDTH*0.5*UNIT_Y

        (p1, p2) = square_for_circle_by_two_points(outer_edge_top, outer_edge_bottom)
        self.canvas.create_oval(*p1, *p2,
                           fill=face_color,
                           outline='')


    def draw_paper_face(self, cube_center, cube_vertices, face_color):

        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        self.canvas.create_rectangle(*face_vertex_NW, *face_vertex_SE,
                                fill='',
                                outline=face_color,
                                width=CUBE_LINE_WIDTH)


    def draw_rock_face(self, cube_center, cube_vertices, face_color):

        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        self.canvas.create_oval(*face_vertex_NW, *face_vertex_SE,
                           fill='',
                           outline=face_color,
                           width=CUBE_LINE_WIDTH)


    def draw_scissors_face(self, cube_center, cube_vertices, face_color):

        face_vertex_NE = 0.5*cube_center + 0.5*cube_vertices[0]
        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SW = 0.5*cube_center + 0.5*cube_vertices[2]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        self.canvas.create_line(*face_vertex_NE, *face_vertex_SW,
                           fill=face_color,
                           width=CUBE_LINE_WIDTH,
                           capstyle=tk.ROUND)

        self.canvas.create_line(*face_vertex_NW, *face_vertex_SE,
                           fill=face_color,
                           width=CUBE_LINE_WIDTH,
                           capstyle=tk.ROUND)


    def draw_mountain_face(self, cube_center, cube_vertices, face_color):

        face_vertex_NE = 0.5*cube_center + 0.5*cube_vertices[0]
        face_vertex_NW = 0.5*cube_center + 0.5*cube_vertices[1]
        face_vertex_SW = 0.5*cube_center + 0.5*cube_vertices[2]
        face_vertex_SE = 0.5*cube_center + 0.5*cube_vertices[3]

        face_N = 0.5*(face_vertex_NW + face_vertex_NE)
        face_S = 0.5*(face_vertex_SW + face_vertex_SE)

        face_W = 0.5*(face_vertex_NW + face_vertex_SW)
        face_E = 0.5*(face_vertex_NE + face_vertex_SE)

        face_data = [*face_N, *face_W, *face_E]

        self.canvas.create_polygon(face_data,
                              fill='',
                              outline=face_color,
                              width=CUBE_LINE_WIDTH,
                              joinstyle=tk.ROUND)

        face_data = [*face_S, *face_W, *face_E]

        self.canvas.create_polygon(face_data,
                              fill='',
                              outline=face_color,
                              width=CUBE_LINE_WIDTH,
                              joinstyle=tk.ROUND)


    def draw_wise_face(self, cube_center, cube_vertices, face_color):

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

        self.canvas.create_polygon(wise_data,
                              fill='',
                              outline=face_color,
                              width=CUBE_LINE_WIDTH,
                              joinstyle=tk.ROUND,
                              smooth=True)


    def draw_all_hexagons(self):

        for (_, hexagon) in Hexagon.alls.items():
            self.draw_hexagon(position_uv=hexagon.position_uv,
                         fill_color=hexagon.color,
                         label=hexagon.label,
                         in_reserve=hexagon.in_reserve,
                         reserve_shift=hexagon.reserve_shift)


    def draw_hexagon(self, position_uv, fill_color='', line_color='black',
                     label='', in_reserve=False, reserve_shift=None):

        if in_reserve and not self.draw_reserve:
            return

        (u, v) = position_uv

        hexagon_center = ORIGIN + HEXA_WIDTH*(u*UNIT_U + v*UNIT_V)

        if reserve_shift is not None:
            hexagon_center = hexagon_center + reserve_shift

        hexagon_data = list()

        for vertex_index in range(HEXA_VERTEX_COUNT):
            vertex_angle = (1/2 + vertex_index)*HEXA_SIDE_ANGLE

            hexagon_vertex = hexagon_center
            hexagon_vertex = hexagon_vertex + HEXA_SIDE*math.cos(vertex_angle)*UNIT_X
            hexagon_vertex = hexagon_vertex + HEXA_SIDE*math.sin(vertex_angle)*UNIT_Y

            hexagon_data.append(hexagon_vertex[0])
            hexagon_data.append(hexagon_vertex[1])

            if vertex_index == 3:
                label_position = hexagon_vertex + 0.25*HEXA_SIDE*(UNIT_X + 0.75*UNIT_Y)


        if in_reserve:
            polygon_line_color = ''
        else:
            polygon_line_color = line_color

        self.canvas.create_polygon(hexagon_data,
                              fill=fill_color,
                              outline=polygon_line_color,
                              width=HEXA_LINE_WIDTH,
                              joinstyle=tk.MITER)

        if label and not in_reserve:
            label_font = font.Font(family=FONT_FAMILY, size=FONT_LABEL_SIZE, weight='bold')

            self.canvas.create_text(*label_position, text=label, justify=tk.CENTER, font=label_font)


    def draw_cube(self, key, config, color, cube_sort=None):

        hexagon = Hexagon.alls[key]

        if hexagon.in_reserve and not self.draw_reserve:
            return

        (u, v) = hexagon.position_uv

        hexagon_center = ORIGIN + HEXA_WIDTH*(u*UNIT_U + v*UNIT_V)

        if hexagon.reserve_shift is not None:
            hexagon_center = hexagon_center + hexagon.reserve_shift

        cube_vertices = list()

        for vertex_index in range(CUBE_VERTEX_COUNT):
            vertex_angle = (1/2 + vertex_index)*CUBE_SIDE_ANGLE

            if config == CubeConfig.SINGLE:
                cube_center = hexagon_center

            elif config == CubeConfig.BOTTOM:
                cube_center = hexagon_center - 0.40*HEXA_SIDE*UNIT_Y

            elif config == CubeConfig.TOP:
                cube_center = hexagon_center + 0.40*HEXA_SIDE*UNIT_Y

            cube_vertex = cube_center
            cube_vertex = cube_vertex + 0.5*HEXA_SIDE*math.cos(vertex_angle)*UNIT_X
            cube_vertex = cube_vertex + 0.5*HEXA_SIDE*math.sin(vertex_angle)*UNIT_Y

            cube_vertices.append(cube_vertex)


        if color == CubeColor.BLACK:
            fill_color = 'black'
            face_color = 'white'
            str_transformation = str.lower

        elif color == CubeColor.WHITE:
            fill_color = 'white'
            face_color = 'black'
            str_transformation = str.upper

        else:
            jersi_assert(False, "not a CubeColor '%s'" % color)


        line_color = ''

        cube_vertex_NW = cube_vertices[1]
        cube_vertex_SE = cube_vertices[3]

        self.canvas.create_rectangle(*cube_vertex_NW, *cube_vertex_SE,
                                fill=fill_color,
                                outline=line_color)

        if cube_sort is not None:

            if self.draw_cube_faces:
                self.face_drawers[cube_sort](cube_center, cube_vertices, face_color)

            else:
                face_font = font.Font(family=FONT_FAMILY, size=FONT_FACE_SIZE, weight='bold')

                self.canvas.create_text(*cube_center,
                                   text=str_transformation(cube_sort.value),
                                   justify=tk.CENTER,
                                   font=face_font,
                                   fill=face_color)


    def draw_state(self):

        self.canvas.delete('all')

        self.draw_all_hexagons()

        for (position_label, position_state) in self.state.hex_content.items():

            if position_state[1] is not None:

                (cube_sort, cube_color) = position_state[1]
                self.draw_cube(key=position_label, config=CubeConfig.TOP,
                          color=cube_color, cube_sort=cube_sort)

                (cube_sort, cube_color) = position_state[0]
                self.draw_cube(key=position_label, config=CubeConfig.BOTTOM,
                          color=cube_color, cube_sort=cube_sort)

            elif position_state[0] is not None:

                (cube_sort, cube_color) = position_state[0]
                self.draw_cube(key=position_label, config=CubeConfig.SINGLE,
                          color=cube_color, cube_sort=cube_sort)

            else:
                pass


class JersiState:
    # State of the board with enough information for drawing


    def __init__(self, simulation=None):
        self.hex_content = None
        self.make_empty_hexagons()

        if simulation is not None:
            self.update(simulation)


    def make_empty_hexagons(self):
        if self.hex_content is None:
            self.hex_content = dict()

        for (_, hexagon) in Hexagon.alls.items():
            self.hex_content[hexagon.label] = [None, None]


    def update(self, simulation):
        self.make_empty_hexagons()

        for hex_index in jersi_certu.constHex.codomain:

            hex_label = jersi_certu.constHex.domain[hex_index]

            if simulation.js.hex_status[hex_index] == jersi_certu.TypeHexStatus.has_no_cube:
                pass

            elif simulation.js.hex_status[hex_index] == jersi_certu.TypeHexStatus.has_one_cube:
                bottom_cube_index = simulation.js.hex_bottom[hex_index]
                bottom_cube_csort_index = jersi_certu.constCube.csort[bottom_cube_index]
                bottom_cube_label = jersi_certu.TypeCubeColoredSort.domain[bottom_cube_csort_index]

                self.set_cube_at_position(hex_label, bottom_cube_label)

            elif simulation.js.hex_status[hex_index] == jersi_certu.TypeHexStatus.has_two_cubes:
                bottom_cube_index = simulation.js.hex_bottom[hex_index]
                bottom_cube_csort_index = jersi_certu.constCube.csort[bottom_cube_index]
                bottom_cube_label = jersi_certu.TypeCubeColoredSort.domain[bottom_cube_csort_index]

                top_cube_index = simulation.js.hex_top[hex_index]
                top_cube_csort_index = jersi_certu.constCube.csort[top_cube_index]
                top_cube_label = jersi_certu.TypeCubeColoredSort.domain[top_cube_csort_index]

                self.set_cube_at_position(hex_label, bottom_cube_label)
                self.set_cube_at_position(hex_label, top_cube_label)

            else:
                assert False


        # white and black reserves

        cube_reserved_selection = (simulation.js.cube_status == jersi_certu.TypeCubeStatus.reserved)

        white_cube_selection = (jersi_certu.constCube.color == jersi_certu.TypeCubeColor.white)
        black_cube_selection = (jersi_certu.constCube.color == jersi_certu.TypeCubeColor.black)

        mountain_cube_selection = (jersi_certu.constCube.sort == jersi_certu.TypeCubeSort.mountain)
        wise_cube_selection = (jersi_certu.constCube.sort == jersi_certu.TypeCubeSort.wise)

        # white reserve

        white_mountain_hex_labels = ['a', 'a', 'b', 'b']
        white_wise_hex_labels =['c', 'c']

        white_wise_indices = jersi_certu.constCube.codomain[cube_reserved_selection &
                                                                white_cube_selection
                                                                & wise_cube_selection]

        white_wise_labels = jersi_certu.TypeCubeColoredSort.domain[jersi_certu.constCube.csort[white_wise_indices]]

        wise_wise_count = white_wise_labels.size
        for (hex_label, wise_label) in zip(white_wise_hex_labels[:wise_wise_count], white_wise_labels):
            self.set_cube_at_position(hex_label, wise_label)

        white_mountain_indices = jersi_certu.constCube.codomain[cube_reserved_selection &
                                                                white_cube_selection
                                                                & mountain_cube_selection]

        white_mountain_labels = jersi_certu.TypeCubeColoredSort.domain[jersi_certu.constCube.csort[white_mountain_indices]]

        mountain_wise_count = white_mountain_labels.size
        for (hex_label, mountain_label) in zip(white_mountain_hex_labels[:mountain_wise_count], white_mountain_labels):
            self.set_cube_at_position(hex_label, mountain_label)


        # black reserve

        black_mountain_hex_labels = ['i', 'i', 'h', 'h']
        black_wise_hex_labels =['g', 'g']

        black_wise_indices = jersi_certu.constCube.codomain[cube_reserved_selection &
                                                                black_cube_selection
                                                                & wise_cube_selection]

        black_wise_labels = jersi_certu.TypeCubeColoredSort.domain[jersi_certu.constCube.csort[black_wise_indices]]

        wise_wise_count = black_wise_labels.size
        for (hex_label, wise_label) in zip(black_wise_hex_labels[:wise_wise_count], black_wise_labels):
            self.set_cube_at_position(hex_label, wise_label)

        black_mountain_indices = jersi_certu.constCube.codomain[cube_reserved_selection &
                                                                black_cube_selection
                                                                & mountain_cube_selection]

        black_mountain_labels = jersi_certu.TypeCubeColoredSort.domain[jersi_certu.constCube.csort[black_mountain_indices]]

        mountain_wise_count = black_mountain_labels.size
        for (hex_label, mountain_label) in zip(black_mountain_hex_labels[:mountain_wise_count], black_mountain_labels):
            self.set_cube_at_position(hex_label, mountain_label)


    def set_cube_at_position(self, position_label, cube_label):

        jersi_assert(position_label in Hexagon.alls,
                     "no hexagon at label '%s'" % position_label)


        jersi_assert(position_label in Hexagon.alls,
                     "no cube colored sort '%s'" % cube_label)

        if self.hex_content[position_label][0] is None:
            self.hex_content[position_label][0] = CUBE_COLORED_SORTS[cube_label]

        elif self.hex_content[position_label][1] is None:
            self.hex_content[position_label][1] = CUBE_COLORED_SORTS[cube_label]

        else:
            raise("No room for cube '%s' at position '%s' !!!" % (cube_label, position_label))


def main():
    print("Hello")

    print(_COPYRIGHT_AND_LICENSE)

    jersi_gui = JersiGui()
    jersi_gui.mainloop()

    print("Bye")


if __name__ == "__main__":
    main()