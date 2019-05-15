from ..microwave import Temp_process
import time
import threading
import cv2
from socket import *
import struct
import numpy as np
import subprocess
import argparse
import os

class VideoCamera(object):
    def __init__(self):
        # self.video = cv2.VideoCapture(0)

        self.cpp_camera = threading.Thread(target=self.camera_CPP, args=())
        self.cpp_camera.start()

        time.sleep(3)

        (self.grabbed, self.frame) = self.get_image()
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()

        self.clientSock = None
        self.record_flag = False


    # def __del__(self):
    #     self.video.release()

    def camera_CPP(self):
        CPP_path = "/home/pi/Yonsei_deum/camera_MLX90640/MLX90640"
        operator = "sudo "+ CPP_path + " 0.0625 8880"
        if not os.path.isfile(CPP_path):
            print("CPP_file_ doesn`t exixt!!!!! did you make it?")
            print("please check:",CPP_path)
        try:
            subprocess.Popen([operator], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            print("fail to open MLX90640`s CPP file")


    def start_record(self):
        self.TD = Temp_process.Thermal_Data()
        self.record_flag = True

    def close_record(self):
        self.record_flag = False
        del self.TD
        print("record finish")

    def init_socket(self, ip, port):
        clientSock = socket(AF_INET, SOCK_STREAM)
        print("connect start")
        clientSock.connect((ip, port))
        print("connect success")


    def get_frame(self):
        image = self.frame
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:

            try:
                (self.grabbed, self.frame) = self.get_image()
            except:
                print("update camera fail")

    def get_image(self):
        bin_data = self.clientSock.recv(1536)
        # print("len bin data", len(bin_data))
        count = int(len(bin_data) / 2)
        short_arr = struct.unpack('<' + ('h' * count), bin_data)
        np.asarray(short_arr)

        try:
            short_arr = np.reshape(short_arr, (24, 32))

            cut_data = np.zeros((24, 24), np.int8)
            cut_data = self.TD.Thermal_data_cut(short_arr)
            img = np.zeros((24, 24, 3), np.uint8)   ##img will be cutted
            if self.record_flag == True:
               self.TD.run1(cut_data)
            
                
            frame = self.absolute_HSV_Control(cut_data, img)
            return True, frame
        except:
            print("--------------Fail--------------")
            return False, None


    def absolute_HSV_Control(self, data, img):
    ##this is for cuted img

        thickness = 2
        org = ( 2, 478 )
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1.2

        for py in range(24):
            for px in range(24):
                value_2 = 255
                value_3 = 255
                if 3000 >= data[py][px] > 1200: #2000 = 200C  max = 300
                    value_1 = 1
                    value_2 = 255 - ((data[py][px] - 1200) * 254 / 1000) ## 0 = white
                elif data[py][px] > 1000 :
                    value_1 =  5 - ((data[py][px] - 1000)*4 / 200)
                elif data[py][px] > 700 :
                    value_1 = 15 - ((data[py][px] - 700)*10 / 300)
                elif data[py][px] > 600 :
                    value_1 = 30 - ((data[py][px] - 600)*15 / 100)
                elif data[py][px] > 500 :
                    value_1 = 45 - ((data[py][px] - 500)*15 / 100)
                elif data[py][px] > 400 :
                    value_1 = 60 - ((data[py][px] - 400)*15 / 100)
                elif data[py][px] > 300 :
                    value_1 = 75 - ((data[py][px] - 300 )*15 / 100)
                elif data[py][px] > 200 :
                    value_1 = 90 - ((data[py][px] - 200 )*15 / 100)
                elif data[py][px] > 150 :
                    value_1 = 105 - ((data[py][px] - 150 )*15 / 50)
                elif data[py][px] > -100:
                    value_1 = 115 - ((data[py][px] + 100 )*10 / 250)
                elif data[py][px] >= -300 :
                    value_1 = 120
                    value_3 = ((data[py][px] + 300) * 254 / 200) ## 0 = black


                img[py][px][0] = int(value_1)  # 0~180
                img[py][px][1] = int(value_2)
                img[py][px][2] = int(value_3)

        max_tmp = np.amax(data) / 10
        global current_max
        current_max = max_tmp
        text_for_display = "max_temp: " + str(max_tmp) + "  [deum_Yonsei]"
        img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)

        img = cv2.resize(img, None, fx=20, fy=15, interpolation=cv2.INTER_CUBIC)
        cv2.putText(img, text_for_display, org, font , fontScale , (255,255,255) , thickness , cv2.LINE_AA)
        # cv2.imshow('frame', img)
        # cv2.waitKey(1)
        return img


    def realse(self):
        pass
        # threading.Thread(target=self.update, args=()).

