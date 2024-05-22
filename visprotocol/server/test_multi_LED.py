#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.screen import Screen, SubScreen
from flystim.draw import draw_screens
from flystim.stim_server import StimServer
from flystim.dlpc350 import make_dlpc350_objects
from math import pi
import matplotlib.pyplot as plt

def main():
    # LCR USB commands handled thru lightcrafter package script first

    def getBrukerRight():
        # Define screen(s) for the rig. Units in meters
        # Fly is at (0, 0, 0), fly looking down +y axis. Top of the screen is at z=0
        scale_fact = 2.52
        x_right = scale_fact*7.99e-2
        # x_almost_center = +0.919e-2
        y_back = scale_fact*-0.8e-2
        # y_forward = +6.25e2
        # z_top = +2.87e2
        # z_bottom = -8.98e-2 #m
        z_bottom = scale_fact*-12.13e-2
        y_forward = scale_fact*7.17e-2

        # set screen width and height

        pb = (x_right, y_back, z_bottom)
        pa = (0, y_forward, z_bottom)
        pc = (0, y_forward, 0)
        viewport_ll = (-0.54, -0.46)
        viewport_height = 0.61 - (-0.46)
        viewport_width = 0.23 - (-0.54)
        
        return SubScreen(pa, pb, pc, viewport_ll, viewport_width, viewport_height)

    def getAux():
        return SubScreen(pa=(x_left, y_back, z_bottom), pb=(0, y_forward, z_bottom), pc=(x_left, y_back, 0))

    bruker_right_screen = Screen(subscreens=[getBrukerRight()], server_number=1, id=3, fullscreen=True, vsync=True, square_size=(0.15, 0.23), square_loc=(0.32, -0.57), name='Left', horizontal_flip=True)

    aux_screen = Screen(subscreens=[getBrukerRight()], server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)
    
    #screens = [bruker_left_screen, aux_screen]
    screens = [bruker_right_screen, aux_screen]
    port = 60629
    host = ''

    manager = StimServer(screens=screens, host=host, port=port, auto_stop=False)

    manager.black_corner_square()
    manager.set_idle_background(0)

    manager.loop()

if __name__ == '__main__':
    main()
