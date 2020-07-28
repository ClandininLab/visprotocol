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

    if len(dlpc350_objects) == 0:
        print('No lightcrafters detected! Try sudo')

    # Define screen(s) for the rig
    w = 20.6e-2; h = 12.8e-2; # meters of image at projection plane

    bruker_left_screen = Screen(width=w, height=h, rotation=pi-pi/4, offset=(4.0e-2, 3.9e-2, -6.1e-2), id=1, fullscreen=True, vsync=True, square_size=(0.2, 0.2), square_loc=(0.80, -1.0))

    aux_screen = Screen(width=w, height=h, rotation=pi-pi/4, offset=(4.0e-2, 3.9e-2, -6.1e-2), id=0, fullscreen=False, vsync=True, square_size=(0.0, 0.0))

    screens = [bruker_left_screen, aux_screen]
    port = 60629
    host = ''

    draw_screens(bruker_left_screen)
    plt.show()

    manager =  StimServer(screens=screens, host=host, port=port, auto_stop=False)

    manager.black_corner_square()
    manager.set_idle_background(0)

    manager.loop()

if __name__ == '__main__':
    main()
