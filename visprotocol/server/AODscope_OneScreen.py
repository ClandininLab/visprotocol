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
         dlpc350_object.set_current(red=0, green = 0, blue = 0.1)
         dlpc350_object.pattern_mode(fps=120, red=True, blue=True, green=False)
    if len(dlpc350_objects) == 0:
        print('No lightcrafters detected! Try sudo')

    # Define screen(s) for the rig. Units in meters
    # Define coordinates s.t. screen is parallel to the YZ plane and fly is at (0,0,0)
    pt2 = ((1.0, -1.0), (20.1e-3, 46.3e-3, -82.9e-3))
    pt1 = ((-0.70, -1.0), (20.1e-3, -72.4e-3, -82.9e-3))
    pt4 = ((-0.70, 1.0), (20.1e-3, -72.4e-3, 12.0e-3))
    pt3 = ((1.0, 1.0), (20.1e-3, 46.3e-3, 12.0e-3))

    tri_list = Screen.quad_to_tri_list(pt1, pt2, pt3, pt4)

    AODscope_left_screen = Screen(tri_list=tri_list, server_number=1, id=1, fullscreen=True, vsync=True, square_side=6.0e-2, square_loc='ll')

    aux_screen = Screen(tri_list=tri_list, server_number=1, id=0, fullscreen=False, vsync=True, square_side=0, square_loc='ll')

    screens = [AODscope_left_screen, aux_screen]
    port = 60629
    host = ''

    #draw_screens(AODscope_left_screen)
    plt.show()

    manager =  StimServer(screens=screens, host=host, port=port, auto_stop=False)

    manager.black_corner_square()
    manager.set_idle_background(0)

    manager.loop()

if __name__ == '__main__':
    main()
