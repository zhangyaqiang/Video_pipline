#coding:utf-8
from __future__ import division
import subprocess
import os
import cv2

class Video(object):
    def __init__(self, video_path=None, shots_dir=None):
        if video_path == None or shots_dir == None:
            raise AttributeError('No source video or shots dir')
        self.video_path = video_path
        self.shots_dir = shots_dir
        self.wav_path = os.path.join(shots_dir, os.path.splitext(os.path.basename(self.video_path))[0]+".wav")
        self.boundaries = None

    def to_wav(self):
        ps = subprocess.Popen(("ffmpeg",
                               "-i",
                               self.video_path,
                               "-ac",
                               "1",
                               "-ar",
                               "16000",
                               self.wav_path),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        output = ps.stdout.read()

    def extract_shots_with_ffprobe(self, threshold=0.3):
        """
        uses ffprobe to produce a list of shot
        boundaries (in seconds)

        Args:
            src_video (string): the path to the source
                video
            threshold (float): the minimum value used
                by ffprobe to classify a shot boundary

        Returns:
            List[(float, float)]: a list of tuples of floats
            representing predicted shot boundaries (in seconds) and
            their associated scores
        """
        scene_ps = subprocess.Popen(("ffprobe",
                                     "-show_frames",
                                     "-of",
                                     "compact=p=0",
                                     "-f",
                                     "lavfi",
                                     "movie=" + self.video_path + ",select=gt(scene\," + str(threshold) + ")"),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        output = scene_ps.stdout.read()
        self.boundaries = self.extract_boundaries_from_ffprobe_output(output)
        self.boundaries.insert(0,0)

    def extract_boundaries_from_ffprobe_output(self, output):
        """
        extracts the shot boundaries from the string src_video
        producted by ffprobe

        Args:
            output (string): the full src_video of the ffprobe
                shot detector as a single string

        Returns:
            List[(float, float)]: a list of tuples of floats
            representing predicted shot boundaries (in seconds) and
            their associated scores
        """
        boundaries = []
        for line in output.split('\n')[13:-2]:
            boundary = float(line.split('|')[4].split('=')[-1])
            score = float(line.split('|')[-1].split('=')[-1])
            boundaries.append((boundary))
        return boundaries

    def split_video(self):
        bound_len = len(self.boundaries)
        #当前帧数
        frame_num = 1
        #第几个镜头
        bound_num = 0
        #长度大于3s的镜头
        shot_num = 0

        #切割视频
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        shot_dir = os.path.join(self.shots_dir, "shot_" + str(shot_num).zfill(4))
        if not os._exists(shot_dir):
            os.mkdir(shot_dir)
        shot_path = os.path.join(shot_dir, "shot_" + str(shot_num).zfill(4) + ".mp4")
        avi_path = os.path.join(shot_dir, "shot_" + str(shot_num).zfill(4) + ".avi")
        wav_path = os.path.join(shot_dir, "shot_" + str(shot_num).zfill(4) + ".wav")
        out = cv2.VideoWriter(avi_path, fourcc, 25, (720, 576))

        cap = cv2.VideoCapture(self.video_path)

        while(self.boundaries[bound_num+1] - self.boundaries[bound_num] < 3):
            bound_num += 1
        start_frame = int(self.boundaries[bound_num]/0.04)
        end_frame = int(self.boundaries[bound_num+1]/0.04)-1
        self.split_wav(self.boundaries[bound_num], self.boundaries[bound_num+1]-0.04, wav_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print ("no image")
                break;
            if frame_num < start_frame:
                frame_num += 1
                continue
            elif frame_num < end_frame:
                out.write(frame)
            elif frame_num == end_frame:
                out.release()
                self.merge_avi_wav(avi_path, wav_path, shot_path)
                #下一个镜头边界
                bound_num += 1
                while bound_num < bound_len-1 and self.boundaries[bound_num + 1] - self.boundaries[bound_num] < 3:
                    bound_num += 1
                if bound_num == bound_len-1: return

                shot_num += 1
                shot_dir = os.path.join(self.shots_dir, "shot_" + str(shot_num).zfill(4))
                if not os._exists(shot_dir):
                    os.mkdir(shot_dir)
                shot_path = os.path.join(shot_dir, "shot_" + str(shot_num).zfill(4) + ".mp4")
                avi_path = os.path.join(shot_dir, "shot_" + str(shot_num).zfill(4) + ".avi")
                wav_path = os.path.join(shot_dir, "shot_" + str(shot_num).zfill(4) + ".wav")
                out = cv2.VideoWriter(avi_path, fourcc, 25, (720, 576))

                start_frame = int(self.boundaries[bound_num] / 0.04)
                end_frame = int(self.boundaries[bound_num + 1] / 0.04)-1
                self.split_wav(self.boundaries[bound_num], self.boundaries[bound_num + 1] - 0.04, wav_path)



            frame_num += 1



    def split_wav(self, start_time, end_time, wav_path):
        ps = subprocess.Popen(("ffmpeg",
                               "-i",
                               self.wav_path,
                               "-ss",
                               str(start_time),
                               "-to",
                               str(end_time),
                               wav_path),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

    def merge_avi_wav(self, avi_path, wav_path, shot_path):
        ps = subprocess.Popen(("ffmpeg",
                               "-i",
                               wav_path,
                               "-i",
                               avi_path,
                               "-vcodec",
                               "copy",
                               shot_path),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)