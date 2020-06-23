#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
from flystim.stim_server import launch_stim_server
from flyrpc.transceiver import MySocketClient
from flystim.screen import Screen
from math import pi


class Client():
    def __init__(self, cfg):
        self.user_name = cfg.get('user_name')
        self.rig_name = cfg.get('rig_name')
        self.cfg = cfg
        # # # load rig-specific server/client options # #
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
            w = 20.6e-2; h = 12.8e-2; # meters of image at projection plane
            aux_screen = Screen(width=w, height=h, rotation=pi-pi/4, offset=(4.0e-2, 3.9e-2, -6.1e-2), id=0, fullscreen=False, vsync=True, square_side=2e-2)
            # aux_screen = Screen(width=w, height=h, rotation=pi, offset=(h/2, w/2, -6.1e-2), id=0, fullscreen=False, vsync=True, square_side=0)

            # pt2 = ((1.0, -1.0), (20.1e-3, 46.3e-3, -82.9e-3))
            # pt1 = ((-0.70, -1.0), (20.1e-3, -72.4e-3, -82.9e-3))
            # pt4 = ((-0.70, 1.0), (20.1e-3, -72.4e-3, 12.0e-3))
            # pt3 = ((1.0, 1.0), (20.1e-3, 46.3e-3, 12.0e-3))
            #
            # tri_list = Screen.quad_to_tri_list(pt1, pt2, pt3, pt4)
            #
            # aux_screen = Screen(tri_list=tri_list, id=0, fullscreen=False, vsync=True, square_side=5e-3, square_loc='ll')

            # self.manager = launch_stim_server(Screen(fullscreen=False, width=0.1, height=0.1, offset=(0,1,0)))
            self.manager = launch_stim_server(aux_screen)

        self.manager.black_corner_square()
        self.manager.set_idle_background(0)
