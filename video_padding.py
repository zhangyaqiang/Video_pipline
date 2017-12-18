import os
import glob
from skimage import io

def padding_frames(frame_dir):
    frame_list = glob.glob(os.path.join(frame_dir, '*.png'))
    # print(frame_list)
    sorted(frame_list)
    frames_length = len(frame_list)
    if frames_length < 250:
        tail_frame = io.imread(frame_list[-1])
        i = frames_length
        while i < 250:
            image_path = os.path.join(frame_dir, "frame_" + str(i).zfill(4) + ".png")
            print(image_path)
            io.imsave(image_path, tail_frame)
            i += 1


if __name__ == '__main__':
    dataset_dir = '/home/zyq/video_pipline_data/test/dataset_avi/test1000'
    dataset_list = glob.glob(os.path.join(dataset_dir, '00*'))
    for dataset in dataset_list:
        padding_frames(dataset)
        print(dataset + 'done')