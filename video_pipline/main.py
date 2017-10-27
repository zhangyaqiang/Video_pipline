# encoding:utf-8
import os
import glob
from video_class import Video
from shot_class import Shot

def main():
    src_video_dir = '/home/zyq/video_pipline_data/test_video'
    shots_root_dir = '/home/zyq/video_pipline_data/test_shots'
    video_list = glob.glob(os.path.join(src_video_dir, '*.mp4'))
    for video in video_list:
        #shots diretor for a video
        shots_dir = os.path.join(shots_root_dir,
                                 os.path.splitext(os.path.basename(video))[0])
        if not os.path.exists(shots_dir):
            os.mkdir(shots_dir)
        _video = Video(video, shots_dir)
        #split video to shots
        _video.extract_shots_with_ffprobe()
        _video.split_video()
        #face detect and tracking in the shot
        shot_list = glob.glob(os.path.join(shots_dir, '*.mp4'))
        for shot in shot_list:
            _shot = Shot(shot)
            #if not statisfy only one face show up around the shot, delete it
            if not _shot.face_detected():
                _shot.delete()
        shot_list = glob.glob(os.path.join(shots_dir, '*.mp4'))
        #determine if the shot av_sync
        for shot in shot_list:
            _shot = Shot(shot)
            _shot.to_frames_wav()
            _shot.to_matdata()
            if not _shot.av_sync():
                _shot.delete()

if __name__ == "__main__":
    main()