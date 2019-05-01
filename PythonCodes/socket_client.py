from socket import *
import numpy as np
import struct
import cv2 as cv

ip = '192.168.219.118'
# ip = '127.0.0.1'
port = 8888

clientSock = socket(AF_INET, SOCK_STREAM)
print("connect start")
clientSock.connect((ip, port))
print("connect success")


def make_hsv(data, img):
    # vmin = np.amin(data)
    # vmax = np.amax(data)
    vmin = 0
    vmax = 200
    vrange = vmax - vmin

    max_H = 250
    if vmax > 2000:
        vmax = 2000
    # min_H = 20 - (vmax / 100)
    min_H = 0
    # print("min H", min_H)

    H_range = max_H - min_H

    for py in range(24):
        for px in range(32):
            value = (H_range * (data[py][px] - vmin) / vrange ) + min_H

            img[py][px][0] = max_H - int(value)  # 0~225
            img[py][px][1] = 255
            img[py][px][2] = 255

    img = cv.cvtColor(img, cv.COLOR_HSV2RGB)
    img = cv.resize(img, None, fx=20, fy=20, interpolation=cv.INTER_CUBIC)
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
        make_hsv(short_arr, img)
    except:
        print("Fail")


