#coding:utf-8
import dlib
import cv2
from imutils import face_utils
import subprocess
import skvideo.io
import numpy as np
from skimage import io,color,transform,img_as_ubyte
import os
import glob
import matlab.engine
from video_pipline.Asr import Asr
from video_pipline.label_class import Label

class Shot(object):
    def __init__(self, shot_path=None):
        if shot_path == None:
            raise AttributeError('No shot path!')
        self.shot_dir = shot_path
        self.shot_path = glob.glob(os.path.join(shot_path, '*mp4'))[0]
        self.shot_name = os.path.splitext(os.path.basename(self.shot_path))[0]
        self.frames_dir = os.path.join(os.path.dirname(os.path.abspath(self.shot_path)), self.shot_name)
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('/home/zyq/PycharmProjects/'
                                              'Video_pipline/bin/shape_predictor_68_face_landmarks.dat')
        self.wav_path = glob.glob(os.path.join(self.shot_dir, "*.wav"))[0]
        self.frames = None
        self.label_path = os.path.join(self.shot_dir, 'label.txt')
        self.mouth_frames = None
        self.audio = None

    def overlap_proportion(self, c1, r1, w1, h1, c2, r2, w2, h2):
        if c1 > c2 + w2: return 0.0
        if r1 > r2 + h2: return 0.0
        if c1 + w1 < c2: return 0.0
        if r1 + h1 < r2: return 0.0
        col = min(c1 + w1, c2 + w2) - max(c1, c2)
        row = min(r1 + h1, r2 + h2) - max(r1, r2)
        intersection = col * row
        area1 = c1 * r1
        area2 = c2 * r2
        return float(intersection) / (area1 + area2 - intersection)

    def face_detected(self):
        detector = dlib.get_frontal_face_detector()

        tracker = cv2.MultiTracker_create()

        cap = cv2.VideoCapture(self.shot_path)
        track_windows = []
        init_once = False
        cur_frame = 0
        face_in_frames = 0

        while cap.isOpened():

            ok, image = cap.read()
            if not ok:
                break

            frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            dets = detector(frame, 1)

            # 初始化跟踪框
            if init_once == False:
                # 只考虑一张人脸的视频
                if len(dets) == 1:
                    for i, d in enumerate(dets):
                        x, y, w, h = face_utils.rect_to_bb(d)
                        face_pos = []
                        face_pos.append((x, y, w, h))
                        track_windows.append((x, y, w, h))
                        #print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                            #i, d.left(), d.top(), d.right(), d.bottom()))

                    for bbox in track_windows:
                        ok = tracker.add(cv2.TrackerKCF_create(), image, bbox)

                    if not ok:
                        print ("tracker initial error")
                        break
                    init_once = True
                    start_frame = cur_frame
                else:
                    return False
            else:
                # 跟踪
                ok, boxes = tracker.update(image)
                for newbox in boxes:
                    p1 = (int(newbox[0]), int(newbox[1]))
                    p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
                if len(dets) != 1:
                    return False
                else:
                    for i, d in enumerate(dets):
                        x, y, w, h = d.left(), d.top(), d.right() - d.left(), d.bottom() - d.top()
                        box_num = 0
                        box = boxes[0]
                        max_overlap = self.overlap_proportion(x, y, w, h, box[0], box[1], box[2], box[3])
                        if max_overlap < 0.1:
                            return False
            cur_frame += 1


        return True

    def delete(self):
        ps = subprocess.Popen(("rm",
                               "-rf",
                               self.shot_dir),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        output = ps.stdout.read()
        # print (output)

    def to_frames_wav(self):
        if not os.path.exists(self.frames_dir):
            os.mkdir(self.frames_dir)
        num = 0
        for frame in self.mouth_frames:
            frame = color.rgb2gray(frame)
            frame = transform.resize(frame, (120, 120))
            frame = img_as_ubyte(frame)
            image_path = os.path.join(self.frames_dir, "frame_" + str(num).zfill(4) + ".png")
            io.imsave(image_path, frame)
            num += 1




    def get_video_frames(self):
        # 原来使用skvideo读取视频文件
        videogen = skvideo.io.vreader(self.shot_path)
        self.frames = np.array([frame for frame in videogen])


    def get_frames_mouth(self):
        mouth_frames = []
        for frame in self.frames:
            dets = self.detector(frame, 1)
            shape = None
            for k, d in enumerate(dets):
                shape = self.predictor(frame, d)
                i = -1
            if shape is None:  # Detector doesn't detect face, just return as is
                return
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
            mouth_crop_image = frame[mouth_centroid[1] - width:mouth_centroid[1] + width, mouth_centroid[0] - width:mouth_centroid[0] + width]
            mouth_frames.append(mouth_crop_image)
        self.mouth_frames =  mouth_frames

    #def to_matdata(self):
     #  frame_nums = len(frame_list)
     #   mat_y = np.empty([120, 120, frame_nums], dtype=np.uint8)
     #   for i in range(frame_nums):
     #       mat_y[:, :, i] = io.imread(frame_list[i])
     #   wav_file = glob.glob(os.path.join(self.shot_dir, "*.wav"))
     #   f, mat_z = wavfile.read(wav_file[0])
     #   mat_z = mat_z / (2. ** 15)
     #   self.mat_data = os.path.join(self.shot_dir, os.path.splitext(os.path.basename(wav_file[0]))[0] + ".mat")
     #   scio.savemat(self.mat_data, {'Y': mat_y, 'Z': mat_z})

    def av_sync(self):
        eng = matlab.engine.start_matlab()
        offset, conf = eng.findoffset(self.frames_dir+"/", self.wav_path, nargout=2)
        av_sync = False
        if (offset >= -1 and offset < 5 and conf > 5):
            av_sync =  True
        eng.close()
        return av_sync

    def asr(self):
        a = Asr(self.wav_path)
        if not a.get_text():
            self.delete()
            return False
        a.get_lab()
        a.get_pinyin()
        a.get_phoneme()
        if not a.alignment():
            self.delete()
            return False
        return True

    def get_labels(self):
        label = Label(self.label_path)
        label.split_label()
        print("label has been splited")
        label.split_video()
        print("video has been splited")
