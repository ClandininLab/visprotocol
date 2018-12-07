#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
from visprotocol.data import clandinin_data

class Data(clandinin_data.Data):
    def __init__(self):
        super().__init__() #call the parent class init method first

        # # # Data directory # # #             
        if socket.gethostname() == "MHT-laptop": # (laptop, for dev.)
            self.data_directory = '/Users/mhturner/documents/stashedObjects'
        else:
            self.data_directory = 'E:/Max/FlystimData/'
    
        # # # Other metadata defaults. These can be changed in the gui as well # # #
        self.experimenter = 'MHT'
        self.rig = 'Bruker'
    
        # # #  Lists of fly metadata # # # 
        self.prepChoices = ['Left optic lobe',
                            'Right optic lobe',
                            'Whole brain']
        self.driverChoices = ['L2 (21Dhh)','LC11 (R22H02; R20G06)','LC17 (R21D03; R65C12)',
                              'LC18 (R82D11; R92B11)', 'LC26 (VT007747; R85H06)', 
                              'LC9 (VT032961; VT040569)','LC20 (R17A04, R35B06)']
        self.indicatorChoices = ['GCaMP6f',
                                 'GCaMP6m',
                                 'ASAP2f',
                                 'ASAP4c',
                                 '10_90_GCaMP6f',
                                 'SF-iGluSnFR.A184V']