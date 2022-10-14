#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAQ (data acquisition) device classes

@author: mhturner and minseung
"""

import numpy as np
import time

import nidaqmx
from nidaqmx.types import CtrTime
from labjack import ljm

class DAQ():
    def __init__(self):
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
    def sendTrigger(self, **kwargs):
        if self.manager is not None:
            self.manager.daq_sendTrigger(**kwargs)
    def outputStep(self, **kwargs):
        if self.manager is not None:
            self.manager.daq_outputStep(**kwargs)

class LabJackTSeries(DAQ):
    def __init__(self, dev=None, trigger_channel=['FIO4']):
        super().__init__()  # call the parent class init method
        serial_number = dev
        self.trigger_channel = trigger_channel

        # Initialize ljm T4/T7 handle
        self.handle = ljm.openS("TSERIES", "ANY", "ANY" if serial_number is None else serial_number)
        self.info = ljm.getHandleInfo(self.handle)
        self.deviceType = self.info[0]
        self.serial_number = self.info[2]
        
        if self.deviceType == ljm.constants.dtT4:
            # LabJack T4 configuration

            # All analog input ranges are +/-1 V, stream settling is 0 (default) and
            # stream resolution index is 0 (default).
            aNames = ["AIN_ALL_RANGE", "STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            aValues = [1.0, 0, 0]
        else:
            # LabJack T7 and other devices configuration

            # Ensure triggered stream is disabled.
            ljm.eWriteName(self.handle, "STREAM_TRIGGER_INDEX", 0)

            # Enabling internally-clocked stream.
            ljm.eWriteName(self.handle, "STREAM_CLOCK_SOURCE", 0)

            # All analog input ranges are +/-1 V, stream settling is 6 
            # and stream resolution index is 0 (default).
            aNames = ["AIN_ALL_RANGE", "STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            aValues = [1.0, 6, 0]

        # Write the analog inputs' negative channels (when applicable), ranges,
        # stream settling time and stream resolution configuration.
        numFrames = len(aNames)
        ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

    def write(self, names, vals):
        ljm.eWriteNames(self.handle, len(names), names, vals)

    def sendTrigger(self, trigger_channel=None, trigger_duration=0.05):
        if trigger_channel is None:
            trigger_channel = self.trigger_channel
        self.outputStep(output_channel=trigger_channel, low_time=0, high_time=trigger_duration, initial_delay=0)

    def outputStep(self, output_channel=['FIO4'], low_time=0.001, high_time=0.100, initial_delay=0.00):
        if not isinstance(output_channel, list):
            output_channel = [output_channel]

        write_states = np.ones(len(output_channel), dtype=int)
        if initial_delay > 0:
            time.sleep(initial_delay)
        if low_time > 0:
            self.daq.write(output_channel, (write_states*0).tolist())
            time.sleep(low_time)
        if high_time > 0:
            self.daq.write(output_channel, (write_states*1).tolist())
            time.sleep(high_time)
        self.daq.write(output_channel, (write_states*0).tolist())

    def close(self):
        ljm.close(self.handle)

class NIUSB6210(DAQ):
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
            task.start()

    def outputStep(self, output_channel='ctr1', low_time=0.001, high_time=0.100, initial_delay=0.00):
        with nidaqmx.Task() as task:
            task.co_channels.add_co_pulse_chan_time('{}/{}'.format(self.dev, output_channel),
                                                    low_time=low_time,
                                                    high_time=high_time,
                                                    initial_delay=initial_delay)

            task.start()
            task.wait_until_done()
            task.stop()


class NIUSB6001(DAQ):
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
