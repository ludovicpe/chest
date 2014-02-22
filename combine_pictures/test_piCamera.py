# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 15:55:33 2013

@author: BLefaudeux
"""

import cv2          # OpenCV
import frameGrabber # Wrap the frame grabbing process
import frameFusion  # Wrap the frame accumulation process


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
    frame_source = frameGrabber.PiCamera()

    # Process the stream frame by frame
    keep_going = True
    i = 0

    base_filename = 'pict_fuse'

    while keep_going and i < n_max_frame:
        keep_going, frame = frame_source.new_frame()

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
                frame_accumulator = frameFusion.FrameFusion(frame_bw, gamma, True)

            # Process frames :
            else:
                frame_accumulator.pile_up(frame_bw)

            # Show results
            # keep_going = frame_accumulator.show()

            # Store the results :
            filename = base_filename + str(i) + '.jpg'
            cv2.imwrite(filename, frame_accumulator.get_fused_frame(),  [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            i += 1

    print "Bybye.."
    cv2.destroyWindow('Raw frame')
    return

    frame_source.release()

# Bam ! Run this stuff
run(500)
