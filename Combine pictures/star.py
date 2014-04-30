# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 15:44:33 2014

@author: malvache
"""

import pylab as pl

class Star:
    
    def __init__(self,name,ra,dec,mag):
        self.name = name
        self.ra = float(ra)
        self.dec = float(dec)
        self.mag = float(mag)
        
class StarList:

    def __init__(self):
        self.stars=[]

    def setData(self,filename):
        file = open(filename,"r")
        i=0
        for line in file:
            if i!=0 and i<120000:
                parse = line.split(',')
                self.stars.append(Star(parse[0],parse[7],parse[8],parse[13]))    
            i+=1
    
    def saveData(self,filename):
        pass
        # Save as binary file
        # file = open(filename,"w")
        # file.write()
        
    def loadData(self,filename):
        pass
        # Load binary file
        
star_list = StarList()
star_list.setData('hygxyz.csv')
mpl.figure