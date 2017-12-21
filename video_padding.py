import os
import glob
from skimage import io
import subprocess

def padding_frames(frame_dir):
    frame_list = glob.glob(os.path.join(frame_dir, '*.png'))
    sorted(frame_list)
    frames_length = len(frame_list)
    if frames_length < 250:
        tail_frame = io.imread(frame_list[-1])
        i = frames_length
        while i < 250:
            image_path = os.path.join(frame_dir, "frame_" + str(i).zfill(4) + ".png")
            # print(image_path)
            io.imsave(image_path, tail_frame)
            i += 1


if __name__ == '__main__':
    dataset_dir = '/home/zyq/video_pipline_data/dataset/ST-1/video_frames/val_set'
    dataset_list = glob.glob(os.path.join(dataset_dir, '00*'))
    for dataset in dataset_list:
        print(dataset + 'start')
        padding_frames(dataset)
        print(dataset + 'done')