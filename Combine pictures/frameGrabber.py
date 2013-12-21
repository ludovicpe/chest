# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 12:07:45 2013

@author: benjamin lefaudeux
"""
import cv2
import os
import utils as ut


"""
  The overall frameGrabber class, from which all our sub-classes inherit
"""
# TODO : use virtual methods instead
class frameGrabber:  
  def __init__(self):
    # The default constructor
    self.n_frames     = 0
    self.n_max_frames = 0
    self.size_x       = 0
    self.size_y       = 0  
    
    return 'New empty framer grabber'
  
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
      return self.frame
  
    else :
      return False
  
class webCam(frameGrabber):
  pass

class pictsFile(frameGrabber):
  # The constructor : get a list of all the frames, and the number of frames 
  def __init__(self, folder):
    [self.pict_list, self.n_max_frames] = self.getPictFiles(folder)    
    self.n_frames = 0    
    
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



  
  