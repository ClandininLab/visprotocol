#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.screen import Screen
from flystim.draw import draw_screens
from flystim.stim_server import StimServer
from flystim.dlpc350 import make_dlpc350_objects
from math import pi
import matplotlib.pyplot as plt

def main():
    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.pattern_mode(fps=120)
         dlpc350_object.pattern_mode(fps=120)

    # Define screen(s) for the rig. Units in meters
    # Fly is at (0, 0, 0), fly looking down +y axis. Top of the screen is at z=0
    z_bottom = -12.13e-2 #m
    x_left = -7.99e-2
    x_right = +7.99e-2
    y_forward = +7.17e-2
    y_back = -0.8e-2

    # LEFT SCREEN
    left_pa = ((-0.55, -1.0), (x_left, y_back, z_bottom))
    left_pb = ((+0.65, -1.0), (0, y_forward, z_bottom))
    left_pc = ((-0.55, +1.0), (x_left, y_back, 0))
    left_p4 = ((+0.65, +1.0), (0, y_forward, 0))

    left_tri = Screen.quad_to_tri_list(left_pa, left_pb, left_pc, left_p4)

    bruker_left_screen = Screen(tri_list=left_tri, id=0, fullscreen=False, vsync=True, square_size=(0.18, 0.25), square_loc=(0.78, -0.86), name='Left', horizontal_flip=True)

    # RIGHT SCREEN
    right_pa = ((-0.57, -1.0), (0, y_forward, z_bottom))
    right_pb = ((+0.60, -1.0), (x_right, y_back, z_bottom))
    right_pc = ((-0.54, +0.96), (0, y_forward, 0))
    right_p4 = ((+0.62, +0.94), (x_right, y_back, 0))

    right_tri = Screen.quad_to_tri_list(right_pa, right_pb, right_pc, right_p4)

    bruker_right_screen = Screen(tri_list=right_tri, id=0, fullscreen=False, vsync=True, square_size=(0.18, 0.25), square_loc=(-0.88, -0.92), name='Right', horizontal_flip=True)

    aux_screen = Screen(tri_list=left_tri, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)

    draw_screens([bruker_left_screen, bruker_right_screen])
    plt.show()

    screens = [bruker_left_screen, bruker_right_screen, aux_screen]
    port = 60629
    host = ''

    manager = StimServer(screens=screens, host=host, port=port, auto_stop=False)

    manager.black_corner_square()
    manager.set_idle_background(0)

    manager.loop()

if __name__ == '__main__':
    main()
