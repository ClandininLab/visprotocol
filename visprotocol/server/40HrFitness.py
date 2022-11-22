#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import matplotlib.pyplot as plt

from flystim.screen import Screen, SubScreen
from flystim.draw import draw_screens

from visprotocol.server.clandinin_server import Server
from visprotocol.device.daq.labjack import LabJackTSeries
from visprotocol.loco_managers.fictrac_managers import FtClosedLoopManager

from jackfish.devices.cameras.flir import FlirCam

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
    square_max_color = 1.0
    left_screen = Screen(subscreens=[get_subscreen('l')], server_number=1, id=1, fullscreen=True, vsync=True, square_size=(0.05, 0.10), square_loc=(-1, -1), square_max_color=square_max_color, name='Left', horizontal_flip=False)
    center_screen = Screen(subscreens=[get_subscreen('c')], server_number=1, id=2, fullscreen=True, vsync=True, square_size=(0.05, 0.10), square_loc=(-1, -1), square_max_color=square_max_color, name='Center', horizontal_flip=False)
    right_screen = Screen(subscreens=[get_subscreen('r')], server_number=1, id=3, fullscreen=True, vsync=True, square_size=(0.05, 0.10), square_loc=(-1, +0.90), square_max_color=square_max_color, name='Right', horizontal_flip=False)
    aux_screen = Screen(subscreens=[get_subscreen('aux')], server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)

    # screens = [left_screen, center_screen, right_screen, aux_screen]
    screens = [left_screen, center_screen, right_screen]
    # screens = [left_screen]
    # draw_screens(screens); plt.show()

    # Initialize camera with proper settings
    jf_cam = FlirCam(serial_number='20243355', attrs_json_fn='/home/clandinin/src/jackfish/presets/cam_20243355.json')
    jf_cam.close()

    loco_class = FtClosedLoopManager
    loco_kwargs = {
        'host':          '127.0.0.1', 
        'port':          33334, 
        'ft_bin':           "/home/clandinin/src/fictrac/bin/fictrac",
        'ft_config':        "/home/clandinin/src/fictrac/config.txt", 
        'ft_theta_idx':     16, 
        'ft_x_idx':         14, 
        'ft_y_idx':         15, 
        'ft_frame_num_idx': 0, 
        'ft_timestamp_idx': 21
    }
    daq_class = LabJackTSeries
    daq_kwargs = {'dev':"440017544", 'trigger_channel':["FIO4", "FIO5", "FIO6"]}
    
    server = Server(screens = screens, loco_class=loco_class, loco_kwargs=loco_kwargs, daq_class=daq_class, daq_kwargs=daq_kwargs)
    server.loop()

if __name__ == '__main__':
    main()
