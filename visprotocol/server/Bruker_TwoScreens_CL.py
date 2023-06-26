#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.screen import Screen, SubScreen
from flystim.draw import draw_screens
from flystim.stim_server import StimServer
from flystim.dlpc350 import make_dlpc350_objects
from math import pi
import matplotlib.pyplot as plt

from visprotocol.server.clandinin_server import Server
from visprotocol.device.daq.labjack import LabJackTSeries
from visprotocol.loco_managers.fictrac_managers import FtClosedLoopManager

# from jackfish.devices.cameras.flir import FlirCam

def main():
    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.set_current(red=0, green = 0, blue = 1.0)
         dlpc350_object.pattern_mode(fps=120)
         dlpc350_object.pattern_mode(fps=120)

    # Define screen(s) for the rig. Units in meters
    # Fly is at (0, 0, 0), fly looking down +y axis. Top of the screen is at z=0
    z_bottom = -12.13e-2 #m
    x_left = -7.99e-2
    x_right = +7.99e-2
    y_forward = +7.17e-2
    y_back = -0.8e-2

    def getBrukerLeft():
        return SubScreen(pa=(x_left, y_back, z_bottom), pb=(0, y_forward, z_bottom), pc=(x_left, y_back, 0), viewport_ll=(-0.63, -1.0), viewport_width=1.37, viewport_height=2)
    
    def getBrukerRight():
        return SubScreen(pa=(0, y_forward, z_bottom), pb=(x_right, y_back, z_bottom), pc=(0, y_forward, 0), viewport_ll=(-0.61, -1.0), viewport_width=1.36, viewport_height=2)
        
    def getAux():
        return SubScreen(pa=(x_left, y_back, z_bottom), pb=(0, y_forward, z_bottom), pc=(x_left, y_back, 0))

    bruker_left_screen = Screen(subscreens=[getBrukerLeft()], server_number=1, id=1, fullscreen=True, vsync=True, square_size=(0.11, 0.23), square_loc=(0.89, -1.00), name='Left', horizontal_flip=True)
    bruker_right_screen = Screen(subscreens=[getBrukerRight()], server_number=1, id=2, fullscreen=True, vsync=True, square_size=(0.14, 0.22), square_loc=(-0.85, -0.94), name='Right', horizontal_flip=True)
    aux_screen = Screen(subscreens=[getBrukerLeft()], server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)

    draw_screens([bruker_left_screen, bruker_right_screen])
    plt.show()

    screens = [bruker_left_screen, bruker_right_screen, aux_screen]

    # Initialize camera with proper settings
    # jf_cam = FlirCam(serial_number='20243355', attrs_json_fn='/home/clandinin/src/jackfish/presets/MC/cam_20243355.json')
    # jf_cam.close()
    
    loco_class = FtClosedLoopManager
    loco_kwargs = {
        'host':          '127.0.0.1', 
        'port':          33334, 
        'ft_bin':           "/home/clandininlab/lib/fictrac/bin/fictrac",
        'ft_config':        "/home/clandininlab/lib/fictrac/configs/config_CL.txt", 
        'ft_theta_idx':     16, 
        'ft_x_idx':         14, 
        'ft_y_idx':         15, 
        'ft_frame_num_idx': 0, 
        'ft_timestamp_idx': 21
    }
    
    server = Server(screens = screens, loco_class=loco_class, loco_kwargs=loco_kwargs)
    server.loop()

if __name__ == '__main__':
    main()
