# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 21:54:19 2013

@author: benjamin lefaudeux
"""

import cv2          # OpenCV
import numpy as np  # Numpy, useful for any computation
import frameGrabber

def getUserChoice():
  """
  Get the video/pict choice from user
  """
  choose_type = False
  
  while (not choose_type):
    choice = raw_input("Video file (V), Pictures (P) or Webcam (W)")

    if ((choice == 'V') or (choice == 'v')):
      path = raw_input("File/folder path ? (keep empty for defaults)")
      frame_source = frameGrabber.videoFile(path)
      choose_type= True

    elif ((choice == 'P') or (choice == 'p')):
      path = raw_input("File/folder path ? (keep empty for defaults)")
      frame_source = frameGrabber.pictsFile(path)
      choose_type= True
        
    elif ((choice == 'W') or (choice == 'w')):
      frame_source = frameGrabber.webCam()      
      choose_type= True
      
  return frame_source

def run(n_max_frame):
  """
  The main part, parsing pict files or movie frames
  and combining them to enhance the pictures
  """
  # Parameters
  gamma = 0.8 # The gamma curve parameter.. lower value lightens the picture

  # Get the inputs
  frame_source = getUserChoice()

  # Process the stream frame by frame
  keep_going = True  
  i = 0
  
  while(keep_going):
    keep_going, frame = frame_source.newFrame()      
    
    # Initialize the accumulated frame
    if i==0:
        frame_acc = np.float32(frame)
        frame_acc_disp = np.float32(frame)
        frame_eq = np.float32(frame)
        cv2.equalizeHist(frame, frame_acc)
        cv2.normalize(frame_acc, frame_acc_disp, 0., 1., cv2.NORM_MINMAX) # just for the display stuff
        cv2.namedWindow('Raw frame', cv2.cv.CV_WINDOW_NORMAL)
        cv2.namedWindow('Processed frame', cv2.cv.CV_WINDOW_NORMAL)

    # Process frames :
    else :
        cv2.equalizeHist(frame, frame_eq)   # Kill black level before the accumulation
        cv2.accumulate(frame, frame_acc) # Just add pixel values
        cv2.normalize(np.power(frame_acc, gamma), frame_acc_disp, 0., 1., cv2.NORM_MINMAX)

    # Show results
    print "Showing frame {}".format(i)
    cv2.imshow('Raw frame', frame)
    cv2.resizeWindow('Raw frame', 800, 600)
    cv2.waitKey(5)
    cv2.imshow('Processed frame', frame_acc_disp)
    cv2.resizeWindow('Processed frame', 800, 600)
    cv2.waitKey(5)
    i = i + 1

    # Wait for key
    while(1) :
        k = cv2.waitKey(33)

        # Escape quits
        if (k==27):
            keep_going = False
            break

        # Space continues
        elif (k==32):
            break

  print "Bybye.."
  cv2.destroyAllWindows()

# Bam !
run(200)