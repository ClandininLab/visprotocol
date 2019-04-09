#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
from flystim.stim_server import launch_stim_server
from flyrpc.transceiver import MySocketClient
from flystim.screen import Screen
from math import pi

class Client():
    def __init__(self):
        if socket.gethostname() == "MHT-laptop": # (laptop, for dev.)
            self.server_options = {'host': '0.0.0.0',
                                   'port': 60629,
                                   'use_server': False}
            self.NI_USB_name = ''
        elif socket.gethostname() == 'DESKTOP-4Q3O7LU': #AODscope
            self.server_options = {'host': '171.65.17.126',
                                   'port': 60629,
                                   'use_server': True}
            self.NI_USB_name = 'NI USB-6001'
        else: #Bruker computer
            self.server_options = {'host': '192.168.1.232',
                                   'port': 60629,
                                   'use_server': True}
            self.NI_USB_name = 'NI USB-6210'

    # # # Start the stim manager and set the frame tracker square to black # # #
        if self.server_options['use_server']:
            self.manager = MySocketClient(host=self.server_options['host'], port=self.server_options['port'])
        else:
            w = 20.6e-2; h = 12.8e-2; # meters of image at projection plane
            screens = [Screen(width=w, height=h, rotation=pi+pi/4, offset=(-3.9e-2, 4.0e-2, -6.1e-2), fullscreen=False, vsync=None, square_loc='lr')]
            self.manager = launch_stim_server(screens)
        
        self.manager.black_corner_square()
        self.manager.set_idle_background(0)
