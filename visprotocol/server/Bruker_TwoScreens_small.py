#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.screen import Screen, SubScreen
from flystim.draw import draw_screens
from flystim.stim_server import StimServer
from flystim.dlpc350 import make_dlpc350_objects
from math import pi
import matplotlib.pyplot as plt

def main():
    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.set_current(red=0, green = 0, blue = 1.0)
         dlpc350_object.pattern_mode(fps=120)
         dlpc350_object.pattern_mode(fps=120)

    # Define screen(s) for the rig. Units in meters
    # Fly is at (0, 0, 0), fly looking down +y axis. Top of the screen is at z=0
    z_bottom = -12.13e-2 #m
    x_left = -7.99e-2
    x_right = +7.99e-2
    y_forward = +7.17e-2
    y_back = 1.0e-2

    def getBrukerLeft():
        return SubScreen(pa=(x_left, y_back, z_bottom), pb=(0, y_forward, z_bottom), pc=(x_left, y_back, 0), viewport_ll=(-0.60, -1.0), viewport_width=1.0, viewport_height=2)

    def getBrukerRight():
        return SubScreen(pa=(0, y_forward, z_bottom), pb=(x_right, y_back, z_bottom), pc=(0, y_forward, 0), viewport_ll=(-0.30, -1.0), viewport_width=1.3, viewport_height=2)

    def getAux():
        return SubScreen(pa=(x_left, y_back, z_bottom), pb=(0, y_forward, z_bottom), pc=(x_left, y_back, 0))

    bruker_left_screen = Screen(subscreens=[getBrukerLeft()], id=1, fullscreen=True, vsync=True, square_size=(0.18, 0.25), square_loc=(0.78, -0.86), name='Left', horizontal_flip=True)

    bruker_right_screen = Screen(subscreens=[getBrukerRight()], id=2, fullscreen=True, vsync=True, square_size=(0.18, 0.25), square_loc=(-0.88, -0.92), name='Right', horizontal_flip=True)

    aux_screen = Screen(subscreens=[getBrukerRight()], id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)

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
