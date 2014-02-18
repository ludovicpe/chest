# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 15:55:33 2013

@author: BLefaudeux
"""

import picamera


picam = picamera.PiCamera()

picam.capture('test_pict.jpg')

