# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 15:44:33 2014

@author: malvache
"""

import pylab as pl
from math import *

def rotate(x, y, alpha):
    x1 = x*cos(alpha)-y*sin(alpha)
    y1 = y*cos(alpha)+x*sin(alpha)
    return (x1, y1)

class Star:
    
    def __init__(self, name, ra, dec, mag):
        self.name = name
        self.ra = float(ra)
        self.dec = float(dec)
        self.mag = float(mag)
    
    def stereoProj(self, info):
#        earth_angle = 22*pi/180
        realYear = 365.25
        #Parameters
        azm = info[0]
        alt = info[1]
        lon = info[2]
        lat = info[3]
        day = info[4]
        hour = info[5]
        eq = 80 #num of winter equinox day
        
        # From astro coord to spherical coord
        th = self.ra*15*pi/180 # th in radiant
        phi = pi - (pi/2 - self.dec*pi/180) # phi in radiant
        
        # From spherical to cartesian
        ### to do : drift in time (ref time 20000321)
        xCart = sin(phi)*cos(th)
        yCart = sin(phi)*sin(th)
        zCart = cos(phi)
        
        # Transform to location and date
        # Rotation about z axis (local time)
        delta = - hour*15*pi/180 - 2*pi*(day-eq)/realYear - lon
        (xCarta, yCarta) = rotate(xCart, yCart, delta)
        zCarta = zCart
        # Rotation about y axis (to put zenith in the right dir)
        gamma = lat-pi/2 #deviation from equator
        yCartb = yCarta
        (zCartb, xCartb) = rotate(zCarta, xCarta, gamma)
        
        # Transform to direction of observation
        # Rotation about z axis (to put phi in the right dir)       
        alpha = azm #th of direction
        (xCart1, yCart1) = rotate(xCartb, yCartb, alpha)
        zCart1 = zCartb
        # Rotation about new y axis (rotation of phi)       
        beta = pi/2-alt #phi of direction
        (zCart2, xCart2) = rotate(zCart1, xCart1, beta)
        yCart2 = yCart1
        
        # Create map from cartesian to stereographic
        if zCart2==1:
            xStereo = 100
            yStereo = 100
        else:    
            yStereo = -xCart2/(1-zCart2)
            xStereo = -yCart2/(1-zCart2)
        return (xStereo, yStereo)
        
class StarList:

    def __init__(self):
        self.stars = []
    
    #Get data from database
    def setData(self,filename):
        file = open(filename,"r")
        i=0
        for line in file:
            if i!=0 and i<120000:
                parse = line.split(',')
                self.stars.append(Star(parse[0], parse[7], parse[8], parse[13]))    
            i+=1
    
    def saveData(self, filename):
        pass
        # Save as binary file
        # file = open(filename,"w")
        # file.write()
        
    def loadData(self, filename):
        pass
        # Load binary file
    
    def hist(self):#magnitudes histogram
        #x=range(len(self.stars))
        y = []
        for star in self.stars:
            y.append(star.mag) #incrémente automatiquement
        pl.figure(1)
        pl.hist(y, 200)
        
    #Plot stars with a condition of magnitude
    #Sky depends on localisation (lat), date (day) and direction of observation (dir)
    def sky(self, mag1, mag2, info):
        pl.figure(2)
        self.plot(mag1, -30, 'ro', info)
        self.plot(mag2, mag1, 'r+', info)
        UMa=[67089,65174,62758,59593,57829,53754,53905] # Ursa Major
        Cet=[3413]
        star_list.constellation(UMa, 'bo', info) # Show constellation
        star_list.constellation(Cet, 'bo', info)        
        
    def plot(self, mag1, mag2, style, info):
        x = []
        y = []
        for star in self.stars:
            if star.mag<mag1 and star.mag>mag2:
                (xtmp, ytmp)=star.stereoProj(info)
                x.append(xtmp)
                y.append(ytmp)
        pl.plot(x, y, style)
        
    def constellation(self, num, style, info):
        x = []
        y = []
        for i in num:
            (xtmp, ytmp) = self.stars[i].stereoProj(info)
            x.append(xtmp)
            y.append(ytmp)
        pl.plot(x, y, style)

# Create starList from database            
star_list = StarList()
star_list.setData('hygxyz.csv')
# star_list.hist()

# User info
#Direction of observation (azm,alt) in radiant
azm = 3*pi/2 # 0: North, pi: South
alt = pi/6 # 0: horizon, pi/2: zenith
#Position (lon,lat) in radiant
lon = (30+46./60)*pi/180#(2+20./60)*pi/180 # >0 for East and <0 for West ???
lat = (46+30./60)*pi/180 # >0 for North and <0 for South
#Date (day,hour)
year = 2014
day = 46 #num of the day 1-366
hour = 18
#Group info
#Normalize by reference date 2000 03 21 at 00 UT
numDay = day + (year-2000)*365+(year-2000)/4 #bissextile years
info=[azm, alt, lon, lat, numDay, hour]

# Show sky
star_list.sky(3, 5, info)
pl.axis([-0.5, 0.5, -0.5, 0.5])
pl.show()