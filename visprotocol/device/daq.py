#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAQ (data acquisition) device classes

@author: minseung
"""

from flyrpc.multicall import MyMultiCall

class DAQ():
    def __init__(self):
        pass

    def send_trigger(self):
        pass

class DAQonServer(DAQ):
    '''
    Dummy DAQ class for when the DAQ resides on the server, so that we can call methods as if the DAQ is on the client side.
    Assumes that server has registered functions "daq_sendTrigger" and "daq_outputStep".
    '''
    def __init__(self):
        super().__init__()  # call the parent class init method
        self.manager = None
    def set_manager(self, manager):
        self.manager = manager
    def send_trigger(self, multicall=None, **kwargs):
        if multicall is not None and isinstance(multicall, MyMultiCall):
            multicall.daq_sendTrigger(**kwargs)
            return multicall
        if self.manager is not None:
            self.manager.daq_sendTrigger(**kwargs)
    def output_step(self, multicall=None, **kwargs):
        if multicall is not None and isinstance(multicall, MyMultiCall):
            multicall.daq_outputStep(**kwargs)
            return multicall
        if self.manager is not None:
            self.manager.daq_outputStep(**kwargs)

