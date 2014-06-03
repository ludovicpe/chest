# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 15:55:33 2013

@author: malvache
"""

import sys
sys.path.insert(0, '../framework')

from star import *

# Create starList from database
star_list = StarList()
star_list.setData('../data/hygxyz.csv')
# star_list.hist()

# User info
#Direction of observation (azm,alt) in radiant
azm = 3*pi/2 # 0: North, pi: South
alt = pi/6 # 0: horizon, pi/2: zenith
#Position (lon,lat) in radiant
lon = (12+34./60)*pi/180#(2+20./60)*pi/180 # >0 for East and <0 for West ???
lat = (55+40./60)*pi/180 # >0 for North and <0 for South
#Date (day,hour)
year = 2014
day = 154 #num of the day 1-366
hour = 20
#Group info
#Normalize by reference date 2000 03 21 at 00 UT
numDay = day + (year-2000)*365+(year-2000)/4 #bissextile years
info=[azm, alt, lon, lat, numDay, hour]

# Show sky
star_list.sky(3, 5, info)
pl.axis([-0.5, 0.5, -0.5, 0.5])
pl.show()
