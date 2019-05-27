# -*- coding: utf-8 -*-
# 2019_05_27_ version
import numpy as np
import cv2
import statistics as s
import time
from datetime import datetime
import csv
import os, sys
import RPi.GPIO as GPIO
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
        max1 = max(edge)
        if edge_1 == edge_2 == edge_3 == edge_4:
            return edge_1
        elif edge_1 < max1:
            return edge_1
        elif edge_2 < max1:
            return edge_2
        elif edge_3 < max1:
            return edge_3
        else:
            return  edge_4
    def Thermal_data_cut(self, data):

        Newdata = np.zeros((24, 24), np.int16)  ##need to check
        for py in range(0, 24):
            newpx = 0
            for px in range(4, 28):
                if (py == 1 and px == 8) or (data[py][px] == 0):
                    Newdata[py][newpx] = data[py][px - 1]
                else:
                    Newdata[py][newpx] = data[py][px]

                newpx += 1
        return Newdata
    def data_Condtion_checker(self,data):
        max_T = np.amax(data)
        min_T = np.amin(data)
        print("max_T", max_T , "min_T", min_T)
        if max_T > self.edge_data * 1.2 and min_T < self.edge_data * 0.8:
            self.initial_condition = self.hot_and_cold_condtion
        elif max_T > self.edge_data * 1.2:
            self.initial_condition = self.over_reffernce
        elif min_T < 70:
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
                print(data[py][px])
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
                elif (self.initial_condition == self.room_condition)  and data[py][px] > self.edge_data:
                    number_of_realpart += 1
                    real_object_temp.append(data[py][px])
        try:
            self.max_tem = max(real_object_temp)
            self.average_tem = s.mean(real_object_temp)
            self.min_tem = min(real_object_temp)
        except:
            print("no_realpart")
        return number_of_realpart
