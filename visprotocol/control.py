#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from PyQt5.QtWidgets import QApplication
import nidaqmx
import flyrpc.multicall

class EpochRun():
    def __init__(self):
        self.stop = False
        
    def stopRun(self):
        self.stop = True
        
    def startRun(self, protocol_object, data, client, save_metadata_flag = True):
        self.stop = False
        client.manager.set_idle_background(protocol_object.run_parameters['idle_color'])
        run_start_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]

        if save_metadata_flag:
            # create a new epoch run group in the data file
            data.reOpenExperimentFile()
            epochRuns = data.experiment_file['/epoch_runs']
            newEpochRun = epochRuns.create_group(str(data.series_count))
            newEpochRun.attrs['run_start_time'] = run_start_time
            for key in protocol_object.run_parameters: #save out run parameters as an attribute of this epoch run
                newEpochRun.attrs[key] = protocol_object.run_parameters[key]

            for key in data.fly_metadata: #save out fly metadata as an attribute of this epoch run
                newEpochRun.attrs[key] = data.fly_metadata[key]
                
            data.experiment_file.close()

        else:
            print('Warning - you are not saving your metadata!')
    
        # # # Epoch run loop # # #
        protocol_object.num_epochs_completed = 0
        for epoch in range(int(protocol_object.run_parameters['num_epochs'])):
            QApplication.processEvents()
            if self.stop is True:
                self.stop = False
                break
            
            #  get stimulus parameters for this epoch
            protocol_object.getEpochParameters()

            if save_metadata_flag:
                # update epoch metadata for this epoch
                data.reOpenExperimentFile()
                epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                newEpoch = data.experiment_file['/epoch_runs/' + str(data.series_count)].create_group('epoch_'+str(protocol_object.num_epochs_completed))
                newEpoch.attrs['epoch_time'] = epoch_time
                
                epochParametersGroup = newEpoch.create_group('epoch_parameters')
                for key in protocol_object.epoch_parameters: #save out epoch parameters
                    newValue = protocol_object.epoch_parameters[key]
                    if type(newValue) is dict: #TODO: Find a way to split this into subgroups. Hacky work around. 
                        newValue = str(newValue)
                    epochParametersGroup.attrs[key] = newValue
              
                convenienceParametersGroup = newEpoch.create_group('convenience_parameters')
                for key in protocol_object.convenience_parameters: #save out convenience parameters
                    convenienceParametersGroup.attrs[key] = protocol_object.convenience_parameters[key]
                data.experiment_file.close()

            if protocol_object.send_ttl:
                # Send a TTL pulse through the NI-USB to trigger acquisition
                with nidaqmx.Task() as task:
                    task.co_channels.add_co_pulse_chan_time("Dev5/ctr0",
                                                            low_time=0.002,
                                                            high_time=0.001)
                    task.start()


            # Use the protocol object to send the stimulus to flystim
            self.multicall = flyrpc.multicall.MyMultiCall(client.manager)
            protocol_object.loadStimuli(self.multicall)
            
            protocol_object.startStimuli(self.multicall)
            
            protocol_object.advanceEpochCounter()
            
        # # # Epoch run loop # # #
    