#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
from flystim.stim_server import launch_stim_server
from flyrpc.transceiver import MySocketClient
from flystim.screen import Screen
from math import pi
from flystim.draw import draw_screens
from visprotocol.device import niusb


class Client():
    def __init__(self, cfg):
        self.user_name = cfg.get('user_name')
        self.rig_name = cfg.get('rig_name')
        self.draw_screens = cfg.get('draw_screens')
        self.cfg = cfg
        self.niusb_device = None

        print("IN CLANDININ CLIENT")

        # # # load rig-specific server/client options # #
        if socket.gethostname() == 'DESKTOP-4Q3O7LU':  # AODscope Karthala
            self.server_options = {'host': '171.65.17.126',
                                   'port': 60629,
                                   'use_server': True}
            self.niusb_device = niusb.NIUSB6001(dev='Dev1', trigger_channel='port2/line0')

        elif socket.gethostname() == 'USERBRU-I10P5LO':  # Bruker
            self.server_options = {'host': '171.65.17.246',
                                   'port': 60629,
                                   'use_server': True}
            self.niusb_device = niusb.NIUSB6210(dev='Dev5', trigger_channel='ctr0')
        elif socket.gethostname() == 'clandinin-ballbehavior':  # 24HrFitness
            self.server_options = {'host': '0.0.0.0',
                                   'port': 60629,
                                   'use_server': True}
        elif socket.gethostname() == '40hr-assist':  # 40HrAssist
            self.server_options = {'host': '171.65.18.61',
                                   'port': 60629,
                                   'use_server': True}
        elif socket.gethostname() == '40hr-fitness':  # 40HrAssist
            self.server_options = {'host': '0.0.0.0',
                                   'port': 60629,
                                   'use_server': True}
        else:
            self.server_options = {'host': '0.0.0.0',
                                   'port': 60629,
                                   'use_server': False}

        # # # Start the stim manager and set the frame tracker square to black # # #
        if self.server_options['use_server']:
            self.manager = MySocketClient(host=self.server_options['host'], port=self.server_options['port'])
        else:
            aux_screen = Screen(server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0.25, 0.25))
            if self.draw_screens:
              draw_screens(aux_screen)
            self.manager = launch_stim_server(aux_screen)

        self.manager.black_corner_square()
        self.manager.set_idle_background(0)

        print("IN CLANDININ CLIENT BOTTOM")


class Client_Stim_Regeneration():
    def __init__(self, cfg, screen):
        self.user_name = cfg.get('user_name')
        self.rig_name = cfg.get('rig_name')
        self.cfg = cfg
        self.niusb_device = None

        self.server_options = {'host': '0.0.0.0',
                               'port': 60629,
                               'use_server': False}

        # # # Start the stim manager # # #
        self.manager = launch_stim_server(screen)

        self.manager.set_idle_background(0)
