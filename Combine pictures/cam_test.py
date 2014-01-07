# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 15:55:33 2013

@author: Abid Rahman K
"""

import cv2

c = cv2.VideoCapture(0)

cv2.namedWindow('e2');

while(1):
    _,f = c.read()
    cv2.imshow('e2',f)
    if cv2.waitKey(5)==27:
        break
      
c.release()
cv2.destroyAllWindows()