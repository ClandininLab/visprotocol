#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.launch import StimManager, stim_server
from flystim.screen import Screen

from flystim.dlpc350 import make_dlpc350_objects


def main():
    FullScreen = True
    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.pattern_mode(fps=115.06)
     
    # Define screen(s) for the rig
    # TODO: check perspective correction measurements
    w = 14.2e-2; h = 9e-2; # meters of image at projection plane, screen only shows 9x9 of this
    zDistToScreen = 5.36e-2; # meters

    bruker_left_screen = Screen(width=w, height=h, rotation=pi/4, offset=(-w/2, zDistToScreen, -h/2), id=1, fullscreen=True, vsync=None, square_side=2e-2, square_loc='lr')
    bruker_right_screen = Screen(width=w, height=h, rotation=-pi/4, offset=(w/2, zDistToScreen, -h/2), id=2, fullscreen=True, vsync=None, square_side=2e-2, square_loc='ll')
    screens = [bruker_left_screen, bruker_right_screen]
    
    manager = StimManager(screens)
    manager.black_corner_square()
    manager.set_idle_background(0)
    stim_server(manager, addr = ('', 60629))

if __name__ == '__main__':
    main()
