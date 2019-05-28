from status_io import *
import auto_contorol as auto_control
import Temp_process_developer as Temp_process
import advanced_thermal_control as atc
from microwave.manual_controller import ManualController
from subprocess import Popen,PIPE

from socket import *
import struct
import numpy as np
import cv2
import time

import os, sys


ip = '127.0.0.1'
port = 8888
max_power = 10

print("wait for camera connection")

clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect((ip, port))
print("connect success")


def auto_run():
    try:
        print("start sound_")
        # os.system('omxplayer /home/pi/Desktop/sound/start.wav')
        cmd = "omxplayer /home/pi/Desktop/sound/start.wav"
        Popen(cmd,stdin=PIPE,shell=True)
    except:
        print("fail to paly sound!! heheheehe start")

    ICC = atc.Initial_condition_checker()
    ATD = atc.Advanced_thermal_data_control()

    bin_data1 = clientSock.recv(1536)
    count = int(len(bin_data1) / 2)
    initial_data = struct.unpack('<' + ('h' * count), bin_data1)
    np.asarray(initial_data)
    initial_data = np.reshape(initial_data, (24, 32))

    ATD.run_initialization(ICC.run(initial_data))
    time.sleep(1)
    bin_data1 = clientSock.recv(1536)
    count = int(len(bin_data1) / 2)
    initial_data = struct.unpack('<' + ('h' * count), bin_data1)
    np.asarray(initial_data)
    initial_data = np.reshape(initial_data, (24, 32))

    ATD.run_initialization(ICC.run(initial_data))
    ATD.run_reset_time()

    #######################################################
    #try:
    #    print("start sound")
    #    os.system('omxplayer /home/pi/Desktop/sound/start')
    #except:
    #    print("fail to paly sound!! heheheehe start sound")

    print("----------------start_microwave_over--------------")

    while True:
        bin_data = clientSock.recv(1536)
        count = int(len(bin_data) / 2)
        short_arr = struct.unpack('<' + ('h' * count), bin_data)
        np.asarray(short_arr)
        short_arr = np.reshape(short_arr, (24, 32))

        lets_stop = ATD.run(short_arr)


        if lets_stop == 1:
            try:
                cv2.destroyAllWindows()
                print("normal_stop")
                # os.system('omxplayer /home/pi/Desktop/sound/normal_stop.wav')
                cmd = "omxplayer /home/pi/Desktop/sound/normal_stop.wav"
                Popen(cmd,stdin=PIPE,shell=True)
            except:
                print("fail to paly sound!! heheheehe normal_stop")
            break
        if lets_stop == 3:
            try:
                cv2.destroyAllWindows()
                print("fire")
                # os.system('omxplayer /home/pi/Desktop/sound/fire.wav')
                cmd = "omxplayer /home/pi/Desktop/sound/fire.wav"
                Popen(cmd,stdin=PIPE,shell=True)
            except:
                print("fail to paly sound!! heheheehefire")
            break
        if lets_stop == 4:
            try:
                cv2.destroyAllWindows()
                print("food_is_out")
                # os.system('omxplayer /home/pi/Desktop/sound/food_is_out.wav')
                cmd = "omxplayer /home/pi/Desktop/sound/food_is_out.wav"
                Popen(cmd,stdin=PIPE,shell=True)
            except:
                print("fail to paly sound!! heheheehe food_is_out")
            break
        if lets_stop == 5:
            try:
                cv2.destroyAllWindows()
                print("no_food_detected")
                # os.system('omxplayer /home/pi/Desktop/sound/no_food_detected.wav')
                cmd = "omxplayer /home/pi/Desktop/sound/no_food_detected.wav"
                Popen(cmd,stdin=PIPE,shell=True)
            except:
                print("fail to paly sound!! heheheehe no_food_detected")
            break

        status = read_status()
        if status["on"] == 0:
            break

    print("turn_off_microwave(auto_mode)")


def manual_run(power, duration):

    try:
        print("start sound_")
        # os.system('omxplayer /home/pi/Desktop/sound/start.wav')
        cmd = "omxplayer /home/pi/Desktop/sound/start.wav"
        Popen(cmd,stdin=PIPE,shell=True)
    except:
        print("fail to paly sound!! heheheehe start")

    manual_controller = ManualController()
    manual_controller.reset_param(power, duration)
    print("reset_the_manual_controller")
    TD = Temp_process.Thermal_Data(255, duration)

    while True:
        bin_data = clientSock.recv(1536)
        count = int(len(bin_data) / 2)
        short_arr = struct.unpack('<' + ('h' * count), bin_data)
        np.asarray(short_arr)

        short_arr = np.reshape(short_arr, (24, 32))
        # img = np.zeros((24, 24, 3), np.uint8)
        Newdata = np.zeros((24, 24), np.int16)
        Newdata = TD.Thermal_data_cut(short_arr)
        print("datcut complete")
        # min_tem = TD.run1(Newdata)
        min_tem = TD.run3(Newdata)
        print("run3")
        # Temp_process.absolute_HSV_Control3_cut(Newdata, img,min_tem )
        TD.absolute_HSV_Control5(Newdata)  ## if you use 110 then use Newdata


        stop_wave = manual_controller.run()

        if stop_wave:
            try:
                cv2.destroyAllWindows()
                print("normal_stop")
                # os.system('omxplayer /home/pi/Desktop/sound/normal_stop.wav')
                cmd = "omxplayer /home/pi/Desktop/sound/normal_stop.wav"
                Popen(cmd,stdin=PIPE,shell=True)
            except:
                print("fail to paly sound!! heheheehe normal_stop")
            break

        status = read_status()
        if status["on"] == 0:
            break


while True:

    status = read_status()
    if status["on"] == 1:
        if status["mode"] == 1:   # automode
            auto_run()

        elif status["mode"] == 0: # manualmode
            manual_run(status["power"], status["duration"])

        write_status(0, 0, 0, 0, 0)
        try:
            cv2.destroyAllWindows()
        except:
            print("failto close_window")


    bin_data = clientSock.recv(1536)
    # count = int(len(bin_data) / 2)
    # _ = struct.unpack('<' + ('h' * count), bin_data)




