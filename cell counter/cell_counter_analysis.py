#!/usr/bin/env python
import numpy as np
import pylab as mp
import glob

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

__author__ = 'benjamin lefaudeux'

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
        print len(mark)
        records.append(mark)

    return records

# Get the coordinates for the crypt and the vilosity
def ComputeMainAxis(records):
    vilosity = np.array(records[2])
    crypt_botton = np.array(records[0])
    crypt_top = np.array(records[1])

    return vilosity - crypt_top

# Compute the cell repartition with respect to the chosen referential, and show statistics
def ComputeCellCoordinates(records, main_axis, start):
    coord = np.empty((1,1))

    length = float(main_axis[0][0] * main_axis[0][0] + main_axis[0][1] * main_axis[0][1] + main_axis[0][2] * main_axis[0][2])

    for item in records[3]:
        pose = [item[0] - start[0], item[1] - start[1], item[2] - start[2]]
        coord_raw = int(pose[0] * main_axis[0][0]) + int(pose[1] * main_axis[0][1]) + int(pose[2] * main_axis[0][2])
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
    main_axis = ComputeMainAxis(records)
    return ComputeCellCoordinates(records, main_axis, records[0][0]) # records[0][0] : bas de la crypte, records[1][0] haut de la crypte

# Get all the XML files in this folder
files = glob.glob("/home/benjamin/Git/chest/cell counter/*.xml")

x = []
coord_ovrl = np.array(x)

for file in files:
    res = Pipeline(file)
    PlotHisto(res)

    coord_ovrl = np.append(coord_ovrl, res)

PlotHisto(coord_ovrl)

