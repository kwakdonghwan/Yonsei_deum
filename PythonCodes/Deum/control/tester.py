# -*- coding: utf-8 -*-

import auto_contorol as auto_control
import Temp_process_developer as Temp_process
import advanced_thermal_control as atc
import RPi.GPIO as GPIO
import time #sleep함수를쓰기위해
from socket import *
import numpy as np
import struct
import cv2
import threading
import os
################################################################################### intitial_parameter
run_type = 0
auto_run_type = 1
manual_run_type = 2
test_run_type = 3

ip = '127.0.0.1'
port = 8888

################################################################################### first_text
print("Welcome to tester")
print("open new terminal key : Ctrl + Shift + T")
print("camera operation using terminal")
print("sudo /home/pi/Yonsei_deum/camera_MLX90640/MLX90640 0.0625 8888")
print("or in camera_path")
print("sudo ./MLX90640 0.0625 8888")
################################################################################### intitial_contition
manual_controller = auto_control.ManualController()
auto_controler = auto_control.auto_contoroler()
print("micro wave controllers setup")
###################################################################################
def auto_run():
    os.system("clear")
    print("auto run start")
    while True:

        print("wait for camera connection")
        clientSock = socket(AF_INET, SOCK_STREAM)
        clientSock.connect((ip, port))
        print("connect success")

        ICC = atc.Initial_condition_checker()
        ATD = atc.Advanced_thermal_data_control()

        #delete trash data
        bin_data0 = clientSock.recv(1536)
        count = int(len(bin_data0) / 2)
        trash_Data = struct.unpack('<' + ('h' * count), bin_data0)
        #check_intitial_contition

        bin_data1 = clientSock.recv(1536)
        count = int(len(bin_data1) / 2)
        inditial_data = struct.unpack('<' + ('h' * count), bin_data1)
        np.asarray(inditial_data)
        inditial_data = np.reshape(inditial_data, (24, 32))

        ATD.run_initialization( ICC.run(inditial_data))
        time.sleep(2)
        bin_data1 = clientSock.recv(1536)
        count = int(len(bin_data1) / 2)
        inditial_data = struct.unpack('<' + ('h' * count), bin_data1)
        np.asarray(inditial_data)
        inditial_data = np.reshape(inditial_data, (24, 32))

        ATD.run_initialization( ICC.run(inditial_data))
        ATD.run_reset_time()

        #######################################################

        print("----------------start_microwave_over--------------")

        lets_stop = False

        while True:
            bin_data = clientSock.recv(1536)
            count = int(len(bin_data) / 2)
            short_arr = struct.unpack('<' + ('h' * count), bin_data)
            np.asarray(short_arr)


            try:  #get data_ form camera
                lets_stop = ATD.run(short_arr)

            except:
                print("Worning! some error occure in thermal_Data_control")

            if lets_stop == True:
                try:
                    del ATD

                except:
                    print("some error occured during to finish microwave")
                break

        print("turn_off_microwave(auto_mode)")

        break


###################################################################################
def manual_run():
    os.system("clear")
    print("manual run start")

###################################################################################
def test_run():
    os.system("clear")
    print("test run start")
    print("experiment data will saved as csv format")

    while True:

        os.system("clear")

        print("input_your_time(min is 1s) and power(max is 10)")
        print("only 'int' type will be accepted")
        duration = int(input("enter time (s) ex) '15' : "))
        power = int(input("enter power(10-{}): ex) '10' : "))

        print("wait for camera connection")

        clientSock = socket(AF_INET, SOCK_STREAM)
        #print("connect start")
        clientSock.connect((ip, port))
        print("connect success")
        # temperature_controller = maxheat.TemperatureController(70)

        IC8888 = Temp_process.Initial_condition_checker()

        #initial contion checker

        bin_data0 = clientSock.recv(1536)
        count = int(len(bin_data0) / 2)
        trash_Data = struct.unpack('<' + ('h' * count), bin_data0)

        bin_data1 = clientSock.recv(1536)
        count = int(len(bin_data1) / 2)
        inditial_data = struct.unpack('<' + ('h' * count), bin_data1)
        np.asarray(inditial_data)
        inditial_data = np.reshape(inditial_data, (24, 32))

        OPENTHEDOOR = IC8888.run(inditial_data)
        print("number_of_realpart:",OPENTHEDOOR[1],"edge_temp:",OPENTHEDOOR[2])

        manual_controller.reset_origin()
        print("reset_the_manual_controller")
        TD = Temp_process.Thermal_Data(OPENTHEDOOR[2])
        print("thermal_data_set_up")
        
        #print("run6_initial_temp",IC8888.origin_temp)
        TD.run6_get_intitial_temp(IC8888.origin_temp)
        start_time = TD.initial_time

        #######################################################
        manual_controller.reset_param(power, duration)
        print("----------------start_microwave_over--------------")

        lets_stop = 0

        while True:
            bin_data = clientSock.recv(1536)
            count = int(len(bin_data) / 2)
            short_arr = struct.unpack('<' + ('h' * count), bin_data)
            np.asarray(short_arr)

            realzon_flag = 0

            try:
                short_arr = np.reshape(short_arr, (24, 32))

                Newdata = TD.Thermal_data_cut(short_arr)

                run_output = TD.run6(Newdata)
                print("run6")
                TD.absolute_HSV_Control5(Newdata)

            except:
                print("Worning! some error occure in thermal_Data_control")

            try:
                lets_stop = manual_controller.run(start_time)

            except:
                print("Fail_in_manual_controller")


            if lets_stop:
                try:
                    cv2.destroyAllWindows() #delete class
                    infomation = []
                    print("turn_off_micro_wave")
                    str1 = input("enter_the_object_name(in english): ")

                    infomation.append("Object Name:")
                    infomation.append(str1)
                    infomation.append("input time:")
                    infomation.append(duration)
                    infomation.append("input power:")
                    infomation.append(power)

                    TD.csv_wirter(infomation)
                    del TD

                except:
                    print("some error occured during to finish microwave")
                break

        print("try to reset microwave")
        print("if you want to close program enter the (N) ")

        trash = input("did you want run more(test_mode)? : (Y/N)")

        if trash == 'N' or trash == 'n':
            os.system("clear")
            print("turn off test_mode")
            break

################################################################################### main_loop
while True:
    print("please input you operation type")
    data_input = int(input("1:auto_run 2:manual_run 3:test_run(for experiment) 4:tun_off :"))
    if data_input == 1:
        run_type = auto_run_type
        auto_run()
    elif data_input == 2:
        run_type = manual_run_type
        manual_run()
    elif data_input == 3:
        run_type = test_run_type
        test_run()
    elif data_input == 4 :
        os.system("clear")
        print("tun_off")
        print("Good bye!")
        break
    else:
        os.system("clear")
        print("incorrect input! please try again")
        continue
###################################################################################
