# -*- coding: utf-8 -*-
#for real_control

# 총 타입 3개
#
#class autorun():
#
# Type_Flag = 0 ~ 4?
#
# 0: 최초 작동 시작 (full 가동)
# 1: 첫번째 작동 중지후 식히기 시작( 팬만 돌아가는 상태).
# 2: 두번째 작동 시작 (full 가동)
# 3: 두번째 작동 중지후 식히기 시작 (팬만 돌아가는 상태)
# 4: 세번쨰 작동 시작 (full 가동)
# 5: 세번쨰 작동 중지 후 식히기 시작 (팬만 돌아가는 상태)
#
#
# 10: 완전 종료 조건. =>필요한지 의문.
#
# type 함수 return타입
# ture == > 프로그램 계속작동
# flase ==> 프로그램 종료 (전자레인지 종료)
#
#
#
# //작동 방식은 루프 (1) 초당 한번씩 max,min,average읽고 명령을 던져주는것 (마이크로 웨이브에)
# type A // 3번 나누어서 작동하는 것
#
# internal_max1
# internal_min1
#
# internal_max2
# internal_min2
#
# internal_max3
# internal_min3
#
# 논리 순서 > 한루프당 하나에만 도달 해야함.
# if 최종 종료 조건 도달
#   self.run_turn_off()
#   self.Type_Flag = 10
#   reutrn flase
#
# elif flag == 0 and 최초 스탑 조건
#   self.run_only_fan()
#   self.Typer_Flag = 1
#   return True
#
# elif flag == 1 and 두번쨰 작동 시작 조건
#
#   self.run_all()
#   self.Type_Flag = 2
#   retun True
# elif flag == 2 and 두번쨰 스탑 조건
#   self,run_only_fan()
#   self.flag = 3
#   return True
#
# elif flag == 3 and 마지막 작동 시작 조건
#   self.run_all()
#   self.flag = 4
#   return Ture
# elif falg == 4 and 마지막 뜸들이기 시작 조건
#   self.run_only_fan
#   self.flag  = 5
#   return True
#
#
#
#
#
#
# type B  // 2번 나누어서 작동하는 것
#
#
#
# type C   // 한번만 작동하는것

###############################################논리 전개 방식



import auto_contorol as auto_control
import Temp_process_developer as Temp_process
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
        auto_control.reset()
        print("wait for camera connection")
        clientSock = socket(AF_INET, SOCK_STREAM)
        clientSock.connect((ip, port))
        print("connect success")

        IC8888 = Temp_process.Initial_condition_checker()

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
        OPENTHEDOOR = IC8888.run(inditial_data)
        print("number_of_realpart:",OPENTHEDOOR[1],"edge_temp:",OPENTHEDOOR[2])


        auto_controler.reset_origin()
        print("auto_controler_reset")
        TD = Temp_process.Thermal_Data(OPENTHEDOOR[2])
        print("thermal_data_set_up")

        TD.run6_get_intitial_temp(IC8888.origin_temp)
        start_time = TD.initial_time

        #######################################################
        auto_controler.run_all()
        print("----------------start_microwave_over--------------")

        lets_stop = 0

        while True:
            bin_data = clientSock.recv(1536)
            count = int(len(bin_data) / 2)
            short_arr = struct.unpack('<' + ('h' * count), bin_data)
            np.asarray(short_arr)

            realzon_flag = 0

            try:  #get data_ form camera
                short_arr = np.reshape(short_arr, (24, 32))
                Newdata = TD.Thermal_data_cut(short_arr)
                run_output = TD.autorun1(Newdata)
                print("run6")
                TD.absolute_HSV_Control5(Newdata)

            except:
                print("Worning! some error occure in thermal_Data_control")

            try:  #run_microwave_oven_automatically
                auto_controler.type_checker(TD.seven_sec_change)
                auto_controler.get_temperature_data_form_TD(TD.max_temp,TD.average_temp,TD.min_temp)
                lets_stop = auto_controler.run(start_time)

            except:
                print("Fail_in_manual_controller")


            if lets_stop:
                try:
                    cv2.destroyAllWindows() #delete class
                    print("turn_off_micro_wave")
                    del TD

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
