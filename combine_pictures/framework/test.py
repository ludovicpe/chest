# -*- coding: utf-8 -*-
"""
Created on Sat May 17 17:20:49 2014

@author: malvache
"""

file = open('hygxyz.csv',"r")
i=0
for line in file:
     if i!=0 and i<2:
         parse=line.split(',')
         print(parse[7])
     i+=1