# _*_ coding: utf-8 _*_
from pypinyin import pinyin, lazy_pinyin, Style
import urllib.request
import urllib.parse
import json as JSON
import base64
import os
import time
import glob
import subprocess
from aip import AipSpeech
import socket

APP_ID = '10545007'
API_KEY = 'HeQhAqUweP09rY9ytpKbuboM'
SECRET_KEY = '000d6809528757f39e901b14063186e4'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

class BaiduRest:
    def __init__(self, cu_id, api_key, api_secert):
        # token认证的url
        self.token_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s"
        # 语音合成的resturl
        self.getvoice_url = "http://tsn.baidu.com/text2audio?tex=%s&lan=zh&cuid=%s&ctp=1&tok=%s"
        # 语音识别的resturl
        self.upvoice_url = 'http://vop.baidu.com/server_api'
        self.cu_id = cu_id
        self.getToken(api_key, api_secert)
        return

    def getToken(self, api_key, api_secert):
        # 1.获取token
        token_url = self.token_url % (api_key, api_secert)
        r_str = urllib.request.urlopen(token_url).read().decode('utf8')
        token_data = JSON.loads(r_str)
        self.token_str = token_data['access_token']
        pass

    def getVoice(self, text, filename):
        # 2. 向Rest接口提交数据
        get_url = self.getvoice_url % (urllib.parse.quote(text), self.cu_id, self.token_str)

        voice_data = urllib.request.urlopen(get_url).read()
        # 3.处理返回数据
        voice_fp = open(filename, 'wb+')
        voice_fp.write(voice_data)
        voice_fp.close()
        pass

    def getText(self, filename):
        # 2. 向Rest接口提交数据
        data = {}
        # 语音的一些参数
        data['format'] = 'wav'
        data['rate'] = 16000
        data['channel'] = 1
        data['cuid'] = self.cu_id
        data['token'] = self.token_str
        wav_fp = open(filename, 'rb')
        voice_data = wav_fp.read()
        data['len'] = len(voice_data)
        data['speech'] = base64.b64encode(voice_data).decode('utf-8')
        post_data = JSON.dumps(data)
        r_data = urllib.request.urlopen(self.upvoice_url, data=bytes(post_data, encoding="utf-8")).read().decode('utf8')
        # 3.处理返回数据
        if JSON.loads(r_data)['err_no'] != 0:
            return 'err'
        return JSON.loads(r_data)['result']



