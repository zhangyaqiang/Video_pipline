#coding:utf-8
from __future__ import division
import subprocess


class Video(object):
    def __init__(self, video_path=None, shots_dir=None):
        if video_path == None or shots_dir == None:
            raise AttributeError('No source video or shots dir')
        self.video_path = video_path
        self.shots_dir = shots_dir
        self.boundaries = None

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
        for line in output.split('\n')[15:-1]:
            boundary = float(line.split('|')[4].split('=')[-1])
            score = float(line.split('|')[-1].split('=')[-1])
            boundaries.append((boundary))
        return boundaries

    def split_video(self):
        j = 0
        for i in range(len(self.boundaries) - 1):
            if (self.boundaries[i + 1] - self.boundaries[i] < 3): continue
            if i == 0:
                ps = subprocess.Popen(("ffmpeg",
                                       "-i",
                                       self.video_path,
                                       "-ss",
                                       str(self.boundaries[i]),
                                       "-to",
                                       str(self.boundaries[i + 1] - 0.12),
                                       "-acodec",
                                       "copy",
                                       "-vcodec",
                                       "copy",
                                       self.shots_dir + "/shot" + "_" + str(j).zfill(4) + ".mp4"),
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
            else:
                ps = subprocess.Popen(("ffmpeg",
                                       "-i",
                                       self.video_path,
                                       "-ss",
                                       str(self.boundaries[i] - 0.08),
                                       "-to",
                                       str(self.boundaries[i + 1] - 0.12),
                                       "-acodec",
                                       "copy",
                                       "-vcodec",
                                       "copy",
                                       self.shots_dir + "/shot" + "_" + str(j).zfill(4) + ".mp4"),
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
            j += 1