# run initial condition checker
    def run(self,data):
        new_data = self.Thermal_data_cut(data)
        self.edge_data = self.edge_temp_claculator(new_data)
        self.data_Condtion_checker(new_data)
        self.realpart_number = self.realpart_finder(new_data)
        print("(Initial_condition_checker) check is completed ")
        print([self.initial_condition, self.realpart_number, self.max_tem , self.average_tem , self.min_tem , self.edge_data])
        return [self.initial_condition, self.realpart_number, self.max_tem , self.average_tem , self.min_tem , self.edge_data]
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
# just turn on or turn off microwaveoven
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
class Advanced_thermal_data_control:
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
        self.condition_fire = 7
        self.condition_fire_count = 0

        self.DATA_initial_data = []   # [type_flag , number_of_real_part , max_temp , average_temp , min_temp, edge_temp ]
        self.DATA_all = []    # DATA_all[0][0]    ==> ex) [[time, number_of_part, max_temp , average_temp , min_temp , edge_temp , status_flag ,std_data ],[time, number_of_part, max_temp , average_temp , min_temp , edge_temp , status_flag ,std_data]]
        self.DATA_all_index = -1
        self.DATA_operation = []  # this one will stored when magnetron is operation.
        self.DATA_operation_index = -1

        self.DATA_operation_flag = True
        self.operation_flag = 0
        self.operation_all = 1
        self.operation_fan_only = 2
        self.operation_magnetron_only = 3
        self.operation_turn_off = 4
        self.operation_power = 10 #0~10 will be used 0 is equal to fan_only

        self.status_edge_temp = 0
        self.status_reference_temp = [0 ,0 ]
        self.status_edge_up = [ False , 0 , 0 , 0 , 0 , 0 , 0 , False ]  #[edge_up flag , edge_up_time , number_of_part ,max_temp , average_temp ,  min_temp , edge_temp , vinyl_flag]
        self.status_operation_interval = 10
        self.status_min_rise = 0
        self.status_10sec_flag = 0
        self.status_10sec_flag_pre = 0
        self.status_forced_stop_flag = False

        self.status_target_max = 800
        self.status_target_max_flag = 0
        self.status_target_next_max_or_avg = 500        # initial flag = icy > 1,3,5,7,11 / cool > 3,5,7,11 / hot_and_cold > 7,9,11 /  room > 7,9,11 /
        self.status_target_next_max_or_avg_flag = 0    # 0 and even # > operation , 1 > enter icy to cool  3>  enter room_temp zone , 5 > enter hot and cool zone 7 > enter hot zone 9 > enter first target_max 11> enter second target_max 13> before turn off(20~30sec_rest)  14>turn_off
        self.status_target_min = 500
        self.status_target_min_flag = 0
        self.status_target_min_can_not_reach_flag = False
        self.status_target_exist_max_temp = 0
        self.status_target_exist_max_temp_flag = False


        self.time_initial_time = 0   #when micro wave open start set it again
        self.time_remain_operation_time = 20
        self.time_break_time_counter = -1
        self.time_break_time_default = 5
        self.time_reach_below_10 = False  ## make flag to 11 and return True
        self.time_display_time_trash = 0

        self.MWC = Microwave_contol()   ## use "self.MWC(self.operation_flag)"

        now = datetime.now()
        time_name = now.strftime("%Y_%m_%d %H_%M_%S")
        save_path = "/home/pi/CSV_data"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        CSV_path = save_path + "/" + time_name + ".csv"
        self.f = open(CSV_path, 'w+', encoding='utf-8', newline='')
        self.wr = csv.writer(self.f)
        basic_info = (['time', 'Number_of_real_part', 'max_temp', 'average_temp', 'min_temp', 'edge_temp', 'status_flag', 'std_data'])

        self.wr.writerow(basic_info)

        ####################### auto mode sound out ##############



        print("Advanced_thermal_data_control setup")
    def __del__(self):
        self.f.close()
        try:
            cv2.destroyAllWindows()
        except:
            print("faile to close data")
        try:
            self.wr.writerows(self.DATA_all)
        except:
            print("fail_to_store_in_CSV")

    def mouse_call_back(self,event,x,y,flags,parm):
        print("stop button pressed")

        if event == cv2.EVENT_LBUTTONUP:
            if self.status_forced_stop_flag == False:
                if 385 < x < 580:
                    if 320 < y < 350:
                        print("forced stop mode on")
                        self.status_target_next_max_or_avg_flag = 14
                        self.operation_flag = self.operation_turn_off
                        self.status_forced_stop_flag = True


    def display_time_control(self,input_time_data):
        self.time_display_time_trash = self.time_display_time_trash+1
        display_time = input_time_data
        if input_time_data > 100:
            display_time = int (input_time_data / 10)

            display_time = display_time - (self.time_display_time_trash % 10)
            if display_time < 1 :
                display_time = 1
            return display_time

        if self.status_target_next_max_or_avg_flag == 13:
            
            display_time = 2 + 2 * self.time_break_time_default - self.time_break_time_counter

        display_time = display_time - (self.time_display_time_trash % 10)
        if display_time < 1:
            display_time = 1
        return display_time
