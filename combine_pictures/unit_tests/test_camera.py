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
	start_time = time.time()
        keep_going, frame = frame_source.new_frame()
	print "... is OK"

        if not keep_going:
            print "Could not read frame"
            break

        else:
            # Bring the picture down to 1 channel if in color
            if 3 == len(frame.shape) and 3 == frame.shape[2]:
                frame_bw = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            else:
                frame_bw = frame

            # Initialize the accumulated frame
            if i == 0:
                frame_accumulator = frameFusion.FrameFusion(frame_bw, gamma, False)

            # Process frames :
            else:
                frame_accumulator.pile_up(frame_bw)

	    # Show what's going on :
	    frame_accumulator.show

            # Store the results :
	    stop_time = time.time()
	    print "Store frame - {0:.2f}s to process".format(stop_time-start_time)

            filename = base_filename + str(i) + '.jpg'
            cv2.imwrite(filename, frame_accumulator.get_fused_frame())

            filename = base_filename + str(i) + 'raw' + '.jpg'
	    cv2.imwrite(filename, frame_bw)
            i += 1

    print "Bybye.."
    cv2.destroyWindow('Raw frame')
    return

    frame_source.release()

# Bam ! Run this stuff
run(50)
