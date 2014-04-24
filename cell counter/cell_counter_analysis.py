#!/usr/bin/env python
import numpy as np
import pylab as mp
import glob
import os

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# Parse the XML file
def ParseCellXML(file):
    tree = ET.parse(file).getroot()

    records = []

    for type in tree.findall('Marker_Data/Marker_Type'):
        mark = []

        for marker in type.findall('Marker'):
            x = int(marker.find('MarkerX').text)
            y = int(marker.find('MarkerY').text)
            z = int(marker.find('MarkerZ').text)
            mark.append([x, y, z])

        records.append(mark)

    return records

# Get the coordinates for the crypt and the vilosity
def ComputeMainAxis(records):
    vilosity = np.array(records[2])
    crypt_botton = np.array(records[0])
    crypt_top = np.array(records[1])
    main_axis = vilosity - crypt_top

    return main_axis

# Compute the cell repartition with respect to the chosen referential, and show statistics
def ComputeCellCoordinates(records, main_axis, start):
    coord = np.empty((1,1))

    length = float(main_axis[0] * main_axis[0] + main_axis[1] * main_axis[1] + main_axis[2] * main_axis[2])

    for item in records[3]:
        pose = [item[0] - start[0], item[1] - start[1], item[2] - start[2]]
        coord_raw = int(pose[0] * main_axis[0]) + int(pose[1] * main_axis[1]) + int(pose[2] * main_axis[2])
        coord_normalized = coord_raw / length
        coord = np.append( coord, coord_normalized)
    return coord

# Plot an histogram
def PlotHisto(coords):
    mp.figure()
    mp.hist(coords, 30)
    mp.show()

# Pipeline for one file
def Pipeline(file):
    records = ParseCellXML(file)
    if len(records) > 0:
        main_axis = ComputeMainAxis(records)
        return ComputeCellCoordinates(records, main_axis[0], records[0][0]) # records[0][0] : bas de la crypte, records[1][0] haut de la crypte
    else:
        return []

# Get all the XML files in this folder and plot
def FolderPipeline(folder):
    coord_ovrl = np.array([])

    files = glob.glob(folder + "/*.xml")

    file_exist = False

    for file in files:
        res = Pipeline(file)
        # PlotHisto(res)
        coord_ovrl = np.append(coord_ovrl, res)
        if len(res) >0:
            file_exist = True

    if file_exist:
        mp.figure()
        mp.hist(coord_ovrl, 30)
        mp.savefig(folder + '/histogram.png', bbox_inches='tight')
        mp.show()
        
# Get all the subfolders and plot
dirList = os.listdir("./") # current directory

for dir in dirList:
  if os.path.isdir(dir) == True:
        FolderPipeline(dir)