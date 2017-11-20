import os
import glob
import subprocess
import cv2

class Label(object):
    def __init__(self, label_file=None):
        if label_file == None:
            raise AttributeError("no label file error")
        self.sen_boundaries = []
        self.label_file = label_file
        self.par_dir = os.path.dirname(label_file)
        self.finaldata_dir = os.path.join(self.par_dir, 'finaldata')
        self.wav_path = glob.glob(os.path.join(self.par_dir, '*.wav'))[0]
        if not os.path.exists(self.finaldata_dir):
            os.mkdir(self.finaldata_dir)

    def split_label(self):
        output = open(self.label_file, 'r', encoding='utf-8')
        sentences = output.readlines()
        row = 0
        row_len = len(sentences)
        for sentence in sentences:
            if row == 0:
                start = int(sentence.split(' ')[0])
                end = int(sentence.split(' ')[1])
                if end > 500:
                    start = end - 500
                    while start % 40 != 0:
                        start += 1
                    start_time = start
                    self.sen_boundaries.append(start_time)
                else:
                    start_time = 0
                    self.sen_boundaries.append(0)
                sen_num = 0
                sen_dir = os.path.join(self.finaldata_dir, 'data_' + str(sen_num))
                if not os.path.exists(sen_dir):
                    os.mkdir(sen_dir)
                label_path = os.path.join(sen_dir, 'label.align')
                f = open(label_path, 'w', encoding='utf-8')
                f.write(str(start-start_time) + ' ' + str(end-start_time) + ' ' + 'sil\n')
            elif sentence.split(' ')[-1][0] == '，':
                start = int(sentence.split(' ')[0])
                end = int(sentence.split(' ')[1])
                next_end = end
                mid = int((start + end) / 2)
                while mid % 40 != 0:
                    mid += 1
                start = str(start - start_time)
                end = str(mid - start_time)
                word = "sil\n"
                f.write(start + ' ' + end + ' ' + word)
                start_time = mid
                sen_num += 1
                self.sen_boundaries.append(mid)
                f.close()

                sen_dir = os.path.join(self.finaldata_dir, 'data_' + str(sen_num))
                if not os.path.exists(sen_dir):
                    os.mkdir(sen_dir)
                label_path = os.path.join(sen_dir, 'label.align')
                f = open(label_path, 'w', encoding='utf-8')
                start = str(0)
                end = str(next_end-start_time)
                if next_end-start_time > 0:
                    f.write(start + ' ' + end + ' ' + 'sil\n')
            else:
                start = int(sentence.split(' ')[0])
                end = int(sentence.split(' ')[1])
                word = sentence.split(' ')[-1]
                if row == row_len-1:
                    if end - start > 500:
                        end = start + 450
                        while end % 40 != 0:
                            end += 1
                    self.sen_boundaries.append(end)
                if start - start_time > 0:
                    f.write(str(start-start_time) + ' ' + str(end-start_time) + '' + word)
                else:
                    f.write(str(0) + ' ' + str(end-start_time) + '' + word)
            row += 1
        f.close()


    def split_video(self):
        src_avi_path = glob.glob(os.path.join(self.par_dir, '*.avi'))[0]
        sen_num = 0
        sen_len = len(self.sen_boundaries)
        frame_num = 1

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        dir_path = os.path.join(self.finaldata_dir, 'data_' + str(sen_num))
        mp4_path = os.path.join(dir_path, "video.mp4")
        avi_path = os.path.join(dir_path, "video.avi")
        wav_path = os.path.join(dir_path, "video.wav")
        out = cv2.VideoWriter(avi_path, fourcc, 25, (720, 576))

        cap = cv2.VideoCapture(src_avi_path)

        start_frame = int(self.sen_boundaries[0]/40)+1
        end_frame = int(self.sen_boundaries[1]/40)

        self.split_wav(self.sen_boundaries[0]/1000, self.sen_boundaries[1]/1000, wav_path)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("done")
                break;
            if frame_num < start_frame:
                frame_num += 1
                continue
            elif frame_num < end_frame:
                out.write(frame)
            elif frame_num == end_frame:
                out.write(frame)
                out.release()
                self.merge_avi_wav(avi_path, wav_path, mp4_path)
                sen_num += 1

                if sen_num == sen_len-1: return

                dir_path = os.path.join(self.finaldata_dir, 'data_' + str(sen_num))
                mp4_path = os.path.join(dir_path, "video.mp4")
                avi_path = os.path.join(dir_path, "video.avi")
                wav_path = os.path.join(dir_path, "video.wav")
                out = cv2.VideoWriter(avi_path, fourcc, 25, (720, 576))

                start_frame = int(self.sen_boundaries[sen_num] / 40) + 1
                end_frame = int(self.sen_boundaries[sen_num+1] / 40)
                self.split_wav(self.sen_boundaries[sen_num] / 1000, self.sen_boundaries[sen_num+1] / 1000, wav_path)
            frame_num += 1

    def split_wav(self, start_time, end_time, wav_path):
        ps = subprocess.Popen(("ffmpeg",
                               "-y",
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
                               "-y",
                               "-i",
                               wav_path,
                               "-i",
                               avi_path,
                               "-vcodec",
                               "copy",
                               shot_path),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        output = ps.stdout.read()

