# -*- coding: utf-8 -*-
import numpy as np
import cv2
import statistics as s
import time
from datetime import datetime
import csv
import os
import RPi.GPIO as GPIO
import time #sleep함수를쓰기위해
from socket import *
import struct
import threading


### the last version of microwave control


#####################################################################################################################################
class Initial_condition_checker:
#this function return form [type_flag , number_of_realpart , max_temp , average_temp , min_temp, edge_temp ]
    def __init__(self):
        self.initial_condition = 0

        self.over_reffernce = 1
        self.room_condition = 2
        self.cool_condition = 3
        self.icy_condtion = 4
        self.hot_and_cold_condtion = 5

        self.edge_data = 0
        self.realpart_number = 0

        self.max_tem = 0
        self.average_tem = 0
        self.min_tem = 0
        print("intitial_Checker_setup")
    def edge_temp_claculator(self, data):
        edge_1 = (data[0][0] + data[0][1] + data[1][1] + data[1][0])/4
        edge_2 = (data[0][22] + data[0][23] + data[1][22] + data[1][23])/4
        edge_3 = (data[22][0] + data[22][1] + data[23][1] + data[23][0])/4
        edge_4 = (data[22][22] + data[22][23] + data[23][22] + data[23][23])/4
        edge= [ edge_1, edge_2, edge_3 , edge_4]
        max = max(edge)
        if edge_1 == edge_2 == edge_3 == edge_4:
            return edge_1
        elif edge_1 < max:
            return edge_1
        elif edge_2 < max:
            return edge_2
        elif edge_3 < max:
            return edge_3
        else:
            return  edge_4
    def Thermal_data_cut(self, data):

        Newdata = np.zeros((24, 24), np.int16)  ##need to check
        for py in range(0, 24):
            newpx = 0
            for px in range(4, 28):
                if py == 1 and px == 8:
                    Newdata[py][newpx] = data[py][px - 1]
                else:
                    Newdata[py][newpx] = data[py][px]
                newpx += 1
        return Newdata
    def data_Condtion_checker(self,data):
        max_T = np.amax(data)
        min_T = np.amin(data)
        if max_T > self.edge_data * 1.2 and min_T < self.edge_data * 0.8:
            self.initial_condition = self.hot_and_cold_condtion
        elif max_T > self.edge_data * 1.2:
            self.initial_condition = self.over_reffernce
        elif min_T < 700:
            self.initial_condition = self.icy_condtion
        elif min_T < self.edge_data * 0.7:
            self.initial_condition = self.cool_condition
        else:
            self.initial_condition = self.room_condition
    def realpart_finder(self,data):
        number_of_realpart = 0
        real_object_temp = []
        for py in range(data.shape[0]):
            for px in range(data.shape[1]):
                if self.initial_condition == self.over_reffernce and data[py][px] > self.edge_data:
                    number_of_realpart += 1
                    real_object_temp.append(data[py][px])
                elif self.initial_condition == self.icy_condtion and data[py][px] < 1000:
                    number_of_realpart += 1
                    real_object_temp.append(data[py][px])
                elif self.initial_condition == self.cool_condition and data[py][px] < self.edge_data * 0.7:
                    number_of_realpart += 1
                    real_object_temp.append(data[py][px])
                elif self.initial_condition == self.hot_and_cold_condtion:

                    if data[py][px] > self.edge_data*1.2:
                        number_of_realpart +=1
                        real_object_temp.append(data[py][px])
                    elif data[py][px] < self.edge_data * 0.8 :
                        number_of_realpart += 1
                        real_object_temp.append(data[py][px])
        self.max_tem = max(real_object_temp)
        self.average_tem = s.mean(real_object_temp)
        self.min_tem = min(real_object_temp)
        return number_of_realpart

    def run(self,data):
        newdata = self.Thermal_data_cut(data)
        self.edge_data = self.edge_temp_claculator(newdata)
        self.data_Condtion_checker(newdata)
        self.realpart_number = self.realpart_finder(newdata)
        print("(Initial_condition_checker) check is completed ")

        return [self.initial_condition, self.realpart_number, self.max_tem , self,average_tem , self.min_tem , self.edge_data]
