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
    n_fused_frames  = 0
    pict_size_x     = 0
    pict_size_y     = 0
    gamma           = 1.0  # The gamma curve parameter.. lower value lightens the picture

    n_max_corners   = 1000
    corners_q_level = 4
    tracked_corners = False

    frame_acc       = np.float32(pict_size_x * pict_size_y)
    frame_acc_disp  = np.float32(pict_size_x * pict_size_y)
    frame_eq        = np.float32(pict_size_x * pict_size_y)
    frame_prev      = np.float32(pict_size_x * pict_size_y)
    corners         = np.float32(0)
    corners_next    = np.float32(0)

    # The constructor, on top of an initial frame
    def __init__(self, frame_first, gamma = 1.0, motion_compensation = False):
        # Define settings
        self.n_fused_frames = 0
        self.gamma          = gamma
        self.n_max_corners  = 400
        self.corners_q_level= 4
        self.motion_comp    = motion_compensation

        # Allocate buffers
        self.frame_acc      = np.float32(frame_first)
        self.frame_acc_disp = np.float32(frame_first)
        self.frame_eq       = np.float32(frame_first)
        self.frame_prev     = frame_first

        # Do the first accumulation
        cv2.equalizeHist(frame_first, self.frame_acc)
        cv2.normalize(self.frame_acc, self.frame_acc_disp, 0., 1., cv2.NORM_MINMAX)  # just for the display stuf

    # Display lines representing tracks
    @staticmethod
    def draw_vec(img, corners, corners_next):
        try:
            corn_xy = corners.reshape((-1, 2))
            corn_xy_next = corners_next.reshape((-1, 2))

            i = 0
            for x, y in corn_xy:
                cv2.line(img, (int(x), int(y)), (int(corn_xy_next[i,0]), int(corn_xy_next[i,1])), [0,0,255],10)
                i += 1

        except ValueError:
            print "Problem printing the motion vectors"

    def pile_up(self, new_frame):
        """
        Add a new frame to the current accumulation

        @param new_frame:
        @return: number of frames in the current pile
        """
        # Kill black level before the accumulation
        cv2.equalizeHist(new_frame, self.frame_eq)

        # Do the accumulation with motion compensation
        # -- we offset the previous accumulation
        if self.motion_comp and self.n_fused_frames > 0:
            b_success = self.compensate_interframe_motion(new_frame)

            if b_success:
                print "Frames aligned"
            else:
                print "Frames not aligned"

        cv2.accumulate(new_frame, self.frame_acc)  # Just add pixel values
        cv2.normalize(np.power(self.frame_acc, self.gamma), self.frame_acc_disp, 0., 1., cv2.NORM_MINMAX)

        # Update and return
        self.n_fused_frames += 1
        self.frame_prev = new_frame

        return self.n_fused_frames

    def compensate_interframe_motion(self, new_frame):
        # Test different techniques to compensate motion :
        # - shi & tomasi + KLT
        success = self.compensate_shi_tomasi(new_frame)

        # - ORB + distance matching
        # success = self.compensate_orb(new_frame)

        # - SIFT + distance matching
        #    acc_frame_aligned = self.compensate_SIFT(new_frame)

        return success

    def compensate_sift(self, new_frame):
        # Test with SIFT corners :
        _min_match_count = 10
        _flann_index_kdtree = 0

        # Initiate SIFT detector
        sift = cv2.SIFT()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(self.frame_prev,None)
        kp2, des2 = sift.detectAndCompute(new_frame,None)

        index_params = dict(algorithm = _flann_index_kdtree, trees = 5)
        search_params = dict(checks = 50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1,des2,k=2)

        # store all the good matches as per Lowe's ratio test.
        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)

        # - bring the second picture in the current referential
        if len(good)>_min_match_count:
            print "Enough matches for compensation - %d/%d" % (len(good),_min_match_count)
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()

            h,w = self.frame_prev.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            transform = cv2.perspectiveTransform(pts,M)
            #        new_frame = cv2.polylines(new_frame,[np.int32(transform)],True,255,3, cv2.LINE_AA)

        else:
            print "Not enough matches are found - %d/%d" % (len(good),_min_match_count)
            matchesMask = None

    def compensate_orb(self, new_frame):
        detector = cv2.FastFeatureDetector(16, True)
        detector = cv2.GridAdaptedFeatureDetector(detector)
        extractor = cv2.DescriptorExtractor_create('ORB')

        # Test with SIFT corners :
        _min_match_count = 10

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
        if len(good_matches)>_min_match_count:
            print "Enough matchs for compensation - %d/%d" % (len(good_matches),_min_match_count)
            self.corners = np.float32([k1[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
            self.corners_next = np.float32([k2[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)

            transform, mask = cv2.findHomography(self.corners_next, self.corners , cv2.RANSAC,5.0)

            # Check that the transform indeed explains the corners shifts ?
            # TODO: Quality check

            # Align the previous accumulated frame
            acc_frame_aligned = cv2.warpPerspective(self.frame_acc, transform, self.frame_acc.shape[2::-1])

            self.frame_acc = acc_frame_aligned

            # DEBUG
            cv2.imshow('Aligned Frame', acc_frame_aligned)
            cv2.waitKey()
            cv2.destroyWindow('Aligned Frame')
            # DEBUG

            return True

        else:
            print "Not enough matches are found - %d/%d" % (len(good_matches), _min_match_count)
            return False

    def compensate_shi_tomasi(self, new_frame):
        """
        Measure and compensate for inter-frame motion:
        - get points on both frames
        -- we use Shi & Tomasi here, to be adapted ?
        @rtype : opencv frame
        """
        self.corners = cv2.goodFeaturesToTrack(self.frame_prev, 50, .01, 50)

        # - track points
        [self.corners_next, status, err] = cv2.calcOpticalFlowPyrLK(self.frame_prev, new_frame, self.corners)

        # - compute the transformation from the tracked pattern
        # -- estimate the rigid transform
        transform, mask = cv2.findHomography(self.corners_next, self.corners, cv2.RANSAC, 5.0)

        # -- see if this transform explains most of the displacements (thresholded..)
        if len(mask[mask>0]) > len(mask/2.0):
            print "Enough match for motion compensation"
            acc_frame_aligned = cv2.warpPerspective(self.frame_acc, transform, self.frame_acc.shape[2::-1])
            self.frame_acc = acc_frame_aligned
            return True

        else:
            print "Not finding enough matchs - {}".format(len(mask[mask>0]))
            return False

    @property
    def show(self):
        keep_going = False

        # Show the current combined picture
        print "Showing frame {}".format(self.n_fused_frames)

        # Do all the resizing beforehand
        frame_fusion_resize = cv2.resize(self.frame_acc_disp, (800,600))

        # Onscreen print
        cv2.putText(frame_fusion_resize, "Space continues, Esc leaves",
                    (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255)

        cv2.namedWindow("FrameFusion")
        cv2.imshow("FrameFusion", frame_fusion_resize)
        cv2.waitKey(5)

        # Show the initial picture
        cv2.namedWindow('Raw frame')
        # - Show tracked features
        if self.motion_comp:
            self.draw_vec(self.frame_prev, self.corners, self.corners_next)

        frame_raw_resize = cv2.resize(self.frame_prev, (800,600))
        cv2.imshow('Raw frame', frame_raw_resize)
        cv2.waitKey(5)

        start_time = time.time()

        while 1:
            # Q quits
            k = cv2.waitKey(33)

            current_time = time.time()

            if 27 == k or  1048603 == k:
                keep_going = False
                cv2.destroyWindow('FrameFusion')
                cv2.destroyWindow('Raw frame')
                break

            # Space continues
            elif 32 == k or 1048608 == k:
                keep_going = True
                break

            # Timer went through, time to leave
            elif (current_time - start_time) > 10:
                keep_going = True
                print "Waited enough, next frame !"
                break

            elif k != -1:
                print k

        return keep_going

