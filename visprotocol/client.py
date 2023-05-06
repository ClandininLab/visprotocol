#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
import posixpath
from PyQt5.QtWidgets import QApplication

from flyrpc.transceiver import MySocketClient
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from visprotocol.util import config_tools

class BaseClient():
    def __init__(self, cfg):
        self.stop = False
        self.pause = False
        self.cfg = cfg
        
        # # # Load server options from config file and selections # # #
        self.server_options = config_tools.get_server_options(self.cfg)
        self.trigger_device = config_tools.load_trigger_device(self.cfg)

        # # # Start the stim manager and set the frame tracker square to black # # #
        if self.server_options['use_server']:
            self.manager = MySocketClient(host=self.server_options['host'], port=self.server_options['port'])
        else:
            aux_screen = Screen(server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0.25, 0.25))
            self.manager = launch_stim_server(aux_screen)

        self.manager.black_corner_square()
        self.manager.set_idle_background(0)

    def stop_run(self):
        self.stop = True
        QApplication.processEvents()

    def pause_run(self):
        self.pause = True
        QApplication.processEvents()

    def resume_run(self):
        self.pause = False
        QApplication.processEvents()

    def start_run(self, protocol_object, data, save_metadata_flag=True):
        """
        Required inputs: protocol_object, data
            protocol_object defines the protocol and associated parameters to be used
            data handles the metadata file
        """
        self.stop = False
        self.pause = False
        protocol_object.save_metadata_flag = save_metadata_flag

        # Precompute useful variables prior to epoch run loop
        protocol_object.precompute_variables()

        # Check that all required run parameters are set
        protocol_object.check_required_run_parameters()
        
        # Set background to idle_color
        self.manager.set_idle_background(protocol_object.run_parameters['idle_color'])

        if save_metadata_flag:
            data.create_epoch_run(protocol_object)
        else:
            print('Warning - you are not saving your metadata!')

        # Set up locomotion data saving on the server and start locomotion device / software
        if protocol_object.loco_available and protocol_object.run_parameters['do_loco']:
            self.start_loco(data, save_metadata_flag=save_metadata_flag)
            
        # Trigger acquisition of scope and cameras by send triggering TTL through the DAQ device (if device is set)
        if protocol_object.trigger_on_epoch_run is True:
            if self.trigger_device is not None:
                print("Triggering acquisition devices.")
                self.trigger_device.send_trigger()

        # Start locomotion loop on the server only if closed_loop is an option for the protocol.
        if protocol_object.loco_available and protocol_object.run_parameters['do_loco'] and 'loco_pos_closed_loop' in protocol_object.protocol_parameters:
            self.start_loco_loop()

        # # # Epoch run loop # # #
        self.manager.print_on_server("Starting run.")
        protocol_object.num_epochs_completed = 0
        while protocol_object.num_epochs_completed < protocol_object.run_parameters['num_epochs']:
            QApplication.processEvents()
            if self.stop is True:
                self.stop = False
                break # break out of epoch run loop

            if self.pause is True:
                pass # do nothing until resumed or stopped
            else: # start epoch and advance counter
                self.start_epoch(protocol_object, data, save_metadata_flag=save_metadata_flag)

        # Set frame tracker to dark
        self.manager.black_corner_square()

        # Stop locomotion device / software
        if protocol_object.loco_available and protocol_object.run_parameters['do_loco']:
            self.stop_loco()

        self.manager.print_on_server('Stopping run.')

    def start_epoch(self, protocol_object, data, save_metadata_flag=True):
        #  get stimulus parameters for this epoch
        protocol_object.get_epoch_parameters()
        
        # Check that all required epoch protocol parameters are set
        protocol_object.check_required_epoch_protocol_parameters()

        if save_metadata_flag:
            data.create_epoch(protocol_object)

        # Send triggering TTL through the DAQ device (if device is set)
        if protocol_object.trigger_on_epoch is True:
            if self.trigger_device is not None:
                print("Triggering acquisition devices.")
                self.trigger_device.send_trigger()

        self.manager.print_on_server(f'Epoch {protocol_object.num_epochs_completed}')

        # Use the protocol object to send the stimulus to flystim
        protocol_object.load_stimuli(self.manager)

        protocol_object.start_stimuli(self.manager)

        self.manager.print_on_server('Epoch completed.')

        if save_metadata_flag:
            data.end_epoch(protocol_object)
        
        protocol_object.advance_epoch_counter()

    #%% Locomotion methods
    def start_loco(self, data, save_metadata_flag=True):
        '''
        Set up locomotion data saving on the server and start locomotion device / software
        '''
        if save_metadata_flag:
            server_data_directory = self.server_options.get('data_directory', None)
            if server_data_directory is not None:
                # set server-side directory in which to save animal positions from each screen.
                server_series_dir = posixpath.join(server_data_directory, data.experiment_file_name, str(data.series_count))
                server_pos_history_dir = posixpath.join(server_series_dir, 'flystim_pos')
                self.manager.set_save_pos_history_dir(server_pos_history_dir)

                # set server-side directory in which to save locomotion data
                server_loco_dir = posixpath.join(self.server_series_dir, 'loco')
                self.manager.loco_set_save_directory(server_loco_dir)
            else:
                print("Warning: Locomotion data won't be saved without server's data_directory specified in config file.")
        self.manager.loco_start()
        sleep(3) # Give locomotion device / software time to load
    
    def start_loco_loop(self):
        '''
        Start locomotion loop on the server for closed-loop updating
        '''
        sleep(2) # Give loco time to start acquiring
        self.manager.loco_loop_start() # start loop, which is superfluous if closed loop is not needed for the exp.
        
    def stop_loco(self):
        self.manager.loco_close()
        self.manager.loco_set_save_directory(None)
    