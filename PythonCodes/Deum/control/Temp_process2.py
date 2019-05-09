import numpy as np
import struct
import cv2
import subprocess
import statistics as s
import time
from datetime import datetime
import csv
import os


#########################
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



class Thermal_Data:
    
    def __init__(self,room_termp):
        self.No_condition = 0
       
        self.Room_temperature_condition = 1
        self.refrigeration_termperagrure_condition = 2
        self.icy_termperagrure_condition = 3
        self.room_temperature = room_termp 
        
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
        #current_path = os.getcwd()
        now = datetime.now()
        time_name = now.strftime("%Y_%m_%d %H_%M_%S")
        #new_time_name = current_path +"/data_out/se" +time_name + '.csv'
        #directory = current_path +"/data_out"
        #if not os.path.exists(directory):
        #    os.makedirs(directory)
        #self.f = open(new_time_name, 'w+', encoding='utf-8', newline='')
        save_path = "/home/pi/CSV_data"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        CSV_path = save_path + "/" + time_name + ".csv"
        self.f = open(CSV_path, 'w+', encoding='utf-8', newline='')


        self.wr = csv.writer(self.f)

        self.wr.writerow(['time','Number_of_real_part','max_temp','min_temp','average_temp','max_rise_temp','min_rise_temp','average_rise_temp'])

    def __del__(self):

        self.No_condition = 0
       
        self.Room_temperature_condition = 1
        self.refrigeration_termperagrure_condition = 2
        self.icy_termperagrure_condition = 3
        self.room_temperature = 0
        
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

        self.initial_time = 0
        time_name = ""

        self.f.close()

    
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


        
    def Thermal_data_cut(self,data):
        #to cut the thermal data set
        Left_Y = 0
        Right_Y = 0
        Left_X = 5
        Right_X = 3 
        
        Newdata= np.zeros((24,24),np.int16)  ##need to check
        #make new data array
        newpx = 0
        for py in range(0,24):
            newpx = 0 
            for px in range(5,29):

                ###########################################################################
                #if data[py][px] == 0:
                #    print("x:", px , "y:", py)
                #
                ###############################################################################
                if py == 1 and px == 9:
                    Newdata[py][newpx] = data[py][px - 1]
                else:
                    Newdata[py][newpx] = data[py][px]

                if Newdata[py][newpx] == 0:
                    print(newpx,",",py,"is zero")

                newpx += 1
            
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

        ################################################making real_temp _list
    
        if min_T > self.room_temperature:
            # room temperature condition
            refference_temp = (4 * average_T + min_T) / 5
            condition = self.Room_temperature_condition
        elif 30 <= min_T < self.room_temperature:
            refference_temp = (3 * average_T + max_T) / 4
            condition = self.refrigeration_termperagrure_condition
        else:
            refference_temp = (2 * average_T + max_T) / 3
            condition = self.icy_termperagrure_condition
    
        for py in range(data.shape[0]):
            for px in range(data.shape[1]):
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
        self.times = time.time() - self.initial_time  # we need a time difference

        self.claculate_temperature_change()

        ##################################################
        #print it to terminal

        #print('time:',self.times,'real_part:',self.Number_of_real_part,'max:',self.max_temp ,'min:',self.min_temp,'average:',self.average_temp)
        #print('RiseMax:',self.max_rise_temp ,'RiseMin:',self.min_rise_temp,'RiseAverage:', self.average_rise_temp )
        
        #write csv file



        if self.old_times > 0 :
            self.wr.writerow([self.times , self.Number_of_real_part , self.max_temp , self.min_temp , self.average_temp , self.max_rise_temp , self.min_rise_temp , self.average_rise_temp])

    def csv_write_add (self, str1):
        self.wr.writerow([str1])
        print("write '" + str1 + "' on CSV file")

def absolute_HSV_Control2 (data, img):
    ##this is for uncuted img

    thickness = 2
    org = ( 2, 478 )
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1.2

    for py in range(24):
        for px in range(32):
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
    text_for_display = "max_temp: " + str(max_tmp) + "  [deum_Yonsei]"
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    img = cv2.resize(img, None, fx=20, fy=15, interpolation=cv2.INTER_CUBIC)
    cv2.putText(img, text_for_display, org, font , fontScale , (255,255,255) , thickness , cv2.LINE_AA)
    # cv2.imshow('frame', img)
    # cv2.waitKey(1)
    return img


def absolute_HSV_Control2_cut (data, img):
    ##this is for cuted img

    thickness = 2
    org = ( 2, 478 )
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1.2
    print("try to show img")
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


            img[py][px][0] = int(value_1)  # 0~120
            img[py][px][1] = int(value_2)
            img[py][px][2] = int(value_3)

    max_tmp = np.amax(data) / 10
   
    text_for_display = "max_temp: " + str(max_tmp) + "  [deum_Yonsei]"
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    img = cv2.resize(img, None, fx=15, fy=15, interpolation=cv2.INTER_CUBIC)
    cv2.putText(img, text_for_display, org, font , fontScale , (255,255,255) , thickness , cv2.LINE_AA)
    cv2.imshow('frame', img)
    cv2.waitKey(1)
    return img



