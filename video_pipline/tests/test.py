#encoding:utf-8
from __future__ import division
import subprocess
import os
import cv2
from skimage import io,color,transform,img_as_ubyte


def merge_avi_wav(avi_path, wav_path, shot_path):
    ps = subprocess.Popen(("ffmpeg",
                           "-i",
                           wav_path,
                           "-i",
                           avi_path,
                           "-vcodec",
                           "copy",
                           "-acodec",
                           "copy",
                           shot_path),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)

def split_wav(start_time, end_time, wav_path, src_wav_path):
    ps = subprocess.Popen(("ffmpeg",
                           "-i",
                           src_wav_path,
                           "-ss",
                           str(start_time),
                           "-to",
                           str(end_time),
                           "-ac",
                           "1",
                           "-ar",
                           "16000",
                           wav_path),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    out = ps.stdout.read()
    print out

def to_wav(video_path, src_wav_path):
    ps = subprocess.Popen(("ffmpeg",
                           "-i",
                            video_path,
                           "-ac",
                           "1",
                           "-ar",
                           "16000",
                           src_wav_path),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    output = ps.stdout.read()
    print output

def extract_shots_with_ffprobe(src_video, threshold=0):
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
                                 "movie=" + src_video + ",select=gt(scene\," + str(threshold) + ")"),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    output = scene_ps.stdout.read()
    print output
    boundaries = extract_boundaries_from_ffprobe_output(output)
    return boundaries


def extract_boundaries_from_ffprobe_output(output):
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

video_path = '/home/zyq/video_pipline_data/test_video/news201710101900.mp4'
# boundaries = extract_shots_with_ffprobe(video_path, 0.3)
# bound_len = len(boundaries)
# # 当前帧数
# frame_num = 1
# # 第几个镜头
# bound_num = 0
# # 长度大于3s的镜头
# shot_num = 0
#
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# shots_dir = '/home/zyq/video_pipline_data/test_shots'
# shot_dir = os.path.join(shots_dir, "shot_" + str(shot_num).zfill(4))
# if not os.path.exists(shot_dir):
#     os.mkdir(shot_dir)
# shot_path = os.path.join(shot_dir, "shot_" + str(shot_num).zfill(4) + ".mp4")
# avi_path = os.path.join(shot_dir, "shot_" + str(shot_num).zfill(4) + ".avi")
# wav_path = os.path.join(shot_dir, "shot_" + str(shot_num).zfill(4) + ".wav")
# out = cv2.VideoWriter(avi_path, fourcc, 25, (640, 480))
cap = cv2.VideoCapture(video_path)
# src_wav_path = os.path.join(shots_dir, os.path.splitext(os.path.basename(video_path))[0] + ".wav")

# if (boundaries[0] - 0 < 3):
#     bound_num += 1
#     while (boundaries[bound_num + 1] - boundaries[bound_num] < 3):
#         bound_num += 1
#     start_frame = int(boundaries[bound_num] / 0.04)
#     end_frame = int(boundaries[bound_num + 1] / 0.04)
#     split_wav(boundaries[bound_num], boundaries[bound_num + 1] - 0.04, wav_path)
# else:
#     start_frame = 1
#     end_frame = int(boundaries[0] / 0.04)
#     split_wav(0, boundaries[0] - 0.04, wav_path, src_wav_path)
video_path = '/home/zyq/video_pipline_data/test_video/news201710101900.mp4'
avi_path = '/home/zyq/video_pipline_data/test_shots/shot_0000/shot_0001.avi'
cap = cv2.VideoCapture(video_path)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(avi_path, fourcc, 25, (720, 576))
i = 1
start = int(17.92/0.04)
end = int(93.56/0.04)-1
while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.resize(frame, (720, 576), interpolation=cv2.INTER_CUBIC)
    if not ret:
        print ("no image")
        break;
    if i < start:
        i += 1
        continue
    elif i < end:
        out.write(frame)
    elif i == end:
        out.release()
        break
    i += 1
    cv2.imshow("a", frame)
    k = cv2.waitKey(1)
    if k == 27: break  # esc pressed
cap.release()