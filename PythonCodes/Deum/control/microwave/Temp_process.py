import numpy as np
import struct
import cv2 as cv
import subprocess
import statistics as s
import time
from datetime import datetime
import csv
import os


######################### ����
#initiallise
#
#TD = Thermal_Data()
#
#cut_data
#
#new_short_arr = TD.Thermal_data_cut(Left_X,Left_Y,Right_X,Right_Y,short_arr)
#
#run_calcuation
#
#TD.run1(new_short_arr)
#
#the data will display to terminal and save to workingPath/-----.csv
###############################



class Thermal_Data():
    ################ dictionaly define 
    #this is for control 
    No_condition = 0
    Room_temperature_condition = 1
    refrigeration_termperagrure_condition = 2
    icy_termperagrure_condition = 3
    

    room_temperature = 200 # 200 = 20.0

    #  #this is old type
    #TD = {}
    #TD['condition'] = No_condition
    #
    #TD['old_time'] = 0   #run time_ unit= sec
    #TD['old_Number_of_real_temp'] = 0 
    #TD['old_max_temp'] = 0
    #TD['old_min_temp'] = 0
    #TD['old_average_temp'] = 0
    #TD['old_average_rise_temp'] = 0
    #
    #TD['time'] = 0   #run time_ unit= sec
    #TD['Number_of_real_temp'] = 0 
    #TD['max_temp'] = 0
    #TD['min_temp'] = 0
    #TD['average_temp'] = 0
    #TD['average_rise_temp'] = 0
  
    
    old_condition = No_condition
    
    old_times = 0   #run time_ unit= sec
    old_Number_of_real_part = 0 
    old_max_temp = 0
    old_max_rise_temp = 0
    old_min_temp = 0
    old_min_rise_temp = 0
    old_average_temp = 0
    old_average_rise_temp = 0
    

    condition = No_condition
    times = 0   #run time_ unit= sec
    Number_of_real_part = 0 
    max_temp = 0
    max_rise_temp = 0
    min_temp = 0
    min_rise_temp = 0
    average_temp = 0
    average_rise_temp = 0

    
    def __init__(self):
        self.No_condition = 0
       
        self.Room_temperature_condition = 1
        self.refrigeration_termperagrure_condition = 2
        self.icy_termperagrure_condition = 3
        self.room_temperature = 200 
        
        self.condition = self.No_condition
        self.old_condition = self.No_condition
    
        self.old_times = 0   #run time_ unit= sec
        self.old_Number_of_real_part = 0 
        self.old_max_temp = 0
        self.old_max_rise_temp = 0
        self.old_min_temp = 0
        self.old_min_rise_temp = 0
        self.old_average_temp = 0
        self.old_average_rise_temp = 0
      
        self.times = 0   #run time_ unit= sec
        self.Number_of_real_part = 0 
        self.max_temp = 0
        self.max_rise_temp = 0
        self.min_temp = 0
        self.min_rise_temp = 0
        self.average_temp = 0
        self.average_rise_temp = 0


        self.initial_time = time.time()
        current_path = os.getcwd()
        now = datetime.now()
        time_name = now.strftime("%H_%M_%S")
        new_time_name = current_path +"\\" +time_name + '.csv'
        self.f = open(new_time_name, 'w+', encoding='utf-8', newline='')

        self.wr = csv.writer(self.f)

        self.wr.writerow(['time','Number_of_real_part','max_temp','min_temp','average_temp','max_rise_temp','min_rise_temp','average_rise_temp'])
    
    def New_data_to_old_data(self):

        self.old_condition = self.condition
    
        self.old_times = self.times
        self.old_Number_of_real_part = self.Number_of_real_part
        self.old_max_temp = self.max_temp
        self.old_max_rise_temp = self.max_rise_temp
        self.old_min_temp = self.min_temp
        self.old_min_rise_temp = self.min_rise_temp 
        self.old_average_temp = self.average_temp
        self.old_average_rise_temp = self.average_rise_temp
    

    def claculate_temperature_change(self):
        if self.old_times <= 0:
            return
        time_difference = self.times - self.old_times 
        max_temp_difference = self.max_temp - self.old_max_temp
        min_temp_difference = self.min_temp - self.old_min_temp
        average_temp_diffence = self.average_temp - self.old_average_temp

        self.max_rise_temp = max_temp_difference / time_difference
        self.min_rise_temp = max_temp_difference / time_difference
        self.average_rise_temp = average_temp_diffence / time_difference


        
    def Thermal_data_cut(self,Left_X,Left_Y,Right_X,Right_Y,data):
        #to cut the thermal data set
        
        Newdata= np.zeros((24-Left_Y-Right_Y,32-Left_X-Right_X),np.uint8)  ##need to check
        #make new data array
    
        for py in range(Left_Y,24-Right_Y):
            for px in range(Left_X,32-Right_X):
                Newdata[py][px] = data[py][px]
    
                # cut data on dish
    
        return Newdata
    
    ## Max data = np.amax(data)
    ## Min data = np.amin(data)
    
    ## cution! average data = np.average(data) or np.mean(data)
    
    def run1(self,data):
        #using statical condition.

        real_object_temp = []
        max_T = np.amax(data)
        min_T = np.amin(data)
        average_T = np.average(data)
    
        Total_number_of_data = data.shape[0] * data.shape[1]
    
        Number_of_real_temp = 0  # it is same with area of food
        
    
        condition = 3
        ################################################making real_temp _list
    
        if min_T > self.room_temperature :
            # room temperature condition
            refference_temp = (average_T + min_T) / 2
            condition = self.Room_temperature_condition
        elif 30 <= min_T < self.room_temperature:
            refference_temp = (average_T + max_T) / 2
            condition = self.refrigeration_termperagrure_condition
        else:
            refference_temp = (2 * average_T + max_T) / 3
            condition = self.icy_termperagrure_condition
    
        for py in range(1,data.shape[0]):
            for px in range(1,data.shape[1]):
                if condition == self.Room_temperature_condition and data[py][px] > refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif condition == self.refrigeration_termperagrure_condition and data[py][px] < refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif condition == self.icy_termperagrure_condition and data[py][px] < refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
        ##################################################find_what we want
        #       
        #
        #real_max_temp = max(real_object_temp)
        #real_min_temp = min(real_object_temp)
        #real_average_temp = s.mean(real_object_temp)
        #
        ################################################## out the data

        #before store new data, save it to old data
        self.New_data_to_old_data()

        self.Number_of_real_part = Number_of_real_temp
        self.condition = condition
        self.max_temp = max(real_object_temp)
        self.min_temp = min(real_object_temp)
        self.average_temp = s.mean(real_object_temp)
        self.times = time.time()  # we need a time difference

        self.claculate_temperature_change()

        ##################################################3
        #print it to terminal

        print('time:',self.times - self.initial_time,'real_part:',self.Number_of_real_part,'max:',self.max_temp ,'min:',self.min_temp,'average:',self.average_temp)
        print('RiseMax:',self.max_rise_temp ,'RiseMin:',self.min_rise_temp,'RiseAverage:', self.average_rise_temp )
        
        #write csv file

        self.wr.writerow([self.times - self.initial_time , self.Number_of_real_part , self.max_temp , self.min_temp , self.average_temp , self.max_rise_temp , self.min_rise_temp , self.average_rise_temp])
        


            