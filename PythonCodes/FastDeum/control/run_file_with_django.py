#new TD.run2 version

import Temp_process_developer as Temp_process
from microwave.manual_controller import ManualController
# import Temp_process_developer as Temp_process
from socket import *
import numpy as np
import struct
import cv2
import threading


import subprocess
import argparse
import os

#from .microwave import Temp_process




ip = '127.0.0.1'
port = 8888
max_power = 10

print("wait for camera connection")

clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect((ip, port))
print("connect success")
# temperature_controller = maxheat.TemperatureController(70)

manual_controller = ManualController()
manual_controller.reset_param(0, 0)
print("reset_the_manual_controller")
TD = Temp_process.Thermal_Data(255)
print("thermal_data_set_up")

check_flag = True
while True:

    bin_data = clientSock.recv(1536)
    count = int(len(bin_data) / 2)
    short_arr = struct.unpack('<' + ('h' * count), bin_data)
    np.asarray(short_arr)

    short_arr = np.reshape(short_arr, (24, 32))
    #img = np.zeros((24, 24, 3), np.uint8)
    Newdata = np.zeros((24,24),np.int16)
    Newdata = TD.Thermal_data_cut(short_arr)
    print("datcut complete")
    # min_tem = TD.run1(Newdata)
    min_tem = TD.run3(Newdata)
    print("run3")
    # Temp_process.absolute_HSV_Control3_cut(Newdata, img,min_tem )
    img = Temp_process.absolute_HSV_Control4(Newdata, min_tem)

    stop_wave = manual_controller.run()

    if stop_wave:
        if check_flag:
            write_stop = open("status.txt", "w")
            write_stop.write("0 0 0")
            write_stop.close()
            check_flag = False
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            #cv2.namedWindow("empty")

    read_status = open("status.txt", "r")
    line = read_status.readline()
    read_status.close()

    split = line.split(" ")
    status = split[0]

    if status == "1":
         if stop_wave:
            # 꺼져있다가 켜짐
            TD.reset_var()
            power = int(split[1])
            duration = int(split[2])
            manual_controller.reset_param(power, duration)
            check_flag = True
            print("----------------restart_microwave_over--------------")
        cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)

        cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("frame", img)

    cv2.waitKey(1)