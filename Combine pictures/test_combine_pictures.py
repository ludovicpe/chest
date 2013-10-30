# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 21:54:19 2013

@author: arnaud malvache, benjamin lefaudeux
"""

import cv2      # OpenCV
import numpy as np  # Numpy, useful for any computation
import os       # Get files in a folder,..
import re       # Sort filenames


def sort_nicely(l ):
  """ Sort the given list in the way that humans expect.
  """
  convert = lambda text: int(text) if text.isdigit() else text
  alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
  l.sort( key=alphanum_key )
  return l

def getVideoFile(filename):
    """
    Just a wrapper to openCV file handle
    """
    capture = cv2.VideoCapture(filename)

    return capture

def getPictFiles(folder):
    """
    Get all the picture files in the folder
    """

    folder_path = os.path.abspath(folder)

    if not os.path.isdir(folder_path):
        print "Trouble reading folder path {}".format(folder_path)

    picture_list = []
    n_files = 0

    for dirname, dirnames, filenames in os.walk(folder_path):

        filenames = sort_nicely(filenames)

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

def getUserChoice():
    """
    Get the video/pict choice from user
    """
    choose_type = False
    video = False

    while (not choose_type):
        choice = raw_input("Video (V) or Pictures (P)")

        if ((choice == 'V') or (choice == 'v')):
            video = True
            choose_type= True

        elif ((choice == 'P') or (choice == 'p')):
            video = False
            choose_type= True

    return video

def run(n_max_frame):
    """
    The main part, parsing pict files or movie frames
    and combining them to enhance the pictures
    """
    # Parameters
    gamma = 0.8 # The gamma curve parameter.. lower value lightens the picture


    # Get the inputs
    use_video = getUserChoice()

    path = raw_input("File/folder path ? (keep empty for defaults)")

    pict_list = []
    n_picts = 0

    if(use_video):
        # To change with a really dark video...
        if (path == ''):
            path = "point_tracking_1px.avi"

        handle = getVideoFile(path)

    else:
        if (path ==''):
            path = 'Photos/20 Photos/'
        [pict_list, n_picts] = getPictFiles(path)


    # Process the stream frame by frame
    keep_going = True
    current_pict = 0

    for i in range(min(n_max_frame, len(pict_list))):
        if (keep_going == True) :

            # Read one frame from either video or filelist
            if(use_video):
                keep_going, frame = handle.read()
                current_pict = current_pict + 1

            else :
                keep_going = (current_pict<n_picts)
                frame = pict_list[current_pict]
                current_pict = current_pict + 1

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