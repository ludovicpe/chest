# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 15:17:59 2013

@author: benjamin lefaudeux

Class to combine different pictures on top of one another.
"""

import cv2
import numpy as np
import time


class FrameFusion:
    n_fused_frames = 0
    pict_size_x = 0
    pict_size_y = 0
    gamma = 1.0  # The gamma curve parameter.. lower value lightens the picture

    n_max_corners = 1000
    corners_q_level = 4
    tracked_corners = False

    frame_acc = np.float32(pict_size_x * pict_size_y)
    frame_acc_disp = np.float32(pict_size_x * pict_size_y)
    frame_eq = np.float32(pict_size_x * pict_size_y)
    frame_prev = np.float32(pict_size_x * pict_size_y)
    corners = np.float32(0)
    corners_next = np.float32(0)

    # The constructor, on top of an initial frame
    def __init__(self, frame_first, gamma=1.0, motion_compensation=False):
        # Define settings
        """
        The constructor for a new frameFusion instance

        @param frame_first: initial picture
        @param gamma: contrast parameter
        @param motion_compensation: (boolean flag) compensate motion over time
        """
        self.n_fused_frames = 0
        self.gamma = gamma
        self.n_max_corners = 400
        self.corners_q_level = 4
        self.motion_comp = motion_compensation
        self.motion_compensation_method = 'shi_tomasi'
        self.reset = False

        # Allocate buffers
        self.frame_acc = np.float32(frame_first)
        self.frame_acc_disp = np.float32(frame_first)
        self.frame_eq = np.float32(frame_first)
        self.frame_prev = frame_first

        # Do the first accumulation
        cv2.equalizeHist(frame_first, self.frame_acc)
        cv2.normalize(self.frame_acc, self.frame_acc_disp, 0., 1., cv2.NORM_MINMAX)  # just for the display stuf

    def compensate_interframe_motion(self, new_frame, technique='shi_tomasi'):
        """
        Compensate the motion between two observations

        @param new_frame: the new observation
        @param technique: the technique to be used (we're trying several of them..)
        @return:
        - the self.frame_acc is offset to its new referential
        - return boolean describing the success of the operation
        """
        if technique == 'shi_tomasi':
            # - shi & tomasi + KLT
            success = self.__compensate_shi_tomasi(new_frame)
            self.motion_compensation_method = technique

        elif technique == 'orb':
            # - ORB + distance matching
            success = self.__compensate_orb(new_frame)
            self.motion_compensation_method = technique

        elif technique == 'sift':
            # - SIFT + distance matching
            #    acc_frame_aligned = self.__compensate_SIFT(new_frame)
            print "Cannot use SIFT right now..."
            pass

        else:
            ValueError('Wrong argument for motion compensation')

        return success

    def get_fused_frame(self, integer_frame=True):
	# Return the frame in float
	if not integer_frame:
	    return self.frame_acc_disp

	# Convert to uint8 and return (default)
	else :
	    self.frame_acc_disp *= 255
	    frame_disp_int = self.frame_acc_disp.astype(int)
	    return frame_disp_int
    	    	

    def pile_up(self, new_frame):
        """
        Add a new frame to the current accumulation

        @rtype: integer, number of frames
        @param new_frame:
        @return: number of frames in the current pile
        """

        # Kill black level before the accumulation
        cv2.equalizeHist(new_frame, self.frame_eq)

        # Do the accumulation with motion compensation
        # -- we offset the previous accumulation
        if self.motion_comp and self.n_fused_frames > 0:
            b_success = self.compensate_interframe_motion(new_frame, 'shi_tomasi')

            if b_success:
                print "Frames aligned"
            else:
                print "Frames not aligned"

        # Handle a reset of the accumulation (TODO : Make it automatic if the scene changes a lot)
        if self.reset:
            self.frame_acc = np.float32(new_frame)
            self.reset = False

        # Pile up
        cv2.accumulate(new_frame, self.frame_acc)  # Just add pixel values
        cv2.normalize(np.power(self.frame_acc, self.gamma), self.frame_acc_disp, 0., 1., cv2.NORM_MINMAX)

        # Update and return
        self.n_fused_frames += 1
        self.frame_prev = new_frame

        return self.n_fused_frames

    def __compensate_orb(self, new_frame):
        """
        Compensate the motion between existing accumulation and the new frame

        @rtype : boolean
        @param new_frame: (numpy array) OpenCV frame
        @return: compensation success
        """

        # Create an ORB detector
        detector = cv2.FastFeatureDetector(16, True)
        # detector = cv2.GridAdaptedFeatureDetector(detector)
        extractor = cv2.DescriptorExtractor_create('ORB')

        # Test with ORB corners :
        _min_match_count = 20

        # find the keypoints and descriptors with ORB
        kp1 = detector.detect(new_frame)
        k1, des1 = extractor.compute(new_frame, kp1)

        kp2 = detector.detect(self.frame_prev)
        k2, des2 = extractor.compute(self.frame_prev, kp2)

        # Match using bruteforce
        matcher = cv2.DescriptorMatcher_create('BruteForce-Hamming')
        matches = matcher.match(des1, des2)

        # store all the good matches as per Lowe's ratio test.
        dist = [m.distance for m in matches]

        # threshold: half the mean
        thres_dist = (sum(dist) / len(dist)) * 0.5

        # keep only the reasonable matches
        good_matches = [m for m in matches if m.distance < thres_dist]

        # - bring the second picture in the current referential
        if len(good_matches) > _min_match_count:
            print "Enough matchs for compensation - %d/%d" % (len(good_matches), _min_match_count)
            self.corners = np.float32([k1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            self.corners_next = np.float32([k2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            transform, mask = cv2.findHomography(self.corners_next, self.corners, cv2.RANSAC, 5.0)

            # Check that the transform indeed explains the corners shifts ?
            # TODO: Quality check

            # Align the previous accumulated frame
            acc_frame_aligned = cv2.warpPerspective(self.frame_acc, transform, self.frame_acc.shape[2::-1])
            self.frame_acc = acc_frame_aligned
            return True

        else:
            print "Not enough matches are found - %d/%d" % (len(good_matches), _min_match_count)
            return False

    def __compensate_shi_tomasi(self, new_frame):
        """
        Measure and compensate for inter-frame motion:
        - get points on both frames
        -- we use Shi & Tomasi here, to be adapted ?
        @rtype : opencv frame
        """
        self.corners = cv2.goodFeaturesToTrack(self.frame_prev, self.n_max_corners, .01, 50)

        # - track points
        [self.corners_next, status, err] = cv2.calcOpticalFlowPyrLK(self.frame_prev, new_frame, self.corners)

        # - track back (more reliable)
        [corners_next_back, status_back, err_back] = cv2.calcOpticalFlowPyrLK(new_frame,
                                                                              self.frame_prev, self.corners_next)

        # - sort out to keep reliable points :
        [self.corners, self.corners_next] = self.__sort_corners(self.corners,
                                                                self.corners_next, status,
                                                                corners_next_back, status_back)

        # - compute the transformation from the tracked pattern
        # -- estimate the rigid transform
        transform, mask = cv2.findHomography(self.corners_next, self.corners, cv2.RANSAC, 5.0)

        # -- see if this transform explains most of the displacements (thresholded..)
        if len(mask[mask > 0]) > 20: # TODO: More robust test here
            print "Enough match for motion compensation"
            acc_frame_aligned = cv2.warpPerspective(self.frame_acc, transform, self.frame_acc.shape[2::-1])
            self.frame_acc = acc_frame_aligned
            return True

        else:
            print "Not finding enough matchs - {}".format(len(mask[mask > 0]))
            return False

    def __compensate_sift(self, new_frame):
        # Test with SIFT corners :
        _min_match_count = 10
        _flann_index_kdtree = 0

        # Initiate SIFT detector
        sift = cv2.SIFT()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(self.frame_prev, None)
        kp2, des2 = sift.detectAndCompute(new_frame, None)

        index_params = dict(algorithm=_flann_index_kdtree, trees=5)
        search_params = dict(checks=50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k=2)

        # store all the good matches as per Lowe's ratio test.
        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)

        # - bring the second picture in the current referential
        if len(good) > _min_match_count:
            print "Enough matches for compensation - %d/%d" % (len(good), _min_match_count)
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            matchesMask = mask.ravel().tolist()

            h, w = self.frame_prev.shape
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            transform = cv2.perspectiveTransform(pts, M)
            #        new_frame = cv2.polylines(new_frame,[np.int32(transform)],True,255,3, cv2.LINE_AA)

        else:
            print "Not enough matches are found - %d/%d" % (len(good), _min_match_count)
            matchesMask = None


    @staticmethod
    def __draw_vec(img, corners, corners_next):
        """
        Draw motion vectors on the picture

        @param img: picture to draw onto
        @param corners: initial keypoints position
        @param corners_next: position after tracking
        """
        try:
            corn_xy = corners.reshape((-1, 2))
            corn_xy_next = corners_next.reshape((-1, 2))

            i = 0
            for x, y in corn_xy:
                cv2.line(img, (int(x), int(y)), (int(corn_xy_next[i, 0]), int(corn_xy_next[i, 1])), [0, 0, 255], 5)
                i += 1

        except ValueError:
            print "Problem printing the motion vectors"

    @staticmethod
    def __sort_corners(corners_init, corners_tracked, status_tracked,
                       corners_tracked_back, status_tracked_back, max_dist=0.5):

        # Check that the status value is 1, and that
        i = 0
        nice_points = []
        for c1 in corners_init:
            c2 = corners_tracked_back[i]
            dist = cv2.norm(c1, c2)

            if status_tracked[i] and status_tracked_back[i] and dist < max_dist:
                nice_points.append(i)

            i += 1

        return [corners_init[nice_points], corners_tracked[nice_points]]

    @property
    def show(self):
        keep_going = False

        # Show the current combined picture
        print "Showing frame {}".format(self.n_fused_frames)

        # Do all the resizing beforehand
        frame_fusion_resize = cv2.resize(self.frame_acc_disp, (800, 600))

        # Onscreen print
        cv2.putText(frame_fusion_resize, "Space continues, Esc leaves \n R resets, M changes method",
                    (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255)

        cv2.namedWindow("FrameFusion")
        cv2.imshow("FrameFusion", frame_fusion_resize)
        cv2.waitKey(5)

        # Show the initial picture
        cv2.namedWindow('Raw frame')
        # - Show tracked features
        if self.motion_comp:
            self.__draw_vec(self.frame_prev, self.corners, self.corners_next)

        frame_raw_resize = cv2.resize(self.frame_prev, (800, 600))
        cv2.imshow('Raw frame', frame_raw_resize)
        cv2.waitKey(5)

        start_time = time.time()

        while 1:
            k = cv2.waitKey(33)

            current_time = time.time()

            # Escape quits
            if 27 == k or 1048603 == k:
                keep_going = False
                cv2.destroyWindow('FrameFusion')
                cv2.destroyWindow('Raw frame')
                break

            # Space continues
            elif 32 == k or 1048608 == k:
                keep_going = True
                break

            # R resets the accumulation
            elif ord('r') == k or 1048690 == k:
                keep_going = True
                self.reset = True
                print "Reset the accumulation"
                break

            # M changes the compensation method
            elif ord('m') == k:
                keep_going = True

                if self.motion_compensation_method == 'shi_tomasi':
                    self.motion_compensation_method = 'orb'
                    self.reset = True

                else:
                    self.motion_compensation_method = 'shi_tomasi'
                    self.reset = True

                print "Change the motion compensation method"
                break

            # Timer went through, time to leave
            elif (current_time - start_time) > 1:
                keep_going = True
                print "Waited enough, next frame !"
                break

            elif k != -1:
                print k

        return keep_going


