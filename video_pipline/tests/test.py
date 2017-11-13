# encoding:utf-8
import os
import glob
from video_pipline.video_class import Video
from video_pipline.shot_class import Shot
import subprocess
import multiprocessing as mp

def pipline(video):
    print (video, "started")
    #shots diretor for a video
    shots_dir = os.path.join(shots_root_dir,
                             os.path.splitext(os.path.basename(video))[0])
    # if not os.path.exists(shots_dir):
    #     os.mkdir(shots_dir)
    #     print ("    dir created")
    # _video = Video(video, shots_dir)
    # # split video to shots
    # _video.to_wav()
    # print ("    video has converted to wav")
    # _video.extract_shots_with_ffprobe()
    # print ("    shot boundaries have been extracted")
    # _video.split_video()
    # print("     video has been splited")
    # face detect and tracking in the shot
    shot_list = glob.glob(os.path.join(shots_dir, 'shot*'))
    for shot in shot_list:
        print("        ", shot, "begin face detect")
        _shot = Shot(shot)
        # if not statisfy only one face show up around the shot, delete it
        if not _shot.face_detected():
            _shot.delete()
            print ("            no face in", shot, ", deleted")
        print("        ", shot, "done")
    shot_list = glob.glob(os.path.join(shots_dir, 'shot*'))
    # determine if the shot av_sync
    for shot in shot_list:
        print("        ", shot, "begin av_sync")
        _shot = Shot(shot)
        _shot.get_video_frames()
        # print (_shot.shot_name+"has got video_frames")
        _shot.get_frames_mouth()
        # print (_shot.shot_name+"has got mouth frames")
        _shot.to_frames_wav()
        # print (_shot.shot_name+"has got shot name")
        if not _shot.av_sync():
            _shot.delete()
            print ("            audio video not sync", shot, "deleted")
        print("        ", shot, "av_sync done")
    shot_list = glob.glob(os.path.join(shots_dir, 'shot*'))
    for shot in shot_list:
        print("        ", shot, "begin asr")
        _shot = Shot(shot)
        if not _shot.asr():
            continue
        _shot.get_labels()
        print("        ", shot, "done")

    subprocess.Popen(('mv',
                     video,
                     '/home/zyq/video_pipline_data/finished_video'),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)

    print(video, 'has finished')


if __name__ == "__main__":
    src_video_dir = '/home/zyq/video_pipline_data/news'
    shots_root_dir = '/home/zyq/video_pipline_data/shots'
    video_list = ['/home/zyq/video_pipline_data/shots/201706111900',
                  '/home/zyq/video_pipline_data/shots/201702281900',
                  '/home/zyq/video_pipline_data/shots/201701112100',
                  '/home/zyq/video_pipline_data/shots/201703291900',
                  ]

    pool = mp.Pool(processes=4)
    pool.map(pipline, video_list)