# img show
    def absolute_HSV_Control5(self,data4):
        img = np.zeros((24, 40, 3), np.uint8)
        thickness = 1
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        font = cv2.FONT_HERSHEY_DUPLEX
        fontScale = 0.7
        for py in range(data4.shape[0]):
            for px in range(data4.shape[1]):
                value_1 = 255
                value_2 = 255
                value_3 = 255
                if 3000 >= data4[py][px] > 1200:  # 2000 = 200C  max = 300
                    value_1 = 1
                    value_2 = 255 - ((data4[py][px] - 1200) * 254 / 1000)  ## 0 = white
                elif data4[py][px] > 1000:
                    value_1 = 5 - ((data4[py][px] - 1000) * 4 / 200)
                elif data4[py][px] > 700:
                    value_1 = 15 - ((data4[py][px] - 700) * 10 / 300)
                elif data4[py][px] > 600:
                    value_1 = 30 - ((data4[py][px] - 600) * 15 / 100)
                elif data4[py][px] > 500:
                    value_1 = 45 - ((data4[py][px] - 500) * 15 / 100)
                elif data4[py][px] > 400:
                    value_1 = 60 - ((data4[py][px] - 400) * 15 / 100)
                elif data4[py][px] > 300:
                    value_1 = 75 - ((data4[py][px] - 300) * 15 / 100)
                elif data4[py][px] > 200:
                    value_1 = 90 - ((data4[py][px] - 200) * 15 / 100)
                elif data4[py][px] > 150:
                    value_1 = 105 - ((data4[py][px] - 150) * 15 / 50)
                elif data4[py][px] > -100:
                    value_1 = 115 - ((data4[py][px] + 100) * 10 / 250)
                elif data4[py][px] >= -300:
                    value_1 = 120
                    value_3 = ((data4[py][px] + 300) * 254 / 200)  ## 0 = black

                img[py][px][0] = 125 - int(value_1)  # 0~120
                img[py][px][1] = int(value_2)
                img[py][px][2] = int(value_3)

        img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
        img = cv2.resize(img, None, fx=15, fy=15, interpolation=cv2.INTER_CUBIC)
        display_time_value = int(self.display_time_control(self.time_remain_operation_time))
        ################# display _data ##############################
        display_max_temp = "max:" + str(self.DATA_all[self.DATA_all_index][2]/10) + "'C"
        display_mid_temp = "mid:" + str(self.DATA_all[self.DATA_all_index][3] / 10) + "'C"
        display_min_temp = "min:" + str(self.DATA_all[self.DATA_all_index][4] / 10) + "'C"
        display_edge_temp = "air:" + str(self.DATA_all[self.DATA_all_index][5]/10 - 3) + "'C"
        display_time_remain_operation_time = str(display_time_value) + "s"
        display_condition_flag = "phase:" + str(self.status_target_next_max_or_avg_flag)
        display_prograss =  "prgrass:" + str(int(self.status_target_next_max_or_avg_flag / 14 * 100)) + "%"
        display_logo = "DEUM_yonsei"

        cv2.putText(img, display_max_temp, (385,30), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        #cv2.putText(img, display_mid_temp, (385, 70), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_min_temp, (385, 70), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        if (self.status_edge_up[0] == True):
            cv2.putText(img, display_edge_temp, (385, 110), font, fontScale, (0, 0, 255), thickness, cv2.LINE_AA)
        else:
            cv2.putText(img, display_edge_temp, (385, 110), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_time_remain_operation_time, (385, 160), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_condition_flag, (385, 200), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_prograss, (385, 240), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_logo, (385, 280), font, fontScale * 1.2, (255, 255, 255), thickness, cv2.LINE_AA)


        #############################stop button#################################
        cv2.rectangle(img,(385,320),(580,350),(150,150,150),-1)
        cv2.putText(img, "STOP", (450, 343), font, fontScale *1.1 , (0, 0, 255), thickness+1, cv2.LINE_AA)




        #########################################################################



        cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("frame", self.mouse_call_back)  # stop button click event

        cv2.imshow('frame', img)
        #try:
        #    cv2.moveWindow('frame' , 2, 2)
        #except:
        #    print("fail_to move window")
        cv2.waitKey(1)
        return img
# data analysis and store in this class
    def PostProcess_edge_temp_calculator(self, data):
        edge_1 = (data[0][0] + data[0][1] + data[1][1] + data[1][0])/4
        edge_2 = (data[0][22] + data[0][23] + data[1][22] + data[1][23])/4
        edge_3 = (data[22][0] + data[22][1] + data[23][1] + data[23][0])/4
        edge_4 = (data[22][22] + data[22][23] + data[23][22] + data[23][23])/4
        edge= [ edge_1, edge_2, edge_3 , edge_4]
        max1 = max(edge)
        if edge_1 == edge_2 == edge_3 == edge_4:
            return edge_1
        elif edge_1 < max1:
            return edge_1
        elif edge_2 < max1:
            return edge_2
        elif edge_3 < max1:
            return edge_3
        else:
            return  edge_4
    def PostProcess_Thermal_data_cut(self, data):
        new_data = np.zeros((24, 24), np.int16)
        for py in range(0, 24):
            newpx = 0
            for px in range(4, 28):
                if (py == 1 and px == 8) or (data[py][px] == 0):
                    new_data[py][newpx] = data[py][px - 1]
                else:
                    new_data[py][newpx] = data[py][px]
                newpx += 1
        return new_data
    def PostProcess_data_Condtion_checker(self,data):
        max_T = np.amax(data)
        min_T = np.amin(data)
        reference_temp2 = self.status_edge_temp
        if max_T > self.status_edge_temp * 1.2 and min_T < self.status_edge_temp * 0.8:
            self.condition_flag = self.condition_hot_and_cold
            reference_temp1 = (3*self.status_edge_temp + max_T) / 4
            reference_temp2 = (self.status_edge_temp+ 3*min_T ) / 4
        elif max_T > self.status_edge_temp * 1.2:
            self.condition_flag = self.condition_hot
            reference_temp1 = (3*self.status_edge_temp + max_T) / 4
        elif min_T < 70:
            self.condition_flag = self.condition_icy
            reference_temp1 = (2*self.status_edge_temp + min_T) / 3
        elif min_T < self.status_edge_temp * 0.7:
            self.condition_flag = self.condition_cool
            reference_temp1 = (self.status_edge_temp + 4 * min_T) / 5
        else:
            self.condition_flag = self.condition_room
            reference_temp1 = (3 * self.status_edge_temp + max_T) / 4

        if self.status_edge_temp > 650:
            self.condition_flag = self.condition_steam
            reference_temp1 = (2*self.status_edge_temp + max_T) / 3

        if max_T > 1400:
            self.condition_flag  = self.condition_fire
            if self.condition_fire_count > 2:
                self.operation_flag = self.operation_turn_off
                self.status_target_next_max_or_avg_flag = 14
            self.condition_fire_count += 1
            print("Caution!!!! fire detected!!!!!")
        else:
            self.condition_fire_count = 0
        self.status_reference_temp = [reference_temp1,reference_temp2]
    def PostProcess_get_data(self,data):
        Number_of_real_temp = 0
        all_object_temp = []
        real_object_temp = []
        for py in range(data.shape[0]):
            for px in range(data.shape[1]):
                all_object_temp.append(data[py][px])
                if self.condition_flag == self.condition_room and data[py][px] > self.status_reference_temp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition_flag == self.condition_cool and data[py][px] < self.status_reference_temp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition_flag == self.condition_icy and data[py][px] < self.status_reference_temp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition_flag == self.condition_hot and data[py][px] > self.status_reference_temp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition_flag == self.condition_steam and data[py][px] > self.status_reference_temp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition_flag == self.condition_hot_and_cold:
                    if data[py][px] > self.status_reference_temp[0]:
                        Number_of_real_temp += 1
                        real_object_temp.append(data[py][px])
                    elif data[py][px] < self.status_reference_temp[1]:
                        Number_of_real_temp += 1
                        real_object_temp.append(data[py][px])

        real_object_temp = sorted(real_object_temp)
        try: #this function will reduce the risk of flutuation
            min_temp = int((real_object_temp[0] + real_object_temp[1] + real_object_temp[2]) / 3)
            real_object_temp.reverse()
            max_temp = int((real_object_temp[0] + real_object_temp[1] + real_object_temp[2]) / 3)
        except:
            real_object_temp.reverse()
            max_temp = max(real_object_temp)
            min_temp = min(real_object_temp)

        times = time.time() - self.time_initial_time
        average_temp = s.mean(real_object_temp)
        self.DATA_all.append([times,Number_of_real_temp,max_temp,average_temp,min_temp,self.status_edge_temp,self.condition_flag,0])
        self.DATA_all_index += 1

        all_object_temp =  sorted(all_object_temp)

        if (self.DATA_all[self.DATA_all_index][6] == 4 or self.DATA_all[self.DATA_all_index][6] == 3):
            all_object_temp = all_object_temp[self.DATA_initial_data[1]:]
        elif self.DATA_all[self.DATA_all_index][6] == 5 :
            temp_number_data=int(self.DATA_initial_data[1] / 2)
            all_object_temp_1 = all_object_temp[temp_number_data:]
            all_object_temp_2 = all_object_temp[:temp_number_data]
            all_object_temp_1.extend(all_object_temp_2)
            all_object_temp = all_object_temp_1
        else:
            all_object_temp = all_object_temp[:self.DATA_initial_data[1]]
        self.DATA_all[self.DATA_all_index][7]=np.std(all_object_temp)
        if self.DATA_operation_flag == True:
            self.DATA_operation.append([times,Number_of_real_temp,max_temp,average_temp,min_temp,self.status_edge_temp,self.condition_flag ,self.DATA_all[self.DATA_all_index][7]])
            self.DATA_operation_index += 1
    def PostProcess(self,data):
        #print("post_process_start")
        new_data = self.PostProcess_Thermal_data_cut(data)
        self.status_edge_temp = self.PostProcess_edge_temp_calculator(new_data)
        self.PostProcess_data_Condtion_checker(new_data)
        self.PostProcess_get_data(new_data)
        self.absolute_HSV_Control5(new_data)
# check operation condition form data functions
    def checker_edge_up_vinyl_flag(self):
        if self.DATA_all[self.DATA_all_index-1][4] /self.DATA_all[self.DATA_all_index-1][2] < 0.4:
            if self.DATA_all[self.DATA_all_index][1] > self.DATA_initial_data[1] * 1.05:
                return True
        return False
    def checker_edge_up(self):
        if self.DATA_initial_data[0] != self.condition_hot and self.status_edge_up[0] == False:
            if self.condition_flag == self.condition_hot:
                self.status_edge_up[0] = True
                for i in range (1,7):
                    self.status_edge_up[i] = self.DATA_all[self.DATA_all_index][i-1]
                self.status_edge_up[7] = self.checker_edge_up_vinyl_flag()
    def checker_min_rise(self):
        min_rise_pre = (self.DATA_operation[self.DATA_operation_index - 1][4] - self.DATA_operation[self.DATA_operation_index - 9][4]) / 8
        min_rise = (self.DATA_operation[self.DATA_operation_index ][4] - self.DATA_operation[self.DATA_operation_index - 8][4]) / 8
        temp = (min_rise_pre + min_rise) / 2
        if temp < 1.3:
            temp = 1.3
        return temp
    def checker_make_target_max_min(self): # self.DATA_all_index % 10 == 0 and self.Data_all_index > 1 >> operation condition
        min_rise = self.checker_min_rise()
        if self.status_target_max_flag == 0:
            if min_rise > 6.0 :
                target_max = 880 + self.DATA_initial_data[1]
            elif min_rise  > 3.5 :
                if (self.DATA_initial_data[1] < 70):
                    s = 70
                else:
                    s = self.DATA_initial_data[1]
                target_max = 750 + s
            else:
                target_max = 750
            self.status_target_max_flag = 1
            self.status_target_max = target_max
            print("target_max_set:", target_max ,"min_rise:",min_rise )
        if self.status_target_min_flag == 0:
            if (self.DATA_initial_data[0] == self.condition_icy) or (self.DATA_initial_data[0] == self.condition_cool) or (self.DATA_initial_data[0] == self.condition_hot_and_cold) :
                target_min = 505
            else:
                target_min = 600
            self.status_target_min_flag = 1
            self.status_target_min = target_min
            print("target_min_set:",target_min)
    def checker_remain_time(self):
        if self.condition_flag == self.condition_steam:
            return
        time_calculate = (self.status_target_min - self.DATA_all[self.DATA_all_index ][4]) / (self.checker_min_rise() * 0.1)
        if self.time_remain_operation_time > 0 :
            self.time_remain_operation_time = (self.time_remain_operation_time + time_calculate) /2
        elif self.time_remain_operation_time == 0:
            self.time_remain_operation_time = time_calculate
        else:
            return
        print("remain_time:",self.time_remain_operation_time * 1.4)
    def checker_steam_condition(self):
        if self.condition_flag == self.condition_steam:
            self.time_remain_operation_time = 10
            self.status_target_next_max_or_avg_flag = 13
            print("steam_condition_detected, prepare to turn off")
    def checker_next_target(self):
        if self.status_edge_up[7] == True: # this is for vinyl detected
            self.status_target_next_max_or_avg = (self.DATA_all[self.DATA_all_index][3] + self.status_target_max)
        else:
            self.status_target_next_max_or_avg = (self.DATA_all[self.DATA_all_index][2] + self.status_target_max)
    def checker_food_exist(self):
        if self.DATA_all[self.DATA_all_index][2] > 550:
            if self.status_target_exist_max_temp < self.DATA_all[self.DATA_all_index][2]:
                self.status_target_exist_max_temp = self.DATA_all[self.DATA_all_index][2]
                self.status_target_exist_max_temp_flag = True
        if self.status_target_exist_max_temp_flag == True:
            if self.status_target_exist_max_temp * 0.7 >self.DATA_all[self.DATA_all_index][2]:
                self.operation_flag = self.operation_turn_off
                print("food_is_out")


# control condtion functions
    def checker_status_target_next_max_or_avg_flag_controller(self):
        if self.DATA_all_index < 9: # prevent error occur
            return
        if (self.time_remain_operation_time < 10) and (self.time_reach_below_10 ==False) :
            self.status_target_next_max_or_avg_flag = 13
            self.time_reach_below_10 = True
            return
        if self.status_target_next_max_or_avg_flag == 0:
            if self.DATA_all[self.DATA_all_index][6] == self.condition_cool and self.DATA_all[self.DATA_all_index-1][6] != self.condition_cool:
                self.status_target_next_max_or_avg_flag = 1
                self.DATA_operation_flag = False
                return
            elif self.DATA_all[self.DATA_all_index][6] == self.condition_room and self.DATA_all[self.DATA_all_index-1][6] != self.condition_room:
                self.status_target_next_max_or_avg_flag = 3
                self.DATA_operation_flag = False
                return
            elif self.DATA_all[self.DATA_all_index][6] == self.condition_hot_and_cold and self.DATA_all[self.DATA_all_index-1][6] != self.condition_hot_and_cold:
                self.status_target_next_max_or_avg_flag = 5
                self.DATA_operation_flag = False
                return
            elif self.DATA_all[self.DATA_all_index][6] == self.condition_hot and self.DATA_all[self.DATA_all_index-1][6] != self.condition_hot:
                self.status_target_next_max_or_avg_flag = 7
                self.DATA_operation_flag = False
                return

        elif self.status_target_next_max_or_avg_flag == 2:
            if self.DATA_all[self.DATA_all_index][6] == self.condition_room and self.DATA_all[self.DATA_all_index-1][6] != self.condition_room:
                self.status_target_next_max_or_avg_flag = 3
                self.DATA_operation_flag = False
                return
            elif self.DATA_all[self.DATA_all_index][6] == self.condition_hot_and_cold and self.DATA_all[self.DATA_all_index-1][6] != self.condition_hot_and_cold:
                self.status_target_next_max_or_avg_flag = 5
                self.DATA_operation_flag = False
                return
            elif self.DATA_all[self.DATA_all_index][6] == self.condition_hot and self.DATA_all[self.DATA_all_index-1][6] != self.condition_hot:
                self.status_target_next_max_or_avg_flag = 7
                self.DATA_operation_flag = False
                return

        elif self.status_target_next_max_or_avg_flag == 4:
            if self.DATA_all[self.DATA_all_index][6] == self.condition_hot_and_cold and self.DATA_all[self.DATA_all_index-1][6] != self.condition_hot_and_cold:
                self.status_target_next_max_or_avg_flag = 5
                self.DATA_operation_flag = False
                return
            elif self.DATA_all[self.DATA_all_index][6] == self.condition_hot and self.DATA_all[self.DATA_all_index-1][6] != self.condition_hot:
                self.status_target_next_max_or_avg_flag = 7
                self.DATA_operation_flag = False
                return
        elif self.status_target_next_max_or_avg_flag == 6:
            if self.DATA_all[self.DATA_all_index][6] == self.condition_hot and self.DATA_all[self.DATA_all_index-1][6] != self.condition_hot:
                self.status_target_next_max_or_avg_flag = 7
                self.DATA_operation_flag = False
                return

        elif self.status_target_next_max_or_avg_flag == 8:
            if self.status_edge_up[7] == False:
                if self.DATA_all[self.DATA_all_index][2] > self.status_target_next_max_or_avg :
                    self.status_target_next_max_or_avg_flag = 9
                    self.DATA_operation_flag = False
                    self.checker_next_target()
                    return
            elif self.status_edge_up[7] == True:
                if self.DATA_all[self.DATA_all_index][3] > self.status_target_next_max_or_avg :
                    self.status_target_next_max_or_avg_flag = 9
                    self.DATA_operation_flag = False
                    self.checker_next_target()
                    return
        elif self.status_target_next_max_or_avg_flag == 10:
            if self.status_edge_up[7] == False:
                if self.DATA_all[self.DATA_all_index][2] > self.status_target_next_max_or_avg :
                    self.status_target_next_max_or_avg_flag = 11
                    self.DATA_operation_flag = False
                    self.checker_next_target()
                    return
            elif self.status_edge_up[7] == True:
                if self.DATA_all[self.DATA_all_index][3] > self.status_target_next_max_or_avg :
                    self.status_target_next_max_or_avg_flag = 11
                    self.DATA_operation_flag = False
                    self.checker_next_target()
                    return
        elif self.status_target_next_max_or_avg_flag == 12:
            if self.status_edge_up[7] == False:
                if self.status_target_min_can_not_reach_flag == True:
                    if self.DATA_all[self.DATA_all_index][4] > self.status_target_min:
                        self.status_target_next_max_or_avg_flag = 13
                        self.DATA_operation_flag = False
                        return
                    elif self.DATA_all[self.DATA_all_index][2] > self.status_target_max * 1.2 :
                        self.status_target_next_max_or_avg_flag = 13
                        self.DATA_operation_flag = False
                        return
                elif self.DATA_all[self.DATA_all_index][2] > self.status_target_max :
                    self.status_target_next_max_or_avg_flag = 13
                    self.DATA_operation_flag = False
                    return
            elif self.status_edge_up[7] == True:
                if self.status_target_min_can_not_reach_flag == True:
                    if self.DATA_all[self.DATA_all_index][4] > self.status_target_min:
                        self.status_target_next_max_or_avg_flag = 13
                        self.DATA_operation_flag = False
                        return
                    elif self.DATA_all[self.DATA_all_index][3] > self.status_target_max * 1.2 :
                        self.status_target_next_max_or_avg_flag = 13
                        self.DATA_operation_flag = False
                        return
                elif self.DATA_all[self.DATA_all_index][3] > self.status_target_max :
                    self.status_target_next_max_or_avg_flag = 13
                    self.DATA_operation_flag = False
                    return
    def checker_even_number(self):
        if self.status_target_next_max_or_avg_flag == 1 :
            if self.time_break_time_counter > self.time_break_time_default:
                self.status_target_next_max_or_avg_flag += 1
                self.time_break_time_counter = -1
                self.DATA_operation_flag = True
        elif self.status_target_next_max_or_avg_flag == 3 :
            if self.time_break_time_counter > self.time_break_time_default:
                self.status_target_next_max_or_avg_flag += 1
                self.time_break_time_counter = -1
                self.DATA_operation_flag = True
        elif self.status_target_next_max_or_avg_flag == 5 :
            if self.DATA_all[self.DATA_all_index][5] < 30:
                if self.time_break_time_counter > 4 * self.time_break_time_default:
                    self.status_target_next_max_or_avg_flag += 1
                    self.time_break_time_counter = -1
                    self.DATA_operation_flag = True
            else:
                if self.time_break_time_counter > 2 * self.time_break_time_default:
                    self.status_target_next_max_or_avg_flag += 1
                    self.time_break_time_counter = -1
                    self.DATA_operation_flag = True
        elif self.status_target_next_max_or_avg_flag == 7 :
            if  self.time_break_time_counter > self.time_break_time_default:
                self.status_target_next_max_or_avg_flag += 1
                self.time_break_time_counter = -1
                self.DATA_operation_flag = True
        elif  self.status_target_next_max_or_avg_flag == 9 :
            if self.time_break_time_counter > self.time_break_time_default:
                self.status_target_next_max_or_avg_flag += 1
                self.time_break_time_counter = -1
                self.DATA_operation_flag = True
        elif self.status_target_next_max_or_avg_flag == 11 :
            if self.time_break_time_counter > self.time_break_time_default:
                self.status_target_next_max_or_avg_flag += 1
                self.time_break_time_counter = -1
                self.DATA_operation_flag = True
        elif self.status_target_next_max_or_avg_flag == 13 :
            if self.time_break_time_counter > 3 * self.time_break_time_default:
                if self.DATA_all[self.DATA_all_index][4] > self.status_target_min:  #if target_min is over the refference than turn - off the microwave oven
                    self.status_target_next_max_or_avg_flag += 1
                elif self.time_break_time_default < 1: # if there are too many operation! try to stop (this function for prevent infinity operation)
                    self.status_target_next_max_or_avg_flag += 1
                else: # if fail to achive the target then run again! but run it less
                    self.status_target_next_max_or_avg_flag += - 1
                    self.time_break_time_default = int(self.time_break_time_default / 2)
                    self.time_break_time_counter = -1
                    self.status_target_min_can_not_reach_flag = True


        #print("max_or_avg_flag :",self.status_target_next_max_or_avg_flag )
    def checker_10sec_break_time_update(self):
        if (self.status_target_next_max_or_avg_flag % 2) == 1:
            self.time_break_time_counter += 1
    def checker_operation_control(self):
        if self.status_target_next_max_or_avg_flag == 0:
            self.operation_flag = self.operation_all
            return
        if self.status_target_next_max_or_avg_flag > 13 :
            self.operation_flag = self.operation_turn_off
        elif (self.status_target_next_max_or_avg_flag % 2) == 0:
            self.operation_flag = self.operation_all
            print("operation_all" )
        elif (self.status_target_next_max_or_avg_flag % 2) == 1:
            self.operation_flag = self.operation_fan_only
            print("operation_fan_only" )
    def checker_std_data_control(self):
        refference = 50
        if self.DATA_all[self.DATA_all_index][7] > refference :
            print("what to do")
        elif self.DATA_all[self.DATA_all_index][7] < refference :
            print("what to do2")
# real control functions
    def checker_10sec(self):
        if self.status_10sec_flag == 0:
            self.checker_make_target_max_min()
        if (self.DATA_initial_data[0] < 3 ) and (self.status_10sec_flag >= 2):
            if self.DATA_all[self.DATA_all_index][2] < 400:
                print("(checker_10sec) no food detected!")
                self.status_target_next_max_or_avg_flag = 14
        self.checker_remain_time()
    def checker(self):  #every 1 sec check / edge up , steam check , fire check
        #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        self.checker_edge_up()
        self.checker_steam_condition()

        self.checker_status_target_next_max_or_avg_flag_controller()

        # self.checker_operation_control()  #do not imoport it at this time
        if (self.DATA_operation_flag == True) and self.status_10sec_flag >=1:
            self.time_remain_operation_time += -1
        if self.time_remain_operation_time < 0:
            self.time_remain_operation_time = 0
        self.checker_even_number()
        self.checker_10sec_break_time_update()
# run code functions
    def run_sound_out_finish(self):
        if self.status_target_next_max_or_avg_flag > 13:
            if self.condition_fire_count > 2:
                try:
                    print("fire sound_will paly")
                    os.system('omxplayer --vol 5000 /pi/home/Desktop/sound/fire_1.mp3')
                except:
                    print("failto play sound _ fire!!!! hehehehe")
            elif self.status_forced_stop_flag == True:
                try:
                    print("forced_stop_sound_will paly")
                    os.system('omxplayer --vol 5000 /pi/home/Desktop/sound/forced_1.mp3')
                except:
                    print("fail to paly sound _ forced _stop case")
            else :
                try:
                    print("normal_turn_off_sounr will paly")
                    os.system('omxplayer --vol 5000 /pi/home/Desktop/sound/final_1.mp3')
                except:
                    print("fail to play souend_ normal_ case")
    def run_initialization(self,icc_data):
        self.DATA_initial_data.extend(icc_data)
        if self.DATA_initial_data[0] == 1:
            self.status_target_next_max_or_avg_flag = 8
        elif self.DATA_initial_data[0] == 2:
            self.status_target_next_max_or_avg_flag = 4
        elif self.DATA_initial_data[0] == 3:
            self.status_target_next_max_or_avg_flag = 2
        elif self.DATA_initial_data[0] == 4:
            self.status_target_next_max_or_avg_flag = 0
        elif self.DATA_initial_data[0] == 5:
            self.status_target_next_max_or_avg_flag = 6
    def run_reset_time(self):
        self.time_initial_time = time.time()
        print("(Advanced_thermal_data_control) time_reset")
# main run of this class ,  if return True => turn off microwave oven
    def run(self,data):

        #postprocess level (get data and update this class)
        self.PostProcess(data)

        self.status_10sec_flag = int(self.DATA_all[self.DATA_all_index][0] / 10)
        if self.status_10sec_flag_pre < self.status_10sec_flag:
            self.checker_10sec()  # if pass the 10sec than run it
        if self.status_10sec_flag > 0:
            self.checker()
        self.status_10sec_flag_pre = self.status_10sec_flag

        self.checker_operation_control()

        self.checker_food_exist() # must be placed before MUC.run
        #real_micorwave_run_code
        self.MWC.run(self.operation_flag)
        # print("condition:",self.DATA_all[self.DATA_all_index][6])
        # print("breaktime:",self.time_break_time_counter)
        self.run_sound_out_finish()
        if self.operation_flag == self.operation_turn_off:
            return True  ##operation finish
        else:
            return False
#####################################################################################################################################
