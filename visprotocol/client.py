#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flyrpc.transceiver import MySocketClient
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from visprotocol.util import config_tools

class BaseClient():
    def __init__(self, cfg):
        self.cfg = cfg

        # # # Load server options from config file and selections # # #
        self.server_options = config_tools.get_server_options(self.cfg)
        self.trigger_device = config_tools.load_trigger_device(self.cfg)

        # # # Start the stim manager and set the frame tracker square to black # # #
        if self.server_options['use_server']:
            self.manager = MySocketClient(host=self.server_options['host'], port=self.server_options['port'])
        else:
            aux_screen = Screen(server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0.25, 0.25))
            self.manager = launch_stim_server(aux_screen)

        self.manager.black_corner_square()
        self.manager.set_idle_background(0)