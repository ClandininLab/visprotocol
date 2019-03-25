#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.screen import Screen
from flystim.stim_server import StimServer
from flystim.dlpc350 import make_dlpc350_objects
from math import pi


def main():
    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.pattern_mode(fps=115.06)
    
    if len(dlpc350_objects) == 0:
        print('No lightcrafters detected! Try sudo')   
     
    # Define screen(s) for the rig
    w = 20.6e-2; h = 12.8e-2; # meters of image at projection plane

    AODscope_left_screen = Screen(width=w, height=h, rotation=pi+pi/4, offset=(-3.9e-2, 4.0e-2, -6.1e-2), server_number=1, id=1, fullscreen=True, vsync=None, square_side=5e-2, square_loc='lr')
 
    aux_screen = Screen(width=w, height=h, rotation=pi+pi/4, offset=(-3.9e-2, 4.0e-2, -6.1e-2), server_number=1, id=0, fullscreen=False, vsync=None, square_side=0)

    screens = [AODscope_left_screen, aux_screen]
    port = 60629
    host = ''

    AODscope_left_screen.draw()
    
    manager =  StimServer(screens=screens, host=host, port=port, auto_stop=False)
    
    manager.black_corner_square()
    manager.set_idle_background(0)    
    
    manager.loop()
    
if __name__ == '__main__':
    main()
