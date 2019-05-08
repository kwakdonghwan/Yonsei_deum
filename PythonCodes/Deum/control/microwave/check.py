from socket import *
import numpy as np
import struct
import cv2 as cv
import subprocess
import Temp_process


#ip = '172.24.221.208'
ip = '127.0.0.1'
port = 8888

clientSock = socket(AF_INET, SOCK_STREAM)
print("connect start")
clientSock.connect((ip, port))
print("connect success")


TD = Temp_process.Thermal_Data(200)
print("Thermal_Data is ready")

def absolute_HSV_Control (data, img):

    thickness = 2
    org = ( 2, 478 )
    font = cv.FONT_HERSHEY_SIMPLEX
    fontScale = 1.2

    for py in range(24):
        for px in range(32):
            value_2 = 255
            value_3 = 255
            if 3000 >= data[py][px] > 2000: #2000 = 200C  max = 300
                value_1 = 1
                value_2 = 255 - ((data[py][px] - 2000) * 254 / 1000) ## 0 = white
            elif data[py][px] > 1000 :
                value_1 =  10 - ((data[py][px] - 1000)*9 / 1000)
            elif data[py][px] > 800 :
                value_1 = 25 - ((data[py][px] - 800)*15 / 200)
            elif data[py][px] > 600 :
                value_1 = 45 - ((data[py][px] - 600)*20 / 200)
            elif data[py][px] > 400 :
                value_1 = 90 - ((data[py][px] - 400)*45 / 200)
            elif data[py][px] > 200 :
                value_1 = 135 - ((data[py][px] - 200)*45 / 200)
            elif data[py][px] > 0 :
                value_1 = 175 - ((data[py][px] )*40 / 200)
            elif data[py][px] > -100:
                value_1 = 179 - ((data[py][px] + 100 )*4 / 100)
            elif data[py][px] >= -300 :
                value_1 = 179
                value_3 = ((data[py][px] + 300) * 254 / 200) ## 0 = black


            img[py][px][0] = int(value_1)  # 0~180
            img[py][px][1] = int(value_2)
            img[py][px][2] = int(value_3)

    max_tmp = np.amax(data) / 10
    text_for_display = "max_temp: " + str(max_tmp) + "  [deum_Yonsei]"
    img = cv.cvtColor(img, cv.COLOR_HSV2RGB)
    img = cv.resize(img, None, fx=20, fy=20, interpolation=cv.INTER_CUBIC)
    cv.putText(img, text_for_display, org, font , fontScale , (255,255,255), thickness , cv.LINE_AA)
    cv.imshow('frame', img)
    cv.waitKey(1)  # & 0xFF == ord('q')





while True:
    bin_data = clientSock.recv(1536)
    # print("len bin data", len(bin_data))
    count = int(len(bin_data) / 2)
    short_arr = struct.unpack('<' + ('h' * count), bin_data)
    # print('받은 데이터 : ', short_arr)
    # print(np.shape(short_arr))
    np.asarray(short_arr)
    try:
        short_arr = np.reshape(short_arr, (24, 32))
        img = np.zeros((24, 32, 3), np.uint8)
        ##make_hsv(short_arr, img)
        absolute_HSV_Control (short_arr, img)
        print('img_showed')
        TD.run1(short_arr)
    except:
        print("Fail")


