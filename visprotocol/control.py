#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EpochRun object controls presentation of a sequence of epochs ("epoch run")
"""

from PyQt5.QtWidgets import QApplication


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

        print("START RUN")

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
                print("CONTROL BEFORE START EPOCH")
                self.startEpoch(protocol_object, data, client, save_metadata_flag=save_metadata_flag)
                print("CONTROL AFTER START EPOCH")
        # # # Epoch run loop # # #

    def startEpoch(self, protocol_object, data, client, save_metadata_flag=True):
        #  get stimulus parameters for this epoch
        protocol_object.getEpochParameters()

        if save_metadata_flag:
            data.createEpoch(protocol_object)

        # Send triggering TTL through the NI-USB device (if device is set)
        if client.niusb_device is not None:
            client.niusb_device.sendTrigger()

        # Use the protocol object to send the stimulus to flystim
        protocol_object.loadStimuli(client)
        print("CONTROL START EPOCH LOADED STIM")

        protocol_object.startStimuli(client)
        print("CONTROL START EPOCH STARTED STIM")

        protocol_object.advanceEpochCounter()
        print("CONTROL START EPOCH ADVANCED COUNTER")
