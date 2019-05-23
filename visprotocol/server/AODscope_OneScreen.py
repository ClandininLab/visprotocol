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
         dlpc350_object.set_current(red=0, green = 0, blue = 1)
         dlpc350_object.pattern_mode(fps=115.06, red=True, blue=True, green=False)  
    if len(dlpc350_objects) == 0:
        print('No lightcrafters detected! Try sudo')   
     
    # Define screen(s) for the rig
    w = 15.0e-2; h = 10.0e-2; # meters of image at projection plane

    pts = [
            ((1.0, 1.0), (46.3e-3, 25.2e-3, 0e-3)),
            ((-0.70, 1.0), (-72.4e-3, 25.2e-3, 0e-3)),
            ((-0.70, -1.0), (-72.4e-3, 0.0e-3, -83.1e-3)),
            ((1.0, -1.0), (46.3e-3, 0.0e-3, -83.1e-3))
        ]

    # Rotate 45 deg around x axis s.t. screen goes from pole to pole of sphere. To reduce visibility of singularity aberrations at poles

    pts = [
            ((1.0, 1.0), (46.3e-3, 17.8e-3, 17.8e-3)),
            ((-0.70, 1.0), (-72.4e-3, 17.8e-3, 17.8e-3)),
            ((-0.70, -1.0), (-72.4e-3, 58.8e-3, -58.8e-3)),
            ((1.0, -1.0), (46.3e-3, 58.8e-3, -58.8e-3))
        ]

    tri_list = Screen.quad_to_tri_list(*pts)

    AODscope_left_screen = Screen(tri_list=tri_list, server_number=1, id=1, fullscreen=True, vsync=None, square_side=4.0e-2, square_loc='ll')

    #aux_screen = Screen(tri_list=tri_list, server_number=1, id=0, fullscreen=False, vsync=True, square_side=0, square_loc='ll')

    screens = [AODscope_left_screen]
    port = 60629
    host = ''

    draw_screens(AODscope_left_screen)
    plt.show()
    
    manager =  StimServer(screens=screens, host=host, port=port, auto_stop=False)
    
    manager.black_corner_square()
    manager.set_idle_background(0)    
    
    manager.loop()
    
if __name__ == '__main__':
    main()
