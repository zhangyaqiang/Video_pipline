import os
import numpy as np
import glob
import cv2
import skvideo.io
from skimage import io,color,transform,img_as_ubyte
import dlib
import time
import matplotlib.pyplot as plt
from collections import Counter

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('/home/zyq/PycharmProjects/'
            'Video_pipline/bin/shape_predictor_68_face_landmarks.dat')

def get_video_frames(video_path):
    videogen = skvideo.io.vreader(video_path)
    frames = np.array([frame for frame in videogen])
    return frames

def get_frames_mouth(video_path):
    frames = get_video_frames(video_path)
    mouth_frames = []
    for frame in frames:
        dets = detector(frame, 1)
        shape = None
        for k, d in enumerate(dets):
            shape = predictor(frame, d)
            i = -1
        if shape is None or len(dets) > 1:  # Detector doesn't detect face, just return as is
            # return
            # mouth_crop_image = frame[mouth_centroid[1] - width:mouth_centroid[1] + width,
            #                mouth_centroid[0] - width:mouth_centroid[0] + width]
            # mouth_crop_image = frame[mouth_centroid[1] - 45:mouth_centroid[1] + 45,
            #                    mouth_centroid[0] - 70:mouth_centroid[0] + 70]
            # mouth_frames.append(mouth_crop_image)
            continue
        mouth_points = []
        for part in shape.parts():
            i += 1
            if i == 4:
                left = part.x
            if i == 12:
                right = part.x
            if i < 48:
                continue
            mouth_points.append((part.x, part.y))
        width = (right - left) // 2
        np_mouth_points = np.array(mouth_points)
        mouth_centroid = np.mean(np_mouth_points[:, -2:], axis=0).astype(int)
#         mouth_crop_image = frame[mouth_centroid[1] - width:mouth_centroid[1] + width, mouth_centroid[0] - width:mouth_centroid[0] + width]
        mouth_crop_image = frame[mouth_centroid[1] - 45:mouth_centroid[1] + 45,
                                 mouth_centroid[0] - 70:mouth_centroid[0] + 70]
        mouth_frames.append(mouth_crop_image)
    return mouth_frames


if __name__ == '__main__':
    video_dir = '/home/zyq/video_pipline_data/dataset/ST-1/video/train_set'
    video_list = glob.glob(os.path.join(video_dir, '0003*.avi'))
    sorted(video_list)
    frames_dir = '/home/zyq/video_pipline_data/dataset/ST-1/video_frames/train_set'
    for video in video_list:
        print(video + ' started')
        _dir = os.path.join(frames_dir, os.path.basename(video).split('.')[0])
        if not os.path.exists(_dir):
            mouth_frames = get_frames_mouth((video))
            os.mkdir(_dir)
            num = 0
            for frame in mouth_frames:
                image_path = os.path.join(_dir, "frame_" + str(num).zfill(4) + ".png")
                io.imsave(image_path, frame)
                num += 1
            print(video + ' finisehd')