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

    def stop_run(self):
        self.stop = True
        QApplication.processEvents()

    def pause_run(self):
        self.pause = True
        QApplication.processEvents()

    def resume_run(self):
        self.pause = False
        QApplication.processEvents()

    def start_run(self, protocol_object, data, client, save_metadata_flag=True):
        """
        Required inputs: protocol_object, data, client
            protocol_object defines the protocol and associated parameters to be used
            data handles the metadata file
            client sends commands to flystim to control the stimulus
        """
        self.stop = False
        self.pause = False
        protocol_object.save_metadata_flag = save_metadata_flag

        # Set background to idle_color
        client.manager.set_idle_background(protocol_object.run_parameters['idle_color'])

        if save_metadata_flag:
            data.create_epoch_run(protocol_object)
        else:
            print('Warning - you are not saving your metadata!')

        # Trigger acquisition of scope and cameras by send triggering TTL through the DAQ device (if device is set)
        # TODO: set up trigger on epoch run or each epoch
        if client.trigger_device is not None:
            print("Triggering acquisition devices.")
            client.trigger_device.send_trigger()

        if 'do_loco' in data.cfg and data.cfg['do_loco']:
            sleep(2) # Give loco time to start acquiring
            client.manager.loco_loop_start() # start loop, which is superfluous if closed loop is not needed for the exp.

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
                self.start_epoch(protocol_object, data, client, save_metadata_flag=save_metadata_flag)

        # Set frame tracker to dark
        client.manager.black_corner_square()
        client.manager.print_on_server('Stopping run.')

    def start_epoch(self, protocol_object, data, client, save_metadata_flag=True):
        #  get stimulus parameters for this epoch
        protocol_object.get_epoch_parameters()

        if save_metadata_flag:
            data.create_epoch(protocol_object)

        # Send triggering TTL through the DAQ device (if device is set)
        if client.trigger_device is not None:
            client.trigger_device.send_trigger()

        client.manager.print_on_server(f'Epoch {protocol_object.num_epochs_completed}')

        # Use the protocol object to send the stimulus to flystim
        protocol_object.load_stimuli(client)

        protocol_object.start_stimuli(client)

        client.manager.print_on_server('Epoch completed.')

        protocol_object.advance_epoch_counter()
