#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.screen import Screen, SubScreen
from flystim.draw import draw_screens
from flystim.stim_server import StimServer
from flystim.dlpc350 import make_dlpc350_objects
from math import pi
import matplotlib.pyplot as plt
import os

from ftutil.ft_managers import FtClosedLoopManager

def get_subscreen(dir):
    # Define screen(s) for the rig. Units in meters
    # Fly is at (0, 0, 0), fly looking down +y axis.
    z_bottom  = -27.25e-2 #m
    z_top     = +27.25e-2
    x_left    = -15.25e-2
    x_right   = +15.25e-2
    y_forward = +15.25e-2
    y_back    = -15.25e-2
    
    if dir == 'l':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pb = (x_left, y_back,    z_bottom)
        pc = (x_left, y_forward, z_top)
        pa = (x_left, y_back,    z_top)

    elif dir == 'c':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pb = (x_left,  y_forward, z_bottom)
        pc = (x_right, y_forward, z_top)
        pa = (x_left,  y_forward, z_top)

    elif dir == 'r':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pb = (x_right, y_forward, z_bottom)
        pc = (x_right, y_back,    z_top)
        pa = (x_right, y_forward, z_top)

    elif dir == 'aux':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pa = (x_left,  y_forward, z_bottom)
        pb = (x_right, y_forward, z_bottom)
        pc = (x_left,  y_forward, z_top)

    else:
        raise ValueError('Invalid direction.')

    return SubScreen(pa=pa, pb=pb, pc=pc, viewport_ll=viewport_ll, viewport_width=viewport_width, viewport_height=viewport_height)

def main():
    left_screen = Screen(subscreens=[get_subscreen('l')], server_number=1, id=1, fullscreen=True, vsync=True, square_size=(0.03, 0.08), square_loc=(-1, -1), name='Left', horizontal_flip=False)

    center_screen = Screen(subscreens=[get_subscreen('c')], server_number=1, id=2, fullscreen=True, vsync=True, square_size=(0.035, 0.08), square_loc=(-1, -1), name='Center', horizontal_flip=False)

    right_screen = Screen(subscreens=[get_subscreen('r')], server_number=1, id=3, fullscreen=True, vsync=True, square_size=(0.04, 0.08), square_loc=(-1, +0.92), name='Right', horizontal_flip=False)

    aux_screen = Screen(subscreens=[get_subscreen('aux')], server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)

    #draw_screens([left_screen, center_screen, right_screen])
    #plt.show()

    # screens = [left_screen, center_screen, right_screen, aux_screen]
    screens = [left_screen, center_screen, right_screen]

    port = 60629
    host = ''

    manager = StimServer(screens=screens, host=host, port=port, auto_stop=False)

    #### Set up Fictrac
    FT_FRAME_NUM_IDX = 0
    FT_X_IDX = 14
    FT_Y_IDX = 15
    FT_THETA_IDX = 16
    FT_TIMESTAMP_IDX = 21

    FT_HOST = '127.0.0.1'  # The server's hostname or IP address
    FT_PORT = 33334         # The port used by the server
    FT_BIN =    "/home/clandinin/src/fictrac/bin/fictrac"
    FT_CONFIG = "/home/clandinin/src/fictrac/config.txt"

    ft_manager = FtClosedLoopManager(fs_manager=manager, ft_bin=FT_BIN, ft_config=FT_CONFIG, ft_host=FT_HOST, ft_port=FT_PORT, ft_theta_idx=FT_THETA_IDX, ft_x_idx=FT_X_IDX, ft_y_idx=FT_Y_IDX, ft_frame_num_idx=FT_FRAME_NUM_IDX, ft_timestamp_idx=FT_TIMESTAMP_IDX, cwd=os.path.expanduser('~'), start_at_init=False)
    manager.register_function_on_root(ft_manager.set_cwd, "ft_set_cwd")
    manager.register_function_on_root(ft_manager.start, "ft_start")
    manager.register_function_on_root(ft_manager.close, "ft_close")
    manager.register_function_on_root(ft_manager.sleep, "ft_sleep")
    manager.register_function_on_root(ft_manager.set_pos_0, "ft_set_pos_0")
    manager.register_function_on_root(ft_manager.update_pos, "ft_update_pos")
    manager.register_function_on_root(ft_manager.update_pos_for, "ft_update_pos_for")
    ####

    manager.black_corner_square()
    manager.set_idle_background(0)

    manager.loop()

if __name__ == '__main__':
    main()
