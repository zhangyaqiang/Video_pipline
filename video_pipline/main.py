# encoding:utf-8
import os
import glob
from video_class import Video
from shot_class import Shot
from Asr import Asr

def main():
    src_video_dir = '/home/zyq/video_pipline_data/test_video'
    shots_root_dir = '/home/zyq/video_pipline_data/test_shots'
    video_list = glob.glob(os.path.join(src_video_dir, '*.mp4'))
    for video in video_list:
        print (video, "started")
        #shots diretor for a video
        shots_dir = os.path.join(shots_root_dir,
                                 os.path.splitext(os.path.basename(video))[0])
        if not os.path.exists(shots_dir):
            os.mkdir(shots_dir)
            print ("    dir created")
        _video = Video(video, shots_dir)
        #split video to shots
        _video.to_wav()
        print ("    video has converted to wav")
        _video.extract_shots_with_ffprobe()
        print ("    shot boundaries have been extracted")
        _video.split_video()
        print("     video has been splited")
        #face detect and tracking in the shot
        shot_list = glob.glob(os.path.join(shots_dir, 'shot*'))
        for shot in shot_list:
            _shot = Shot(shot)
            #if not statisfy only one face show up around the shot, delete it
            if not _shot.face_detected():
                _shot.delete()
                print ("    no face in", shot, ", deleted")
        shot_list = glob.glob(os.path.join(shots_dir, 'shot*'))
        #determine if the shot av_sync
        for shot in shot_list:
            _shot = Shot(shot)
            _shot.get_video_frames()
            print (_shot.shot_name+"has got video_frames")
            _shot.get_frames_mouth()
            print (_shot.shot_name+"has got mouth frames")
            _shot.to_frames_wav()
            print (_shot.shot_name+"has got shot name")
            if not _shot.av_sync():
                _shot.delete()
                print ("    audio video not sync", shot, "deleted")
        shot_list = glob.glob(os.path.join(shots_dir, 'shot*'))
        for shot in shot_list:
            _shot = Shot(shot)
            _shot.asr()


if __name__ == "__main__":
    main()