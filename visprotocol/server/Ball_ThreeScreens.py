#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.screen import Screen
from flystim.stim_server import StimServer
from flystim.dlpc350 import make_dlpc350_objects
from math import pi

# Define screen(s) for the rig
def dir_to_tri_list(dir):
    # set screen width
    w = 3.0e-2

    # set coordinates as a function of direction
    if dir == 'w':
        h = 2.9e-2
        pts = [
            ((+0.563125, -0.32875), (-w/2, -w/2, -h/2)),
            ((+0.563125, -0.66125), (-w/2, +w/2, -h/2)),
            ((+0.354375, -0.66125), (-w/2, +w/2, +h/2)),
            ((+0.354375, -0.32875), (-w/2, -w/2, +h/2))
        ]
    elif dir == 'n':
        h = 3.1e-2
        pts = [
            ((+0.2150, +0.62000), (-w/2, +w/2, -h/2)),
            ((+0.2150, +0.31625), (+w/2, +w/2, -h/2)),
            ((+0.0125, +0.31625), (+w/2, +w/2, +h/2)),
            ((+0.0125, +0.62000), (-w/2, +w/2, +h/2))
        ]

    elif dir == 'e':
        h = 3.2e-2
        pts = [
            ((-0.101875, -0.28500), (+w/2, +w/2, -h/2)),
            ((-0.101875, -0.58875), (+w/2, -w/2, -h/2)),
            ((-0.314375, -0.58875), (+w/2, -w/2, +h/2)),
            ((-0.314375, -0.28500), (+w/2, +w/2, +h/2))
        ]
    else:
        raise ValueError('Invalid direction.')

    return Screen.quad_to_tri_list(*pts)

# Helper for defining screen(s) for the rig
def make_tri_list():
    return dir_to_tri_list('w') + dir_to_tri_list('n') + dir_to_tri_list('e')

def main():
    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.pattern_mode(fps=120, red=0, blue=2.1, green=2.1)

    screen = Screen(server_number=1, id=1, tri_list=make_tri_list())
    #draw_screens(screen)
    screen.draw()

    port = 60629
    host = ''

    manager =  StimServer(screens=screen, host=host, port=port, auto_stop=False)

    manager.black_corner_square()
    manager.set_idle_background(0)

    manager.loop()

if __name__ == '__main__':
    main()
