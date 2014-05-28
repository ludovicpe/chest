#!/usr/bin/env python

import utils

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

__author__ = 'benjamin lefaudeux'

# Parse the XML file
def parseCellXML(file):
    tree = ET.parse(file).getroot()

    for type in tree.findall('Marker_Data/Marker_Type'):
        print type.find('Type').text

        for marker in type.findall('Marker'):
            print "Coordinate : {}".format(marker.find('MarkerX').text)

# TODO

# Get the coordinates for the crypt and the vilosity
# TODO

# Compute the cell repartition with respect to the chosen referential, and show statistics

# The overall program
parseCellXML('CellCounter_Counter Window - C0136 0002.xml')
