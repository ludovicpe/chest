# -*- coding: utf-8 -*-
"""
Created on Thursday 27 Februray, 2014

@author: BLefaudeux
"""
import sys
sys.path.insert(0, '../framework')

import cv2          # OpenCV
import frameGrabber # Wrap the frame grabbing process
import frameFusion  # Wrap the frame accumulation process
import time

def run(n_max_frame):
    """
    The main part, get frames from the pi camera
    and combine them to enhance the pictures
    @rtype : nothing
    @param n_max_frame:
    """
    # Parameters
    gamma = 0.8  # The gamma curve parameter.. lower value lightens the picture

    # Get the inputs
    frame_source = frameGrabber.Webcam()
    print "Opening webcam"

    # Process the stream frame by frame
    keep_going = True
    i = 0

    base_filename = 'pict_fuse'

    while keep_going and i < n_max_frame:
        print "Grab frame {}".format(i)
        keep_going, frame = frame_source.new_frame()

        if not keep_going:
            print "Could not read frame"
            break

        else:
            print "... is OK"

            cv2.namedWindow("Show")
            cv2.imshow("Show", frame)
            k = cv2.waitKey(33)

            b_quit = False

            # Escape quits
            if k == 27:
                b_quit = True
                cv2.destroyAllWindows()
                cv2.imshow()

            keep_going = keep_going and not(b_quit)

    print "Bybye.."
    cv2.destroyWindow('Raw frame')
    frame_source.release()

    return

# Bam ! Run this stuff
run(50)
