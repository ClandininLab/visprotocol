#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class BaseClient():
    def __init__(self, cfg):

        # # # Load server options from config file and selections # # #
        self.server_options = cfg['rig_config'][cfg.get('rig_name')].get('server_options', None)
       
        if self.server_options is None:
            self.server_options = {'host': '0.0.0.0',
                                    'port': 60629,
                                    'use_server': False}