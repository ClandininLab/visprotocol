#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import signal
import sys
import matplotlib.pyplot as plt

from flystim.screen import Screen, SubScreen
from flystim.stim_server import StimServer
from flystim.draw import draw_screens

from clandinin_server import Server
from visprotocol.device import daq

class FortyHrFitnessServer(Server):
    def __init__(self):
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

        left_screen = Screen(subscreens=[get_subscreen('l')], server_number=1, id=1, fullscreen=True, vsync=True, square_size=(0.03, 0.08), square_loc=(-1, -1), name='Left', horizontal_flip=False)
        center_screen = Screen(subscreens=[get_subscreen('c')], server_number=1, id=2, fullscreen=True, vsync=True, square_size=(0.035, 0.08), square_loc=(-1, -1), name='Center', horizontal_flip=False)
        right_screen = Screen(subscreens=[get_subscreen('r')], server_number=1, id=3, fullscreen=True, vsync=True, square_size=(0.04, 0.08), square_loc=(-1, +0.92), name='Right', horizontal_flip=False)
        aux_screen = Screen(subscreens=[get_subscreen('aux')], server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)

        screens = [left_screen, center_screen, right_screen, aux_screen]
        # screens = [left_screen, center_screen, right_screen]
        # draw_screens(screens)
        # plt.show()

        manager = StimServer(screens=screens, host='', port=60629, auto_stop=False)

        fictrac_kwargs = {
            'cwd': os.path.expanduser('~'),
            'ft_bin': "/home/clandinin/src/fictrac/bin/fictrac",
            'ft_config': "/home/clandinin/src/fictrac/config.txt", 
            'ft_host': '127.0.0.1', 
            'ft_port': 33334, 
            'ft_theta_idx': 16, 
            'ft_x_idx': 14, 
            'ft_y_idx': 15, 
            'ft_frame_num_idx': 0, 
            'ft_timestamp_idx': 21
        }
        daq_class = daq.LabJackTSeries
        daq_kwargs = {'dev':"440017544", 'trigger_channel':["FIO4", "FIO5", "FIO6"]}

        super().__init__(manager = manager, do_fictrac=True, fictrac_kwargs=fictrac_kwargs, daq_class=daq_class, daq_kwargs=daq_kwargs)

def main():
    server = FortyHrFitnessServer()
    
    def signal_handler(sig, frame):
        print('Closing server after Ctrl+C...')
        server.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    server.loop()
    server.close()

if __name__ == '__main__':
    main()