class Asr(object):
    def __init__(self, wav_path=None):
        if wav_path == None:
            raise AttributeError("no .wav file")

        self.wav_path = wav_path
        self.par_path = os.path.dirname(wav_path)
        self.textgrid_dir = os.path.join(self.par_path, "textgrid")
        if not os.path.exists(self.textgrid_dir):
            os.mkdir(self.textgrid_dir)
        #self.textgrid_path = os.path.join(self.textgrid_dir, "Textgrid.textgrid")
        self.dic_path = os.path.join(self.par_path, "dictionary.txt")
        self.alignment_dir = os.path.join(self.par_path, "alignment")
        if not os.path.exists(self.alignment_dir):
            os.mkdir(self.alignment_dir)
        self.lab_path = os.path.join(self.alignment_dir, os.path.splitext(os.path.basename(wav_path))[0] + ".lab")
        subprocess.Popen(('cp',
                          self.wav_path,
                          self.alignment_dir))
        self.label_path = os.path.join(self.par_path, "label.txt")

        self.rhyme = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's', 'y', 'w']
        # 21个声母  wy
        self.consonant = ['a', 'ai', 'ao', 'e', 'ei', 'i', 'ii', 'ia', 'iao', 'ie', 'io', 'iou', 'iu', 'o', 'ou', 'u', 'ua',
                     'ue', 'uo', 'uai', 'uei', 'v', 'va', 've', ]
        # 24个韵母
        self.phonetic = ['1', '2', '3', '4', '5']
        self.special = ['yi', 'ya', 'ye', 'yo', 'yu', 'w', 'ju', 'qu', 'xu', 'ui', 'un']
        self.special_consonant = ['ii', 'ia', 'ie', 'io', 'v', 'u', 'jv', 'qv', 'xv', 'uei', 'uen']

        self.num0 = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
        self.kin = ['十', '百', '千', '万', '零']

        self.rhymeout = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's']


        self.phonetic_path = '/home/zyq/PycharmProjects/alignment/python-pinyin-master/pypinyin/phonetic.txt'

        #百度语音识别接口
        self.api_key = "HeQhAqUweP09rY9ytpKbuboM"
        self.api_secret = "000d6809528757f39e901b14063186e4"
        self.bdr = BaiduRest("test", self.api_key, self.api_secret)

        #text是百度语音识别的结果
        self.text = None
        #将数字转成汉字
        self.wenben = None
        #汉字和对应的拼音
        self.word_pinyin = None
        #纯拼音
        self.pinyin = None

    #获取ASR的结果
    # def get_text(self):
    #     bairesult = self.bdr.getText(self.wav_path)
    #     if bairesult == 'err':
    #         return False
    #     bairesult = str(bairesult[0])
    #     bairesult = bairesult[:-1]
    #     for ch in bairesult:
    #         if (ch >= 'a' and ch <='z') or (ch >= 'A' and ch <= 'Z'):
    #             return False
    #     self.text = bairesult
    #     return True

    def get_file_content(self, filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    def getText(self, wav_path):
        try:
            res = client.asr(self.get_file_content(wav_path),
                         'wav',
                         16000)
            if res['err_no'] != 0:
                return 'err'
            else:
                return res['result']
        except :return 'err'


    def get_text(self):
        try:
            bairesult = self.getText(self.wav_path)
        except socket.timeout:
            try: bairesult = self.getText(self.wav_path)
            except socket.timeout: return False

        if bairesult == 'err':
            return False
        bairesult = str(bairesult[0])
        bairesult = bairesult[:-1]
        for ch in bairesult:
            if (ch >= 'a' and ch <='z') or (ch >= 'A' and ch <= 'Z'):
                return False
        self.text = bairesult
        return True

    #将结果中的数字转成汉字，并存为.lab文件
    def get_lab(self):
        index = 0
        mandarin = open(self.lab_path, "w", encoding="utf-8")
        str = self.text
        while index < len(str):
            num = ""
            if str[index].isdigit():

                n = index
                while n < len(str) and str[n].isdigit():
                    num = num + str[n]
                    n += 1
                if n < len(str) and str[n] == ".":
                    n += 1
                    num_dot = ""
                    while n < len(str) and str[n].isdigit():
                        num_dot = num_dot + str[n]
                        n += 1
                    new_num = self.change_num(num) + "点" + self.change_year(num_dot)
                else:
                    if len(num) == 4:
                        if n < len(str):
                            if str[n] != "年":
                                new_num = self.change_num(num)
                            else:
                                new_num = self.change_year(num)
                        else:
                            new_num = self.change_year(num)
                        new_num = self.change_year(num)
                    elif num[0] == "0":
                        new_num = self.change_year(num)
                    else:
                        new_num = self.change_num(num)
                if n < len(str) and str[n] == "%":
                    new_num = "百分之" + new_num
                    n += 1
                str = str[:index] + new_num + str[n:]
                index = n
            index += 1
        self.wenben = str
        mandarin.write(str)
        print(".lab has been generated")

    #获取汉字对应的拼音
    def get_pinyin(self):
        line = self.wenben
        x = pinyin(line.rstrip(), style=Style.TONE3)
        self.word_pinyin = line.rstrip()+'\t'
        x = [str(i) for i in x]
        for ele in x:
            ele = ele.lstrip('[').rstrip(']').rstrip()
            ele = eval(ele)
            self.word_pinyin = self.word_pinyin + ele.rstrip() + ' '
            if self.pinyin == None:
                self.pinyin = ele.rstrip() + ' '
            else:
                self.pinyin = self.pinyin + ele.rstrip() + ' '
        print ("pinyin has generated")


    #获取音素
    def get_phoneme(self):
        line = self.word_pinyin
        dictionary = open(self.dic_path, 'w', encoding='utf-8')
        dictionary.write("\n")
        var0 = line
        var0 = var0.rstrip()
        var1 = var0.split("\t", 1)[1]
        var2 = self.replace(var1)

        dictionary.write(var0.split("\t", 1)[0] + "\t")
        for index4 in range(len(var2)):
            if index4 == 0:
                dictionary.write(var2[index4])
            else:
                dictionary.write(" " + var2[index4])
        dictionary.write("\n")
        dictionary.close()
        print("dictionary han generated")

    def alignment(self):
        ps = subprocess.Popen(('/home/zyq/Downloads/montreal-forced-aligner/bin/mfa_align',
                         self.alignment_dir,
                         self.dic_path,
                         '/home/zyq/Downloads/montreal-forced-aligner/bin/mandarin.zip',
                         self.textgrid_dir),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)

        output = ps.stdout.read()
        print(output)
        time.sleep(5)
        line_tr = self.wenben
        phonetic = open(self.phonetic_path, encoding="utf-8")
        line_se = self.pinyin
        line_ph = phonetic.readlines()

        in_tr = 0
        in_ph = 0
        in_se = 0
        pt = 0

        while in_ph < len(line_ph):
            line_ph[in_ph] = line_ph[in_ph].rstrip()
            in_ph += 1

        line_se = line_se.rstrip()

        grid_list = glob.glob(os.path.join(self.textgrid_dir, "alignment/*.TextGrid"))
        if len(grid_list) == 0:
            ps = subprocess.Popen(('/home/zyq/Downloads/montreal-forced-aligner/bin/mfa_align',
                                   self.alignment_dir,
                                   self.dic_path,
                                   '/home/zyq/Downloads/montreal-forced-aligner/bin/mandarin.zip',
                                   self.textgrid_dir),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)

            output = ps.stdout.read()
            print(output)
            time.sleep(5)
            line_tr = self.wenben
            phonetic = open(self.phonetic_path, encoding="utf-8")
            line_se = self.pinyin
            line_ph = phonetic.readlines()

            in_tr = 0
            in_ph = 0
            in_se = 0
            pt = 0

            while in_ph < len(line_ph):
                line_ph[in_ph] = line_ph[in_ph].rstrip()
                in_ph += 1

            line_se = line_se.rstrip()
            grid_list = glob.glob(os.path.join(self.textgrid_dir, "alignment/*.TextGrid"))
            if len(grid_list) == 0:
                return False
        textgrid_path = grid_list[0]
        textgrid = open(textgrid_path, encoding="utf-8")
        line_text = textgrid.readlines()
        self.writein(self.label_path, line_text, line_tr, line_se, line_ph)
        print("alignment has generated")
        return True



    def has_num(slef, str):
        return any(char.isdigit() for char in str)

    def change_year(self, list):
        new = ""
        num_year = 0
        while num_year < len(list):
            if list[num_year] == "1":
                new = new + "一"
            elif list[num_year] == "2":
                new = new + "二"
            elif list[num_year] == "3":
                new = new + "三"
            elif list[num_year] == "4":
                new = new + "四"
            elif list[num_year] == "5":
                new = new + "五"
            elif list[num_year] == "6":
                new = new + "六"
            elif list[num_year] == "7":
                new = new + "七"
            elif list[num_year] == "8":
                new = new + "八"
            elif list[num_year] == "9":
                new = new + "九"
            elif list[num_year] == "0":
                new = new + "零"
            num_year += 1
        return new

    def d1(self, x):
        if '零' in x:
            a = x.index('零')
            if a == 0:
                del x[0]
                self.d1(x)
            else:
                if x[a + 2] in ['十', '百', '千', '万', '零']:
                    if x[a + 1] != '万':
                        del x[a + 1]
                        self.d1(x)
        return x


    def d2(self, x):
        try:
            a = x.index('零')
            if x[a - 1] in ['十', '百', '千', '零']:
                del x[a - 1]
                self.d2(x[a + 1])
        except:
            pass
        return x


    def fw(self, x):
        if len(x) >= 9:
            if x[8] == '零':
                del x[8]
        return x


    def dl(self, x):
        try:
            if x[0] == '零':
                del x[0]
        except:
            pass
        x.reverse()
        x = ''.join(x)
        return x

    def change_num(self, str):
        x = list(str)
        for j in x:
            x[(x.index(j))] = self.num0[int(j)]
        x.reverse()
        if len(x) >= 2:
            x.insert(1, self.kin[0])
            if len(x) >= 4:
                x.insert(3, self.kin[1])
                if len(x) >= 6:
                    x.insert(5, self.kin[2])
                    if len(x) >= 8:
                        x.insert(7, self.kin[3])
                        if len(x) >= 10:
                            x.insert(9, self.kin[0])
                            if len(x) >= 12:
                                x.insert(11, self.kin[1])

        x = self.fw(x)
        x = self.d1(x)
        x = self.d2(x)
        x = self.dl(x)
        return x




    def segment(self, str):
        index1 = 0
        while index1 < len(str):
            if str[index1][len(str[index1]) - 1].isalpha():
                str[index1] = str[index1] + "5"
            for index2 in range(len(self.rhyme)):
                index3 = str[index1].find(self.rhyme[index2], 0, 2)
                if index3 >= 0:
                    if (self.rhyme[index2] == "z" or self.rhyme[index2] == "s" or self.rhyme[index2] == "c") and str[index1][
                                index3 + 1] == "h":
                        pass
                    elif (self.rhyme[index2] == "n" or self.rhyme[index2] == "r") and index3 > 0:
                        pass
                    else:
                        str[index1] = str[index1][:index3 + 1] + " " + str[index1][index3 + 1:]
            index3 = str[index1].find(" ") + 1
            index4 = str[index1].find("n", index3)
            index5 = str[index1].find("r", index3)
            if index4 >= 0:
                str[index1] = str[index1][:index4] + str[index1][len(str[index1]) - 1] + " " + str[index1][index4:len(
                    str[index1]) - 1]
            if index5 >= 0:
                str[index1] = str[index1][:index5] + str[index1][len(str[index1]) - 1] + " " + str[index1][index5:len(
                    str[index1]) - 1]
            if str[index1] == "，":
                str[index1] = "sil"
            index1 += 1
        return str

    def segmenta(self ,str):
        index1 = 0
        rhymeout = self.rhymeout
        while index1 < len(str):
            if str[index1][len(str[index1]) - 1].isalpha():
                str[index1] = str[index1] + "5"
            for index2 in range(len(rhymeout)):
                index3 = str[index1].find(rhymeout[index2], 0, 2)
                if index3 >= 0:
                    if (rhymeout[index2] == "z" or rhymeout[index2] == "s" or rhymeout[index2] == "c") and str[index1][
                            index3 + 1] == "h":
                        pass
                    elif (rhymeout[index2] == "n" or rhymeout[index2] == "r") and index3 > 0:
                        pass
                    else:
                        str[index1] = str[index1][:index3 + 1] + " " + str[index1][index3 + 1:]
            index3 = str[index1].find(" ") + 1
            index4 = str[index1].find("n", index3)
            index5 = str[index1].find("r", index3)
            if index4 >= 0:
                str[index1] = str[index1][:index4] + str[index1][len(str[index1]) - 1] + " " + str[index1][index4:len(
                    str[index1]) - 1]
            if index5 >= 0:
                str[index1] = str[index1][:index5] + str[index1][len(str[index1]) - 1] + " " + str[index1][index5:len(
                    str[index1]) - 1]
            index1 += 1
        return str

    def replacea(self, str):
        special = self.special
        special_consonantout = self.special_consonant
        for index1 in range(len(special)):
            str = str.replace(special[index1], special_consonantout[index1])
            str = str.replace("uu", "u")
        return self.segmenta(str.split(" "))

    def replace(self, str):
        for index1 in range(len(self.special)):
            str = str.replace(self.special[index1], self.special_consonant[index1])
            str = str.replace("uu", "u")
        return self.segment(str.split(" "))

    def createlab(self, wavpath, alltxtpath, labpath):
        # 打开wav文件目录
        txtaline = []
        i = 0
        pathDir = os.listdir(wavpath)
        # 打开总的transcription的txt文件
        output = open(alltxtpath, 'r', encoding='utf-8')
        all_lines = output.readlines()
        for aline in all_lines:
            txtaline.append(aline)
        output.close()
        for allDir in pathDir:
            # 1.创建相应txt
            # 2.打开相应txt
            allDir = allDir.replace("wav", "txt")
            obj = open(labpath + "/" + allDir, 'w', encoding='utf-8')
            # 3.将output的一行写入txt中
            obj.write('%s' % txtaline[i].rstrip() + '\n')
            # 4.关掉相应的txt
            obj.close()
            i += 1
        # 将txt替换为lab
        pathDir = os.listdir(labpath)
        for allDir in pathDir:
            portion = os.path.splitext(allDir)
            if portion[1] == ".txt":
                newname = portion[0] + ".lab"
                os.rename(labpath + "/" + allDir, labpath + "/" + newname)

    def writein(self, path, line_text, line_tr, line_se, line_ph):
        phone = ""
        text = ""
        in_text = 0
        num = 0
        xmin = []
        xmax = []
        bmin = 0
        bmax = 0
        emin = 0
        emax = 0

        output = open(path, 'w', encoding="utf-8")

        while len(text) == 0 and in_text < len(line_text):
            if "\"" + line_tr + "\"" in line_text[in_text]:
                text = line_tr  # 获取文字
            in_text += 1
        phone0 = self.replacea(line_se)
        sil_begin = 0
        sil_end = 0
        while in_text < len(line_text):  # 判断字音的时间
            in_ph = 0
            find = 0
            while in_ph < len(line_ph) and find == 0:
                if "\"sil\"" in line_text[in_text]:
                    if sil_begin == 0:
                        sil_begin = 1
                        bmin = float(line_text[in_text - 2].split(" = ")[1].rstrip())
                        bmax = float(line_text[in_text - 1].split(" = ")[1].rstrip())
                        find = 1
                    else:
                        xmin.append(float(line_text[in_text - 2].split(" = ")[1].rstrip()))
                        xmax.append(float(line_text[in_text - 1].split(" = ")[1].rstrip()))
                        find = 1
                        num += 1
                if "\"\"" in line_text[in_text]:
                    sil_end = 1
                    emax = float(line_text[in_text - 1].split(" = ")[1].rstrip())
                if "\"" + line_ph[in_ph] + "\"" in line_text[in_text]:
                    sil_begin = 1
                    if len(phone) == 0:
                        xmin.append(float(line_text[in_text - 2].split(" = ")[1].rstrip()))
                        phone = phone + line_ph[in_ph]
                    else:
                        phone = phone + " " + line_ph[in_ph]  # 获取音素line_ph[in_ph]
                    find = 1
                in_ph += 1
                if num < len(phone0) and phone == phone0[num]:
                    xmax.append(float(line_text[in_text - 1].split(" = ")[1].rstrip()))
                    num += 1
                    phone = ""
            in_text += 1

        op = 0
        if sil_begin == 1:
            output.write(str(int(bmin * 1000)) + " " + str(int(bmax * 1000)) + " sil\n")

        while op < len(text):
            output.write(str(int(xmin[op] * 1000)) + " " + str(int(xmax[op] * 1000)) + " " + text[op] + "\n")
            op += 1

        if sil_end == 1:
            output.write(str(int(xmax[op - 1] * 1000)) + " " + str(int(emax * 1000)) + " sil\n")

        del xmax[:]
        del xmin[:]
        output.close()
        print("label has generated")