#####################################################################################################################################
class Microwave_contol:
    def __init__(self):

        self.magnetron_pin = 18
        self.fan_pin = 23
        self.max_power = 10
        self.control_time = 20  # 10 -> 한 루프가 1/10초 100 -> 1/100
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.magnetron_pin, GPIO.OUT)
        GPIO.setup(self.fan_pin, GPIO.OUT)
        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)

        print("Microwave_contol setup")
    def run_trun_off(self):
        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)
    def run_only_fan(self):
        try:
            GPIO.output(self.fan_pin, False)
            GPIO.output(self.magnetron_pin, True)
            return True
        except:
            print("(Microwave_contol)fail to trun on fan only!")
            return False
    def run_only_magnetron(self):
        try:
            GPIO.output(self.fan_pin, True)
            GPIO.output(self.magnetron_pin, False)
            return True
        except:
            print("(Microwave_contol)fail to trun on magnetron only!")
            return False
    def run_all(self):
        try:
            GPIO.output(self.fan_pin, False)
            GPIO.output(self.magnetron_pin, False)
            return True
        except:
            print("(Microwave_contol)fail to run_all!")
            return False

    def run(self,flag):
        if flag == 1:
            self.run_all()
        elif flag == 2:
            self.run_only_fan()
        elif flag == 3:
            self.run_only_magnetron()
        elif flag == 4:
            self.run_trun_off()
#####################################################################################################################################
class Advenced_thermal_data_control:

    def __init__(self):
        #represent_current_condition
        self.condition_flag = 0
        self.condition_initial_flag = 0
        self.condition_hot = 1
        self.condition_room = 2
        self.condition_cool = 3
        self.condition_icy = 4
        self.condition_hot_and_cold = 5
        self.condition_steam = 6

        self.DATA_initial_data = []   # [type_flag , number_of_realpart , max_temp , average_temp , min_temp, edge_temp ]
        self.DATA_all = []    # DATA_all[0][0]    ==> ex) [[time, number_of_part, max_temp , average_temp , min_temp , edge_temp ],[time, number_of_part, max_temp , average_temp , min_temp , edge_temp]]
        self.DATA_all_index = 0
        self.DATA_operation = []  # this one will stored whan magnetron is operation.
        self.DATA_operation_index = 0

        self.operation_flag = 0
        self.operation_all = 1
        self.operation_fan_only = 2
        self.operation_magnetron_only = 3
        self.operation_turn_off = 4
        self.operation_power = 10 #0~10 will be used 0 is equal to fan_only

        self.status_edge_up = [ False , 0 , 0 , 0 , 0 , 0 , 0 , False ]  #[edge_up flag , edge_up_time , number_of_part ,max_temp , average_temp ,  min_temp , edge_temp , vinyl_flag]
        self.status_operation_interval = 10
        self.status_operation_flag = True
        self.status_min_rise = 0
        self.status_target_max = 800
        self.status_targer_next_max_or_avg = 400
        self.status_target_min = 500

        self.time_initial_time = 0   #when micro wave open start set it again
        self.time_remain_operation_time = 0

        self.MWC = Microwave_contol()   ## use "self.MWC(self.operation_flag)"

        print("Advenced_thermal_data_control setup")
    def __del__(self):
        try:
            cv2.destroyAllWindows()
        except:
            print("faile to close data")
    def checker_vinyl_flag(self):
        if self.DATA_all[self.DATA_all_index-1][4] /self.DATA_all[self.DATA_all_index-1][2] < 0.4:
            if self.DATA_all[self.DATA_all_index][1] > self.DATA_initial_data[1] * 1.05:
                return True
        return False
    def checker_edge_up(self):
        if ((self.condition_initial_flag == self.condition_cool) or (self.condition_initial_flag == self.condition_icy) or (self.condition_initial_flag == self.self.condition_hot_and_cold)) and self.status_edge_up[0] == False:
            if (self.condition_flag == 1) or (self.condition_flag == 2):
                self.status_edge_up[0] = True
                for i in range (1,7):
                    self.status_edge_up[i] = self.DATA_all[self.DATA_all_index][i-1]
                self.status_edge_up[7] = self.checker_vinyl_flag()
    def checker_min_rise(self):
        min_rise_pre = (self.DATA_operation[self.DATA_operation_index - 1][4] - self.DATA_operation[self.DATA_operation_index - 9][4]) / (self.DATA_operation[self.DATA_operation_index - 1][0] - self.DATA_operation[self.DATA_operation_index - 9][0])
        min_rise = (self.DATA_operation[self.DATA_operation_index ][4] - self.DATA_operation[self.DATA_operation_index - 8][4]) / (self.DATA_operation[self.DATA_operation_index][0] - self.DATA_operation[self.DATA_operation_index - 8][0])
        temp = (min_rise_pre + min_rise) / 2
        if temp < 1.3:
            temp = 1.3
        return temp
    def checker_remain_time(self):
        time_calculate = (self.status_target_min - self.DATA_all[self.DATA_all_index ][4]) / (self.checker_min_rise() * 0.1)
        if self.time_remain_operation_time > 0 :
            self.time_remain_operation_time = (self.time_remain_operation_time + time_calculate) /2
        elif self.time_remain_operation_time == 0:
            self.time_remain_operation_time = time_calculate
        print("remain_time:",self.time_remain_operation_time * 1.4)

    def run_initialization(self,icc_data):
        self.DATA_initial_data.extend(icc_data)
#####################################################################################################################################
