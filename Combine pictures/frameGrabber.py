# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 12:07:45 2013

@author: benjamin lefaudeux
"""
import cv2
import os
import utils as ut
import numpy as np

"""
  The overall frameGrabber class, from which all our sub-classes inherit
"""
# TODO : use virtual methods instead ?
class frameGrabber:  
  n_frame       = 0
  n_max_frames  = 0
  size_x        = 0
  size_y        = 0  
  
  def __init__(self):
    # The default constructor
    self.n_frames     = 0
    self.n_max_frames = 0
    self.size_x       = 0
    self.size_y       = 0  
    
    return 'New empty frame grabber'

  def showPictInWindow(self, pict):
    cv2.namedWindow("Show")
    cv2.imshow("Show", pict)  

    k = cv2.waitKey(33)
    # Escape quits
    if (k==27):
        b_quit = False
  
class videoFile(frameGrabber):
  # The constructor : get a handle on a video file
  def __init__(self, filename):
    self.n_frames   = 0
    self.capture    = cv2.VideoCapture(filename)
    self.keep_going = True
    
  # Get a new frame
  def newFrame(self):
    if (self.keep_going):  
      self.keep_going, self.frame = self.capture.read()    
      self.n_frame = self.n_frame + 1  
      return [True, self.frame]
  
    else :
      return [False, []]
  
  def show(self):
    frameGrabber.showPictInWindow(self.frame)
  
class webCam(frameGrabber):
  def __init__(self, device_id = 0):
    self.n_frames = 0
    self.cam = cv2.VideoCapture(device_id)
    
    if self.cam.isOpened():
      self.cam.release()
      
    self.cam.open(device_id)
    self.keep_going = True


  def newFrame(self):
    if self.keep_going :
      self.keep_going,self.frame_last = self.cam.read()
      return [True, self.frame_last]
      
    else:
      self.cam.release()
      return [False, []]      
      
  def show(self):
    b_quit = False
    
    while not b_quit:
      self.frame = self.newFrame()
      frameGrabber.showPictInWindow(self, self.frame)

class pictsFile(frameGrabber):
  # The constructor : get a list of all the frames, and the number of frames 
  def __init__(self, folder):
    [self.pict_list, self.n_max_frames] = self.getPictFiles(folder)    
    self.n_frames = 0    
    
  def newFrame(self):
    if self.n_frames < (self.n_max_frames-1):
      self.n_frames = self.n_frames + 1
      return [True, self.pict_list[self.n_frames]]
    
    else : 
      return [False, []]
    
  def getPictFiles(self, folder):
      """
      Get all the picture files in the folder
      """
  
      folder_path = os.path.abspath(folder)
  
      if not os.path.isdir(folder_path):
          print "Trouble reading folder path {}".format(folder_path)
  
      picture_list = []
      n_files = 0
  
      for dirname, dirnames, filenames in os.walk(folder_path):
  
          filenames = ut.sort_nicely(filenames)
  
          for filename in filenames:
              print "Reading file {}".format(filename)
  
              full_filepath = os.path.join(folder_path, filename)
  
              if (filename[-3:] == "bmp") or \
                  (filename[-3:] == "png") or \
                  (filename[-3:] == "jpg") :
  
                  try:
                      picture_list.append(cv2.imread(full_filepath, cv2.CV_LOAD_IMAGE_GRAYSCALE))
                      if (picture_list[n_files] == None) :
                          picture_list.pop()
                          print "Error loading file {}".format(filename)
                      else :
                          n_files = n_files + 1
  
                  except:
                      print "Error loading file {}".format(filename)
  
      return picture_list, n_files



  
  