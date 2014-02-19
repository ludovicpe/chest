# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 12:07:45 2013

@author: benjamin lefaudeux

Root and inherited classes to wrap different possible picture inputs,
such as a series of files, a movie file, or a connected camera
"""
import cv2
import os
import utils as ut
from time import sleep

import picamera
import numpy as np
import io, time
from __future__ import division

class FrameGrabber:
    """
    The overall FrameGrabber class, from which all our sub-classes inherit
    """
    n_frame = 0
    n_max_frames = 0
    size_x = 0
    size_y = 0

    def __init__(self):
        # The default constructor
        self.n_frames = 0
        self.n_max_frames = 0
        self.size_x = 0
        self.size_y = 0

        return 'New empty frame grabber'

    @staticmethod
    def __show_pict_window(pict):
        b_quit = False

        cv2.namedWindow("Show")
        cv2.imshow("Show", pict)
        k = cv2.waitKey(33)

        # Escape quits
        if k == 27:
            b_quit = True
            cv2.destroyAllWindows()

        return b_quit

    # 'Pure virtual' methods
    def release(self):
        raise 'Abstract method, please override'

    def new_frame(self):
        raise 'Abstract method, please override'


class PictsFile(FrameGrabber):
    """
    Inherited class : read a sequence of pictures
    """

    # The constructor : get a list of all the frames, and the number of frames
    def __init__(self, folder):
        [self.pict_list, self.n_max_frames] = self.__get_pict_files(folder)
        self.n_frames = 0
        self.size_x = 0
        self.size_y = 0

    @staticmethod
    def __get_pict_files(folder):
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
                        if picture_list[n_files] is None:
                            picture_list.pop()
                            print "Error loading file {}".format(filename)
                        else:
                            n_files += 1

                    except:
                        print "Error loading file {}".format(filename)

        return picture_list, n_files

    def new_frame(self):
        if self.n_frames < (self.n_max_frames-1):
            self.n_frames += 1
            return [True, self.pict_list[self.n_frames]]

        else:
            return [False, []]

    def show(self):
        FrameGrabber.__show_pict_window(self.frame)


class VideoFile(FrameGrabber):
    """
    Inherited class : read a video file
    """

    # The constructor : get a handle on a video file
    def __init__(self, filename):
        self.n_frames = 0
        self.capture = cv2.VideoCapture(filename)
        self.keep_going = True
        self.frame = []

    # Get a new frame
    def new_frame(self):
        if self.keep_going:
            self.keep_going, self.frame = self.capture.read()
            self.n_frame += 1
            return [True, self.frame]

        else:
            return [False, []]

    def show(self):
        FrameGrabber.__show_pict_window(self.frame)


class Webcam(FrameGrabber):
    """
    Inherited class : read a video stream from a connected camera
    """

    def __init__(self, device_id=0):
        self.n_frames = 0
        self.cam = cv2.VideoCapture(device_id)

        if self.cam.isOpened():
            self.cam.release()

        self.cam.open(device_id)  # Useful ?
        self.keep_going = True

        # # Change the gain and exposure (if supported ?)
        # # 14 - CV_CAP_PROP_GAIN Gain of the image (only for cameras).
        # # 15 - CV_CAP_PROP_EXPOSURE Exposure (only for cameras).
        # self.cam.set(14, 2)
        # self.cam.set(15, 2)

        # Init frames, empty for now..
        self.frame_last = []
        self.frame = []

    def new_frame(self):
        self.keep_going, self.frame_last = self.cam.read()

        if self.keep_going :
            return [True, self.frame_last]

        else:
            self.cam.release()
            return [False, []]

    def show(self):
        keep_going = True

        while keep_going:
            grab_success, self.frame = self.new_frame()

            if not grab_success:
                return

            else :
                b_quit = FrameGrabber.__show_pict_window(self, self.frame)
                keep_going = keep_going and not b_quit

    # Re-implement this method
    # in this case we really want to release the connected cam
    def release(self):
        self.cam.release()


class PiCamera(FrameGrabber):
    def __init__(self):
        self.cam = picamera.PiCamera()
        self.width = 2592
        self.height = 1944
        self.cam.resolution = (self.width, self.height)
        self.n_frames = 0
        self.keep_going = True
        self.ongoing_record = False

    def capture(self, filename='pict.jpg'):
        self.cam.capture(filename)

    def new_frame(self):
        stream = open('image.data', 'wb')  # FIFO to store the picture

        self.cam.start_preview()
        time.sleep(2)
        self.cam.capture(stream, format='rgb')

        stream.seek(0)  # Rewind the FIFO

        # Construct a numpy array from the stream
        fwidth = (self.width + 31) // 32 * 32
        fheight = (self.height + 15) // 16 * 16
        image = np.fromfile(stream, dtype=uint8).\
            reshape((fheight, fwidth, 3))[:height, :width, :]

        # Transform the format into floats ?
        # image = image.astype(np.float, copy=False)
        # image = image / 255.0

        return [True, image]

    def record_movie(self, filename='movie.h264'):
        if not self.ongoing_record:
            self.cam.start_recording(filename)
            self.ongoing_record = True

    def stop_recording(self):
        if self.ongoing_record:
            self.cam.stop_recording()
            self.ongoing_record = False

    def show(self):
        self.cam.start_preview()
        self.cam.vflip = True
        self.cam.hflip = True
        self.cam.brightness = 60