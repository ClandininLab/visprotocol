#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flyrpc.launch import launch_server
from flystim.screen import Screen
import flystim.stim_server
from flystim.dlpc350 import make_dlpc350_objects
from math import pi


def main():
    # Put lightcrafter(s) in pattern mode
#    dlpc350_objects = make_dlpc350_objects()
#    for dlpc350_object in dlpc350_objects:
#         dlpc350_object.pattern_mode(fps=115.06)
#     
     
    # Define screen(s) for the rig
    w = 15.75e-2; h = 12.6e-2; # meters of image at projection plane

    bruker_left_screen = Screen(width=w, height=h, rotation=-pi/4, offset=(5.0e-2, 6.1e-2, -6.1e-2), id=1, fullscreen=False, vsync=None, square_side=3.75e-2, square_loc='lr')
    screens = [bruker_left_screen]
    port = 60629
    host = ''
    
    manager = launch_server(flystim.stim_server, host=host, port=port, auto_stop=False, setup_name='macbook')
    
#    manager = StimManager(screens)
    manager.black_corner_square()
    manager.set_idle_background(0)
    print('Serving on port 60629')
#    if len(dlpc350_objects) == 0:
#        print('No lightcrafters detected! Try sudo')
#    stim_server(manager, addr = ('', 60629))

if __name__ == '__main__':
    main()
