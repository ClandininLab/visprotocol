#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication
import nidaqmx
import flyrpc.multicall

class EpochRun():
    def __init__(self):
        self.stop = False
        
    def stopRun(self):
        self.stop = True
        QApplication.processEvents()
        
    def startRun(self, protocol_object, data, client, save_metadata_flag = True):
        self.stop = False
        client.manager.set_idle_background(protocol_object.run_parameters['idle_color'])
        
        if save_metadata_flag:
            protocol_object.saveEpochRunMetaData(data)
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
               protocol_object.saveEpochMetaData(data)

            if protocol_object.send_ttl:
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
            self.multicall = flyrpc.multicall.MyMultiCall(client.manager)
            protocol_object.loadStimuli(self.multicall)
            
            protocol_object.startStimuli(self.multicall)
            
            protocol_object.advanceEpochCounter()
            
        # # # Epoch run loop # # #
    