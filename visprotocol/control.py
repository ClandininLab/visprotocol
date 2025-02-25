#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EpochRun object controls presentation of a sequence of epochs ("epoch run")
"""

from PyQt5.QtWidgets import QApplication
from time import sleep
import os
import posixpath

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
        protocol_object.save_metadata_flag = save_metadata_flag
        client.manager.set_idle_background(protocol_object.run_parameters['idle_color'])

        protocol_object.precomputeEpochParameters()

        self.server_series_dir = None
        if save_metadata_flag and ('server_data_directory' in data.cfg) and (data.cfg['server_data_directory'] is not None):
            self.server_series_dir = posixpath.join(data.cfg['server_data_directory'], data.experiment_file_name, str(data.series_count))

            # set directory in which to save animal positions from each screen.
            server_pos_history_dir = posixpath.join(self.server_series_dir, 'flystim_pos')
            client.manager.set_save_pos_history_dir(server_pos_history_dir)

        if 'do_loco' in data.cfg and data.cfg['do_loco']:
            if save_metadata_flag:
                if ('server_data_directory' in data.cfg) and (data.cfg['server_data_directory'] is not None):
                    server_loco_dir = posixpath.join(self.server_series_dir, 'loco')
                    client.manager.loco_set_save_directory(server_loco_dir)
                else:
                    print("Locomotion data can't be saved on server without server_data_directory specified in config.yaml.")
            client.manager.loco_start()
            sleep(3) # Give loco time to load

        if save_metadata_flag:
            data.createEpochRun(protocol_object)
        else:
            print('Warning - you are not saving your metadata!')

        # Trigger acquisition of scope and cameras by send triggering TTL through the DAQ device (if device is set)
        if client.daq_device is not None:
            print("Triggering acquisition devices.")
            client.daq_device.sendTrigger()

        if 'do_loco' in data.cfg and data.cfg['do_loco']:
            sleep(2) # Give loco time to start acquiring
            client.manager.loco_loop_start() # start loop, which is superfluous if closed loop is not needed for the exp.

        # # # Pre-run Time # # #
        if 'pre_run_time' in protocol_object.run_parameters:
            client.manager.print_on_server(f'Starting pre-run time of {protocol_object.run_parameters["pre_run_time"]} seconds.')
            sleep(protocol_object.run_parameters['pre_run_time'])

        # # # Epoch run loop # # #
        client.manager.print_on_server("Starting run.")
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

        # Set screens to dark
        client.manager.black_corner_square()
        # client.manager.set_idle_background(0)

        if 'do_loco' in data.cfg and data.cfg['do_loco']:
            client.manager.loco_close()
            client.manager.loco_set_save_directory(None)

        client.manager.print_on_server('Stopping run.')
        # # # Epoch run loop # # #

    def startEpoch(self, protocol_object, data, client, save_metadata_flag=True):
        #  get stimulus parameters for this epoch
        protocol_object.getEpochParameters()

        if save_metadata_flag:
            data.createEpoch(protocol_object)

        # Send triggering TTL through the DAQ device (if device is set)
        if client.daq_device is not None:
            client.daq_device.sendTrigger()

        client.manager.print_on_server(f'Epoch {protocol_object.num_epochs_completed}')

        # Use the protocol object to send the stimulus to flystim
        protocol_object.loadStimuli(client)

        protocol_object.startStimuli(client)

        client.manager.print_on_server('Epoch completed.')

        if save_metadata_flag:
            data.endEpoch(protocol_object)

        protocol_object.advanceEpochCounter()
