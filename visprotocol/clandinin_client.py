#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
from flystim.stim_server import launch_stim_server
from flyrpc.transceiver import MySocketClient
from flystim.screen import Screen


class Client():
    def __init__(self):
        # # # load rig-specific server/client options # # #
        if socket.gethostname() == 'DESKTOP-4Q3O7LU':  # AODscope Karthala
            self.server_options = {'host': '171.65.17.126',
                                   'port': 60629,
                                   'use_server': True}
            self.NI_USB_name = 'NI USB-6001'
            self.send_ttl = True
        elif socket.gethostname() == 'USERBRU-I10P5LO':  # Bruker
            self.server_options = {'host': '171.65.17.246',
                                   'port': 60629,
                                   'use_server': True}
            self.NI_USB_name = 'NI USB-6210'
            self.send_ttl = True
        else:
            self.server_options = {'host': '0.0.0.0',
                                   'port': 60629,
                                   'use_server': False}
            self.NI_USB_name = ''
            self.send_ttl = False

        # # # Start the stim manager and set the frame tracker square to black # # #
        if self.server_options['use_server']:
            self.manager = MySocketClient(host=self.server_options['host'], port=self.server_options['port'])
        else:
            self.manager = launch_stim_server(Screen(fullscreen=False, width=0.1, height=0.1, offset=(0,1,0)))

        self.manager.black_corner_square()
        self.manager.set_idle_background(0)
