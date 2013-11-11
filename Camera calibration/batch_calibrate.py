# -*- coding: utf-8 -*-

#!/usr/bin/env python

"""
Created on Mon Nov 11 11:32:37 2013

@author: Benjamin Lefaudeux (blefaudeux at github)

This script uses OpenCV to calibrate a batch of cameras in one run.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import camera_calibration

class batchCalibration:
    def __init__(self):
        self.root_path      = ''
        self.folder_list    = []

        
        pass
    
    def calibrate():        
        # Get the root folder
        folder_read = False
    
        while not folder_read:
            path = raw_input("Root path for the calibration files : ")
            folder_read = self.readFolders(path)        
    
        
        # Get all the subfolders
        
        # Do all the subsequent calibrations and record the results


    def readFolders(self, path):
        # Get all the folders from this path
        pass 
    


# Run this script
run = batchCalibration()
run.calibrate()