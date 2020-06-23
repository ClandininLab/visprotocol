#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EpochRun object controls presentation of a sequence of epochs ("epoch run")
"""

from PyQt5.QtWidgets import QApplication
import nidaqmx


class EpochRun():
    def __init__(self):
        self.stop = False
        self.pause = False

    def stopRun(self):
        self.stop = True
        QApplication.processEvents()

    def pauseRun(self):
        self.pause = True
        QApplication.processEvents()

    def resumeRun(self):
        self.pause = False
        QApplication.processEvents()

    def startRun(self, protocol_object, data, client, save_metadata_flag=True):
        """
        Required inputs: protocol_object, data, client are 3 major classes of visprotocol
            protocol_object defines the protocol and associated parameters to be used
            data handles the metadata file
            client sends commands to flystim to control the stimulus
        """
        self.stop = False
        self.pause = False
        client.manager.set_idle_background(protocol_object.run_parameters['idle_color'])

        if save_metadata_flag:
            data.createEpochRun(protocol_object)
        else:
            print('Warning - you are not saving your metadata!')

        # # # Epoch run loop # # #
        protocol_object.num_epochs_completed = 0
        while protocol_object.num_epochs_completed < protocol_object.run_parameters['num_epochs']:
            QApplication.processEvents()
            if self.stop is True:
                self.stop = False
                break # break out of epoch run loop

            if self.pause is True:
                pass # do nothing until resumed or stopped
            else: # start epoch and advance counter
                self.startEpoch(protocol_object, data, client, save_metadata_flag=save_metadata_flag)
        # # # Epoch run loop # # #

    def startEpoch(self, protocol_object, data, client, save_metadata_flag=True):
        #  get stimulus parameters for this epoch
        protocol_object.getEpochParameters()

        if save_metadata_flag:
            data.createEpoch(protocol_object)

        if client.send_ttl:
            # Send a TTL pulse through the NI-USB to trigger acquisition
            with nidaqmx.Task() as task:
                if client.NI_USB_name == 'NI USB-6210':
                    task.co_channels.add_co_pulse_chan_time('Dev5/ctr0',
                                                            low_time=0.002,
                                                            high_time=0.001)
                    task.start()
                elif client.NI_USB_name == 'NI USB-6001':
                    task.do_channels.add_do_chan('Dev1/port2/line0')
                    task.start()
                    task.write([True, False])

        # Use the protocol object to send the stimulus to flystim
        protocol_object.loadStimuli(client)

        protocol_object.startStimuli(client)

        protocol_object.advanceEpochCounter()
