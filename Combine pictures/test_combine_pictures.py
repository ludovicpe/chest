# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 21:54:19 2013

@author: benjamin lefaudeux
"""

import cv2          # OpenCV
import frameGrabber # Wrap the frame grabbing process
import frameFusion  # Wrap the frame accumulation process

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
    
    if not keep_going:
      print "Could not read frame"
      break
    
    else :
      # Bring the picture down to 1 channel
      frame_bw = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
      
      # Initialize the accumulated frame
      if i==0:
        frame_accumulator = frameFusion.frameFusion(frame_bw, gamma, False)     
          
      # Process frames :
      else :
        frame_accumulator.pileUp(frame_bw)        
        
      # Show results
      keep_going = frame_accumulator.show()
      i = i + 1
  
  print "Bybye.."
  cv2.destroyWindow('Raw frame')
  
  frame_source.release()

# Bam !
run(200)