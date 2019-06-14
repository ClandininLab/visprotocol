#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data parent class. Override any methods in here in the user data subclass
"""
import h5py
import os
import shutil
import inspect
import yaml
import socket
from datetime import datetime
from nptdms import TdmsFile
import numpy as np
import configparser
import skimage.io as io
import xml.etree.ElementTree as ET
import re

import visprotocol

class Data():
    def __init__(self, user_name):
        self.experiment_file = None
        self.experiment_file_name = None
        self.series_count = 1
        self.fly_metadata = {}  # populated in GUI or user protocol
        
        #load user config file based on user name
        path_to_config_file = os.path.join(inspect.getfile(visprotocol).split('visprotocol')[0], 'visprotocol', 'config', user_name + '_config.yaml')
        with open(path_to_config_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)

        # # # Other metadata defaults # # #
        self.experimenter = cfg.get('experimenter', '')
    
        # # #  Lists of fly metadata # # # 
        self.prepChoices = cfg.get('prep_choices', [])
        self.driverChoices = cfg.get('driver_choices', [])
        self.indicatorChoices = cfg.get('indicator_choices', [])
        
        # # #  Poi name options # # # 
        self.poiNames = cfg.get('poi_names', [])
           
        #load rig-specific metadata things
        if socket.gethostname() == 'DESKTOP-4Q3O7LU':  # AODscope Karthala
            self.data_directory = 'D:/Max/FlystimData'
            self.rig = 'AODscope'
        elif socket.gethostname() == 'USERBRU-I10P5LO':  # Bruker
            self.data_directory = 'E:/Max/FlystimData/'
            self.rig = 'Bruker'
        else:
            self.data_directory = os.getcwd()
            self.rig = '(rig)'

    def initializeExperimentFile(self):
        # Create HDF5 file
        self.experiment_file = h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), 'w-')
        
        # Experiment date/time
        init_now = datetime.now()
        date = init_now.isoformat()[:-16]
        init_time = init_now.strftime("%H:%M:%S")
        
        # Write experiment metadata as top-level attributes
        self.experiment_file.attrs['date'] = date;
        self.experiment_file.attrs['init_time'] = init_time;
        self.experiment_file.attrs['data_directory'] = self.data_directory;
        self.experiment_file.attrs['experimenter'] = self.experimenter;
        self.experiment_file.attrs['rig'] = self.rig;
        
        # Create a top-level group for epoch runs and user-entered notes
        self.experiment_file.create_group('epoch_runs')
        self.experiment_file.create_group('notes')
        self.experiment_file.create_group('client') # TODO: figure out what to save here...
        self.experiment_file.close()
        
    def saveEpochRunMetaData(self, protocol_object):
        # create a new epoch run group in the data file
        run_start_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.reOpenExperimentFile()
        epochRuns = self.experiment_file['/epoch_runs']
        newEpochRun = epochRuns.create_group(str(self.series_count))
        newEpochRun.attrs['run_start_time'] = run_start_time
        for key in protocol_object.run_parameters: #save out run parameters as an attribute of this epoch run
            newEpochRun.attrs[key] = protocol_object.run_parameters[key]

        for key in self.fly_metadata: #save out fly metadata as an attribute of this epoch run
            newEpochRun.attrs[key] = self.fly_metadata[key]
            
        # save poi metadata
        poi_parent_group = newEpochRun.require_group("pois") #opens group if it exists or creates it if it doesn't
        for current_tag in self.poi_metadata:
            current_poi_group = poi_parent_group.require_group(current_tag)
            current_poi_group.create_dataset("poi_numbers", data = self.poi_metadata[current_tag])
            
        self.experiment_file.close()
        
    def saveEpochMetaData(self,protocol_object):
        # update epoch metadata for this epoch
        self.reOpenExperimentFile()
        epoch_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        newEpoch = self.experiment_file['/epoch_runs/' + str(self.series_count)].create_group('epoch_'+str(protocol_object.num_epochs_completed))
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
        self.experiment_file.close()

    def addNoteToExperimentFile(self, noteText):
        noteTime = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.reOpenExperimentFile()
        notes = self.experiment_file['/notes']
        notes.attrs[noteTime] = noteText
        self.experiment_file.close()


    def reOpenExperimentFile(self, mode = 'r+'):
        self.experiment_file = h5py.File(os.path.join(self.data_directory, self.experiment_file_name + '.hdf5'), mode)
        
    def advanceSeriesCount(self):
        self.series_count += 1
        
    def getExistingPoiData(self):
        # return list of poi sets already present in experiment file
        poi_data_list = []
        if self.experiment_file is not None:
            self.reOpenExperimentFile(mode = 'r')
            for er in self.experiment_file['/epoch_runs']:
                new_pois = self.experiment_file['/epoch_runs'][er]['pois']
                tg = []
                rg = []
                for k in new_pois:
                    tg.append(k)
                    new_range = str(new_pois.get(k).get('poi_numbers')[:])
                    interpreted_range = re.sub(' +', ' ', re.sub('\[|\]','', new_range)).strip().replace(' ',',')
                    rg.append(interpreted_range)
                    
                new_dict = {'tag': tg, 'range': rg}
                
                if new_dict in poi_data_list:
                    pass
                else:
                    poi_data_list.append(new_dict)
                
            id_val = 0
            for ind in range(len(poi_data_list)):
                id_val+=1
                poi_data_list[ind]['poi_id'] = str(id_val)
                
            poi_data_list = sorted(poi_data_list, key = lambda i: i['poi_id'])
                
            self.experiment_file.close()
        
        return poi_data_list
            
    def getExistingFlyData(self):
        # return list of dicts for fly metadata already present in experiment file
        fly_data_list = []
        if self.experiment_file is not None:
            self.reOpenExperimentFile(mode = 'r')
            for er in self.experiment_file['/epoch_runs']:
                new_run = self.experiment_file['/epoch_runs'][er]
                new_dict = {}
                for at in new_run.attrs:
                    if 'fly' in at:
                        new_dict[at] = new_run.attrs[at]
                
                if new_dict in fly_data_list:
                    pass
                else:
                    fly_data_list.append(new_dict)
            
            fly_data_list = sorted(fly_data_list, key = lambda i: i['fly:fly_id'])
    
            self.experiment_file.close()
        
        return fly_data_list

# # # # # # # Tools for random access scan data # # # # # # # # # # # # # # # # # # # # # # #             
    def attachPoiData(self, poi_directory):
        if self.experiment_file is not None:
            #make a backup copy first
            file_base = os.path.join(self.data_directory, self.experiment_file_name)
            backup_path = file_base + '_backup' + '.hdf5'
            ct = 0
            while os.path.isfile(backup_path):
                ct+=1
                backup_path = file_base + '_backup' + str(ct) + '.hdf5'
            shutil.copyfile(file_base + '.hdf5', backup_path)
            
            #Attach poi data according to poi names/ranges (if provided)
            self.reOpenExperimentFile()
            for er in list(self.experiment_file.get('epoch_runs').keys()):
                current_run = self.experiment_file.get('epoch_runs')[er]
                poi_parent_group = current_run.require_group('pois')
                poi_series_number = int(er)
                time_points, poi_data_matrix, poi_xy = getPoiData(poi_directory, poi_series_number, pmt = 1)
                photodiode_time, photodiode_input = getPhotodiodeSignal(poi_directory, poi_series_number)
                if time_points is None:
                    print('No POI data found for Series ' + str(er))
                    continue
                
                if poi_parent_group.get('poi_data_matrix'): #poi dataset exists already. Delete and overwrite
                    del poi_parent_group['poi_data_matrix']
                if poi_parent_group.get('time_points'):
                    del poi_parent_group['time_points']
                
                poi_parent_group.create_dataset("time_points", data = time_points)
                poi_parent_group.create_dataset("poi_data_matrix", data = poi_data_matrix)
                if photodiode_time is not None:
                    poi_parent_group.create_dataset("photodiode_time", data = photodiode_time)
                    poi_parent_group.create_dataset("photodiode_input", data = photodiode_input)
                    
                
                
                # attach random access scan configuration settings as attributes
                config_dict = getRandomAccessConfigSettings(poi_directory, poi_series_number)
                for outer_k in config_dict.keys():
                    for inner_k in config_dict[outer_k].keys():
                        poi_parent_group.attrs[outer_k + '/' + inner_k] = config_dict[outer_k][inner_k]
                        
                # attach poi map jpeg and Snap Image
                snap_name = config_dict['Image']['name'].replace('"','')
                ct=0
                while ('points' in snap_name) or (ct < 100): #used snap image from a previous POI scan
                    ct+=1
                    alt_dict = getRandomAccessConfigSettings(poi_directory, int(snap_name[6:]))
                    temp_image = alt_dict.get('Image')
                    if temp_image is not None:
                        snap_name = temp_image['name'].replace('"','')
                    
                snap_image, snap_settings = getSnapImage(poi_directory, snap_name, pmt = 1)
                
                roi_map = getRoiMapImage(poi_directory, poi_series_number)
                poi_parent_group.create_dataset("poi_map", data = roi_map)
                poi_parent_group.create_dataset("snap_image", data = snap_image)
                # Poi xy locations are in full resolution space. Need to map to snap space
                poi_xy_to_resolution =  poi_xy / (snap_settings['full_resolution'] / snap_settings['resolution'])
                poi_to_snap = (poi_xy_to_resolution - snap_settings['snap_dims'][0:2]).astype(int)
                poi_parent_group.create_dataset("poi_locations", data = poi_to_snap)

                print('Series ' + str(er) + ': added POI data')
            
            self.experiment_file.close()
        else:
            print('No experiment file assigned yet')

    
def getPoiData(poi_directory, poi_series_number, pmt = 1):
    poi_name = 'points' + ('0000' + str(poi_series_number))[-4:]
    full_file_path = os.path.join(poi_directory, 'points', poi_name, poi_name + '_pmt' + str(pmt) + '.tdms')
    
    try:
        tdms_file = TdmsFile(full_file_path)
        
        time_points = tdms_file.channel_data('PMT'+str(pmt),'POI time') #msec
        poi_data_matrix = np.ndarray(shape = (len(tdms_file.group_channels('PMT'+str(pmt))[1:]), len(time_points)))
        poi_data_matrix[:] = np.nan
        
        for poi_ind in range(len(tdms_file.group_channels('PMT'+str(pmt))[1:])): #first object is time points. Subsequent for POIs
            poi_data_matrix[poi_ind,:] = tdms_file.channel_data('PMT'+str(pmt),'POI ' + str(poi_ind) + ' ')


        # get poi locations:
        poi_x = [int(v) for v in tdms_file.channel_data('parameter','parameter')[21:]]
        poi_y = [int(v) for v in tdms_file.channel_data('parameter','value')[21:]]
        poi_xy = np.array(list(zip(poi_x, poi_y)))
    except:
        time_points = None
        poi_data_matrix = None
        print('No tdms file found at: ' + full_file_path)
        
    return time_points, poi_data_matrix, poi_xy

def getPhotodiodeSignal(poi_directory, poi_series_number):
    poi_name = 'points' + ('0000' + str(poi_series_number))[-4:]
    full_file_path = os.path.join(poi_directory, 'points', poi_name, poi_name + '-AnalogIN.tdms')
    
    if os.path.exists(full_file_path):
        tdms_file = TdmsFile(full_file_path)
        try:
            time_points = tdms_file.object('external analogIN', 'AnalogGPIOBoard/ai0').time_track()
            analog_input = tdms_file.object('external analogIN', 'AnalogGPIOBoard/ai0').data
        except:
            time_points = None
            analog_input = None
            print('Analog input file has unexpected structure: ' + full_file_path)
    else:
        time_points = None
        analog_input = None
        print('No analog_input file found at: ' + full_file_path)
        
    return time_points, analog_input

def getRandomAccessConfigSettings(poi_directory, poi_series_number):
    poi_name = 'points' + ('0000' + str(poi_series_number))[-4:]
    full_file_path = os.path.join(poi_directory, 'points', poi_name, poi_name + '.ini')
    
    config = configparser.ConfigParser()
    config.read(full_file_path)
    
    config_dict = config._sections
    
    return config_dict

def getSnapImage(poi_directory, snap_name, pmt = 1):
    full_file_path = os.path.join(poi_directory, 'snap', snap_name, snap_name[9:] + '_' + snap_name[:8] + '-snap-' + 'pmt'+str(pmt) + '.tif')
    if os.path.exists(full_file_path):
        snap_image = io.imread(full_file_path)
    else:
        snap_image = 0
        print('Warning no snap image found atL ' + full_file_path)
    
    roi_para_file_path = os.path.join(poi_directory, 'snap', snap_name, snap_name[9:] + '_' + snap_name[:8] + 'para.roi')
    roi_root = ET.parse(roi_para_file_path).getroot()
    ArrayNode = roi_root.find('{http://www.ni.com/LVData}Cluster/{http://www.ni.com/LVData}Array')
    snap_dims = [int(x.find('{http://www.ni.com/LVData}Val').text) for x in ArrayNode.findall('{http://www.ni.com/LVData}I32')]
    
    snap_para_file_path = os.path.join(poi_directory, 'snap', snap_name, snap_name[9:] + '_' + snap_name[:8] + 'para.xml')
    
    with open(snap_para_file_path) as strfile:
        xmlString = strfile.read()
    french_parser = ET.XMLParser(encoding="ISO-8859-1")
    snap_parameters = ET.fromstring(xmlString, parser = french_parser)
    
    resolution = [int(float(x.find('{http://www.ni.com/LVData}Val').text)) for x in snap_parameters.findall(".//{http://www.ni.com/LVData}DBL") if x.find('{http://www.ni.com/LVData}Name').text == 'Resolution'][0]
    full_resolution = [int(float(x.find('{http://www.ni.com/LVData}Val').text)) for x in snap_parameters.findall(".//{http://www.ni.com/LVData}DBL") if x.find('{http://www.ni.com/LVData}Name').text == 'Resolution full'][0]
     
    snap_settings = {'snap_dims':snap_dims, 'resolution': resolution, 'full_resolution': full_resolution}
    
    return snap_image, snap_settings
    
def getRoiMapImage(poi_directory, poi_series_number, pmt = 1):
    poi_name = 'points' + ('0000' + str(poi_series_number))[-4:]
    full_file_path = os.path.join(poi_directory, 'points', poi_name, poi_name + '_pmt' + str(pmt) + '.jpeg')
    
    roi_image = io.imread(full_file_path)
    return roi_image
