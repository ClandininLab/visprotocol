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
         dlpc350_object.set_current(red=0, green=0, blue=0.1)
         dlpc350_object.pattern_mode(fps=120, red=False, blue=True, green=False)
    if len(dlpc350_objects) == 0:
        print('No lightcrafters detected! Try sudo')


    # Define screen(s) for the rig. Units in meters
    # Fly is at (0, 0, 0), fly looking down +y axis. Top of the screen is near z=0
    z_bottom = -8.2e-2 # m
    x_left = -5e-2
    x_right = +5e-2
    y_forward = +5e-2
    y_back = -1e-2

    def getAODscreen():
        return SubScreen(pa=(x_left, y_back, z_bottom), pb=(x_right, y_back, z_bottom), pc=(x_left, y_forward, 0), viewport_ll=(-1.0, -1.0), viewport_width=2.0, viewport_height=2.0)

    AODscope_screen = Screen(subscreens=[getAODscreen()], id=1, fullscreen=True, vsync=True, square_size=(0.5, 0.5), square_loc=(-1.00, -1.00), name='AOD', horizontal_flip=True)

    aux_screen = Screen(subscreens=[getAODscreen()], id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)


    screens = [AODscope_screen, aux_screen]
    port = 60629
    host = ''

    #draw_screens(AODscope_screen)
    plt.show()

    manager =  StimServer(screens=screens, host=host, port=port, auto_stop=False)

    manager.black_corner_square()
    manager.set_idle_background(0)

    manager.loop()

if __name__ == '__main__':
    main()
