#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EpochRun object controls presentation of a sequence of epochs ("epoch run")
"""

from PyQt5.QtWidgets import QApplication
from time import sleep
import os

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
        
        if 'do_loco' in data.cfg and data.cfg['do_loco']:
            if save_metadata_flag:
                if data.cfg['server_data_directory'] is not None:
                    server_experiment_dir = os.path.join(data.cfg['server_data_directory'], data.experiment_file_name, str(data.series_count))
                    client.manager.loco_set_save_directory(server_experiment_dir)
                else:
                    print("Locomotion data can't be saved on server without server_data_directory specified in config.yaml.")
            client.manager.loco_start()
            sleep(2) # Give loco time to load
            client.manager.loco_loop_start() # start loop, which is superfluous if closed loop is not needed for the exp.

        if save_metadata_flag:
            data.createEpochRun(protocol_object)
        else:
            print('Warning - you are not saving your metadata!')

        # print("START RUN")

        # # # Epoch run loop # # #
        protocol_object.num_epochs_completed = 0
        while protocol_object.num_epochs_completed < protocol_object.run_parameters['num_epochs']:
            print('COMPLETED {} / {} EPOCHS'.format(protocol_object.num_epochs_completed, protocol_object.run_parameters['num_epochs']))

            QApplication.processEvents()
            if self.stop is True:
                self.stop = False
                break # break out of epoch run loop

            if self.pause is True:
                pass # do nothing until resumed or stopped
            else: # start epoch and advance counter
                # print("CONTROL BEFORE START EPOCH")
                self.startEpoch(protocol_object, data, client, save_metadata_flag=save_metadata_flag)
                # print("CONTROL AFTER START EPOCH")

        if 'do_loco' in data.cfg and data.cfg['do_loco']:
            client.manager.loco_close()
        # # # Epoch run loop # # #

    def startEpoch(self, protocol_object, data, client, save_metadata_flag=True):
        #  get stimulus parameters for this epoch
        protocol_object.getEpochParameters()

        if save_metadata_flag:
            data.createEpoch(protocol_object)

        # Send triggering TTL through the DAQ device (if device is set)
        if client.daq_device is not None:
            client.daq_device.sendTrigger()

        # Use the protocol object to send the stimulus to flystim
        protocol_object.loadStimuli(client)
        # print("CONTROL START EPOCH LOADED STIM")

        protocol_object.startStimuli(client)
        # print("CONTROL START EPOCH STARTED STIM")

        protocol_object.advanceEpochCounter()
        # print("CONTROL START EPOCH ADVANCED COUNTER")
