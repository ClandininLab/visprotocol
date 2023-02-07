#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import matplotlib.pyplot as plt

from flystim.screen import Screen, SubScreen
from flystim.draw import draw_screens
from flystim.dlpc350 import make_dlpc350_objects

from visprotocol.server.clandinin_server import Server
from visprotocol.device.daq.labjack import LabJackTSeries
from visprotocol.loco_managers.fictrac_managers import FtClosedLoopManager

def get_subscreen(dir):
    '''
    Tuned for ballrig with "rotate left" in /etc/X11/xorg.conf
    Because screens are flipped l<->r, viewport_ll is actually lower right corner.
    '''
    north_w = 2.956e-2
    side_w = 2.96e-2

    # set coordinates as a function of direction
    if dir == 'w':
       # set screen width and height
       h = 3.10e-2
       pa = (-north_w/2, -side_w/2, -h/2)
       pb = (-north_w/2, +side_w/2, -h/2)
       pc = (-north_w/2, -side_w/2, +h/2)
       viewport_ll = (-0.636, -0.5)
       viewport_width = -0.636 - (-0.345)
       viewport_height = -0.289 - (-0.5)
    elif dir == 'n':
       # set screen width and height
       h = 3.29e-2
       pa = (-north_w/2, +side_w/2, -h/2)
       pb = (+north_w/2, +side_w/2, -h/2)
       pc = (-north_w/2, +side_w/2, +h/2)
       viewport_ll = (+0.2956, -0.1853)
       viewport_width = +0.2956 - 0.5875
       viewport_height = +0.015 - (-0.1853)
    elif dir == 'e':
        # set screen width and height
        h = 3.40e-2
        pa = (+north_w/2, +side_w/2, -h/2)
        pb = (+north_w/2, -side_w/2, -h/2)
        pc = (+north_w/2, +side_w/2, +h/2)
        viewport_ll = (-0.631, +0.135)
        viewport_width = -0.631 - (-0.355)
        viewport_height = +0.3397- (+0.135)
    elif dir == 'aux':
        # set screen width and height
        h = 3.29e-2
        pa = (-north_w/2, +side_w/2, -h/2)
        pb = (+north_w/2, +side_w/2, -h/2)
        pc = (-north_w/2, +side_w/2, +h/2)
        viewport_ll = (-1, -1)
        viewport_width = 2
        viewport_height = 2
    else:
        raise ValueError('Invalid direction.')

    return SubScreen(pa=pa, pb=pb, pc=pc, viewport_ll=viewport_ll, viewport_width=abs(viewport_width), viewport_height=abs(viewport_height))

def main():
    # Set lightcrafter and GL environment settings
    os.system('export __GL_SYNC_TO_VBLANK=0; export __GL_MaxFramesAllowed=1; echo $__GL_SYNC_TO_VBLANK; echo $__GL_MaxFramesAllowed')

    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.pattern_mode(fps=120, red=0, blue=0.9, green=0.9)

    aux_screen = Screen(subscreens=[get_subscreen('aux')], server_number=1, id=0, fullscreen=False, vsync=False, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)
    projector_screen = Screen(subscreens=[get_subscreen('w'), get_subscreen('n'), get_subscreen('e')], server_number=1, id=1, fullscreen=True, square_loc=(0.75, -1.0), square_size=(0.25, 0.25), vsync=False, horizontal_flip=True)

    screens = [projector_screen, aux_screen]

    # Initialize camera with proper settings
    # jf_cam = FlirCam(serial_number='20243355', attrs_json_fn='/home/clandinin/src/jackfish/presets/MC/cam_20243355.json')
    # jf_cam.close()

    loco_class = FtClosedLoopManager
    loco_kwargs = {
        'host':          '127.0.0.1',
        'port':          33334,
        'ft_bin':           "/home/clandinin/lib/fictrac211/bin/fictrac",
        'ft_config':        "/home/clandinin/lib/fictrac211/config_MC.txt",
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
Z
