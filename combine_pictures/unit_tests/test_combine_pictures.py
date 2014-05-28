# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 21:54:19 2013

@author: Blefaudeux
"""

import sys
sys.path.insert(0, '../framework')

import cv2          # OpenCV
import frameGrabber # Wrap the frame grabbing process
import frameFusion  # Wrap the frame accumulation process


def get_user_choice():
    """
    Get the video/pict choice from user
    """
    choose_type = False

    while not choose_type:
        choice = raw_input("Video file (V), Pictures (P), Webcam (W) or PiCamera (C)")

        if (choice == 'V') or (choice == 'v'):
            path = raw_input("File/folder path ? (keep empty for defaults)")
            frame_source = frameGrabber.VideoFile(path)
            choose_type= True

        elif (choice == 'P') or (choice == 'p'):
            path = raw_input("File/folder path ? (keep empty for defaults)")
            frame_source = frameGrabber.PictsFile(path)
            choose_type= True

        elif (choice == 'W') or (choice == 'w'):
            frame_source = frameGrabber.Webcam()
            choose_type= True

        elif (choice == 'W') or (choice == 'w'):
            frame_source = frameGrabber.PiCamera()
            choose_type = True

    return frame_source


def run(n_max_frame):
    """
    The main part, parsing pict files or movie frames
    and combining them to enhance the pictures
    @rtype : nothing
    @param n_max_frame:
    """
    # Parameters
    gamma = 0.8  # The gamma curve parameter.. lower value lightens the picture

    # Get the inputs
    frame_source = get_user_choice()

    # Process the stream frame by frame
    keep_going = True
    i = 0

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
                frame_accumulator = frameFusion.FrameFusion(frame_bw, gamma, False)

            # Process frames :
            else:
                frame_accumulator.pile_up(frame_bw)

            # Show results
            keep_going = frame_accumulator.show
            i += 1

    print "Bybye.."
    cv2.destroyWindow('Raw frame')
    return

    frame_source.release()

# Bam ! Run this stuff
run(500)
