#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from nptdms import TdmsFile
import configparser
import skimage.io as io
import xml.etree.ElementTree as ET
import numpy as np


def getPoiData(poi_directory, poi_series_number, pmt = 1):
    poi_name = 'points' + ('0000' + str(poi_series_number))[-4:]
    full_file_path = os.path.join(poi_directory, 'points', poi_name, poi_name + '_pmt' + str(pmt) + '.tdms')

    try:
        tdms_file = TdmsFile(full_file_path)

        time_points = tdms_file.channel_data('PMT'+str(pmt),'POI time') #msec
        poi_data_matrix = np.ndarray(shape = (len(tdms_file.group_channels('PMT'+str(pmt))[1:]), len(time_points)))
        poi_data_matrix[:] = np.nan

        for poi_ind in range(len(tdms_file.group_channels('PMT'+str(pmt))[1:])): #first object is time points. Subsequent for POIs
            poi_data_matrix[poi_ind, :] = tdms_file.channel_data('PMT'+str(pmt), 'POI ' + str(poi_ind) + ' ')

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


def getSnapImage(poi_directory, snap_name, poi_xy, pmt = 1):
    full_file_path = os.path.join(poi_directory, 'snap', snap_name, snap_name[9:] + '_' + snap_name[:8] + '-snap-' + 'pmt'+str(pmt) + '.tif')
    if os.path.exists(full_file_path):
        snap_image = io.imread(full_file_path)

        roi_para_file_path = os.path.join(poi_directory, 'snap', snap_name,
                                          snap_name[9:] + '_' + snap_name[:8] + 'para.roi')
        roi_root = ET.parse(roi_para_file_path).getroot()
        ArrayNode = roi_root.find('{http://www.ni.com/LVData}Cluster/{http://www.ni.com/LVData}Array')
        snap_dims = [int(x.find('{http://www.ni.com/LVData}Val').text) for x in
                     ArrayNode.findall('{http://www.ni.com/LVData}I32')]

        snap_para_file_path = os.path.join(poi_directory, 'snap', snap_name,
                                           snap_name[9:] + '_' + snap_name[:8] + 'para.xml')

        with open(snap_para_file_path) as strfile:
            xmlString = strfile.read()
        french_parser = ET.XMLParser(encoding="ISO-8859-1")
        snap_parameters = ET.fromstring(xmlString, parser=french_parser)

        resolution = [int(float(x.find('{http://www.ni.com/LVData}Val').text)) for x in
                      snap_parameters.findall(".//{http://www.ni.com/LVData}DBL") if
                      x.find('{http://www.ni.com/LVData}Name').text == 'Resolution'][0]
        full_resolution = [int(float(x.find('{http://www.ni.com/LVData}Val').text)) for x in
                           snap_parameters.findall(".//{http://www.ni.com/LVData}DBL") if
                           x.find('{http://www.ni.com/LVData}Name').text == 'Resolution full'][0]

        snap_settings = {'snap_dims': snap_dims, 'resolution': resolution, 'full_resolution': full_resolution}

        # Poi xy locations are in full resolution space. Need to map to snap space
        poi_xy_to_resolution = poi_xy / (snap_settings['full_resolution'] / snap_settings['resolution'])
        poi_locations = (poi_xy_to_resolution - snap_settings['snap_dims'][0:2]).astype(int)

    else:
        snap_image = 0
        snap_settings = []
        poi_locations = []
        print('Warning no snap image found at: ' + full_file_path)

    return snap_image, snap_settings, poi_locations


def getRoiMapImage(poi_directory, poi_series_number, pmt = 1):
    poi_name = 'points' + ('0000' + str(poi_series_number))[-4:]
    full_file_path = os.path.join(poi_directory, 'points', poi_name, poi_name + '_pmt' + str(pmt) + '.jpeg')

    roi_image = io.imread(full_file_path)
    return roi_image
