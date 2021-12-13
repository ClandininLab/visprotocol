#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ni-usb device classes

@author: mhturner
"""


import nidaqmx

class NIUSB():
    def __init__(self):
        pass

class NIUSB6210(NIUSB):
    """
    https://www.ni.com/en-us/support/model.usb-6210.html
    """
    def __init__(self, dev='Dev5', trigger_channel='ctr0'):
        super().__init__()  # call the parent class init method
        self.dev = dev
        self.trigger_channel = trigger_channel

    def sendTrigger(self):
        with nidaqmx.Task() as task:
            task.co_channels.add_co_pulse_chan_time('{}/{}'.format(self.dev, self.trigger_channel),
                                                    low_time=0.002,
                                                    high_time=0.001)


    def outputStep(self, output_channel='ctr1', low_time=0.001, high_time=0.100):
        with nidaqmx.Task() as task:
            task.co_channels.add_co_pulse_chan_time('{}/{}'.format(self.dev, output_channel),
                                                    low_time=low_time,
                                                    high_time=high_time)
            task.start()


class NIUSB6001(NIUSB):
    """
    https://www.ni.com/en-us/support/model.usb-6001.html
    """
    def __init__(self, dev='Dev1', trigger_channel='port2/line0'):
        super().__init__()  # call the parent class init method
        self.dev = dev
        self.trigger_channel = trigger_channel

    def sendTrigger(self):
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan('{}/{}'.format(self.dev, self.trigger_channel))
            task.start()
            task.write([True, False])
