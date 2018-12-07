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
        else:
            self.server_options = {'host': '192.168.1.232',
                                   'port': 60629,
                                   'use_server': True}

    # # # Start the stim manager and set the frame tracker square to black # # #
        if self.server_options['use_server']:
            self.manager = MySocketClient(host=self.server_options['host'], port=self.server_options['port'])
        else:
            w = 15.75e-2; h = 12.6e-2; # meters of image at projection plane
            screens = [Screen(width=w, height=h, rotation=-pi/4, offset=(5.0e-2, 6.1e-2, -6.1e-2), fullscreen=False, vsync=None)]
            self.manager = launch_stim_server(screens)
        
        self.manager.black_corner_square()
        self.manager.set_idle_background(0)