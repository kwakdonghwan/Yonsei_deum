import numpy as np
import cv2
import statistics as s
import time
from datetime import datetime
import csv
import os


#########################
# initiallise
#
# TD = Thermal_Data()
#
# cut_data
#
# new_short_arr = TD.Thermal_data_cut(Left_X,Left_Y,Right_X,Right_Y,short_arr)
#
# run_calcuation
#
# TD.run1(new_short_arr)
#
# the data will display to terminal and save to workingPath/-----.csv
###############################

class Initial_condition_checker:

    def __init__(self):

        print("intitial_Checker_setup")
        self.initial_condition = 0

        self.over_reffernce = 1
        self.room_condition = 2
        self.cool_condition = 3
        self.icy_condtion = 4
        self.hot_and_cold_condtion = 5

        self.edge_data = 0
        self.realpart_number = 0
        self.origin_temp = 0


    def edge_temp_claculator(self, data):
        sem_of_edge = 0


        sem_of_edge += data[0][0] + data[0][1] + data[1][1] + data[1][0]
        sem_of_edge += data[0][22] + data[0][23] + data[1][22] + data[1][23]
        sem_of_edge += data[22][0] + data[22][1] + data[23][1] + data[23][0]
        sem_of_edge += data[22][22] + data[22][23] + data[23][22] + data[23][23]

        return sem_of_edge / 16
    def Thermal_data_cut(self, data):
        # to cut the thermal data set
        Left_Y = 0
        Right_Y = 0
        Left_X = 5
        Right_X = 3

        Newdata = np.zeros((24, 24), np.int16)  ##need to check
        # make new data array
        newpx = 0
        for py in range(0, 24):
            newpx = 0
            for px in range(4, 28):

                ###########################################################################
                # if data[py][px] == 0:
                #    print("x:", px , "y:", py)
                #
                ###############################################################################
                if py == 1 and px == 8:
                    Newdata[py][newpx] = data[py][px - 1]
                else:
                    #print(data[py][px])
                    Newdata[py][newpx] = data[py][px]

                # if Newdata[py][newpx] == 0:
                #     print(newpx, ",", py, "is zero")

                newpx += 1

                # cut data on dish

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

        self.origin_temp = s.mean(real_object_temp)

        return number_of_realpart


    def run(self,data):
        print("run_")
        newdata = self.Thermal_data_cut(data)
        self.edge_data = self.edge_temp_claculator(newdata)

        self.data_Condtion_checker(newdata)
        self.realpart_number = self.realpart_finder(newdata)

        print("intitial_condition_check_complited")

        return [self.initial_condition, self.realpart_number, self.edge_data]


class Thermal_Data:

    def __init__(self, room_termp):
        self.No_condition = 0

        self.hot_condtion = 1
        self.Room_temperature_condition = 2
        self.refrigeration_termperagrure_condition = 3
        self.icy_termperagrure_condition = 4
        self.hot_and_cold_condition = 5
        self.steam_condition = 6
        self.room_temperature = room_termp

        self.condition = self.No_condition
        self.old_condition = self.No_condition

        self.old_times = 0  # run time_ unit= sec
        self.old_Number_of_real_part = 0
        self.old_max_temp = 0
        self.old_max_rise_temp = 0
        self.old_min_temp = 0
        self.old_min_rise_temp = 0
        self.old_average_temp = 0
        self.old_average_rise_temp = 0
        self.old_average_middle = 0
        self.old_average_rise_middle = 0

        self.times = 0  # run time_ unit= sec
        self.Number_of_real_part = 0
        self.max_temp = 0
        self.max_rise_temp = 0
        self.min_temp = 0
        self.min_rise_temp = 0
        self.average_temp = 0
        self.average_rise_temp = 0
        self.average_middle = 0
        self.average_rise_middle = 0



        self.seven_sec_flag = 0    ##use for run6
        self.seven_sec_change = 0  ##use for run6



        self.initial_time = time.time()
        # current_path = os.getcwd()
        now = datetime.now()
        time_name = now.strftime("%Y_%m_%d %H_%M_%S")
        # new_time_name = current_path +"/data_out/se" +time_name + '.csv'
        # directory = current_path +"/data_out"
        # if not os.path.exists(directory):
        #    os.makedirs(directory)
        # self.f = open(new_time_name, 'w+', encoding='utf-8', newline='')
        save_path = "/home/pi/CSV_data"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        CSV_path = save_path + "/" + time_name + ".csv"
        self.f = open(CSV_path, 'w+', encoding='utf-8', newline='')

        self.wr = csv.writer(self.f)

        basic_info = (['time', 'Number_of_real_part', 'max_temp', 'min_temp', 'average_temp', 'max_rise_temp', 'min_rise_temp',
             'average_rise_temp','middle_temp','middle_rise_temp'])

        self.wr.writerow(basic_info)
    def __del__(self):


        self.f.close()

        try:
            cv2.destroyAllWindows()
        except:
            print("faile to close data")
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
        self.old_average_middle = self.average_middle
        self.old_average_rise_middle = self.average_rise_middle
    def claculate_temperature_change(self):
        if self.old_times <= 0:
            return
        
        time_difference = self.times - self.old_times
        if time_difference == 0:
            time_difference = 1
        max_temp_difference = self.max_temp - self.old_max_temp
        min_temp_difference = self.min_temp - self.old_min_temp
        average_temp_diffence = self.average_temp - self.old_average_temp
        average_middle_diffence = self.average_middle - self.old_average_middle

        self.max_rise_temp = max_temp_difference / time_difference
        self.min_rise_temp = min_temp_difference / time_difference
        self.average_rise_temp = average_temp_diffence / time_difference
        self.average_rise_middle = average_middle_diffence / time_difference
    def Thermal_data_cut(self, data):
        # to cut the thermal data set
        Left_Y = 0
        Right_Y = 0
        Left_X = 5
        Right_X = 3

        Newdata = np.zeros((24, 24), np.int16)  ##need to check
        # make new data array
        newpx = 0
        for py in range(0, 24):
            newpx = 0
            for px in range(4, 28):

                ###########################################################################
                # if data[py][px] == 0:
                #    print("x:", px , "y:", py)
                #
                ###############################################################################
                if py == 1 and px == 9:
                    Newdata[py][newpx] = data[py][px - 1]
                else:
                    Newdata[py][newpx] = data[py][px]

                # if Newdata[py][newpx] == 0:
                #     print(newpx, ",", py, "is zero")

                newpx += 1

                # cut data on dish

        return Newdata
    def csv_write_add(self, str1):
        self.wr.writerow([str1])
        print("write '" + str1 + "' on CSV file")
    def csv_wirter(self, str2):



        #if self.old_times > 0:
        #     str2 = self.times + self.Number_of_real_part + self.max_temp + self.min_temp + self.average_temp + self.max_rise_temp + self.min_rise_temp + self.average_rise_temp
        #     self.csv_wirter(str2)
        #     self.wr.writerow([self.times, self.Number_of_real_part, self.max_temp, self.min_temp, self.average_temp,
        #                       self.max_rise_temp, self.min_rise_temp, self.average_rise_temp])
        self.wr.writerow(str2)
    def edge_temp_claculator(self, data):
        sem_of_edge = 0


        sem_of_edge += data[0][0] + data[0][1] + data[1][1] + data[1][0]
        sem_of_edge += data[0][22] + data[0][23] + data[1][22] + data[1][23]
        sem_of_edge += data[22][0] + data[22][1] + data[23][1] + data[23][0]
        sem_of_edge += data[22][22] + data[22][23] + data[23][22] + data[23][23]

        return sem_of_edge / 16

    def autorun1(self,data):
        print("auto_run_data_get")


    def run1(self, data):
        # using statical condition.

        real_object_temp = []
        max_T = np.amax(data)
        min_T = np.amin(data)
        average_T = np.average(data)

        Total_number_of_data = data.shape[0] * data.shape[1]

        Number_of_real_temp = 0  # it is same with area of food

        ################################################making real_temp _list

        if min_T > self.room_temperature:
            # room temperature condition
            refference_temp = (4 * average_T + max_T) / 5
            condition = self.Room_temperature_condition
        elif 30 <= min_T < self.room_temperature:
            refference_temp = (3 * average_T + min_T) / 4
            condition = self.refrigeration_termperagrure_condition
        else:
            refference_temp = (2 * average_T + min_T) / 3
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
        # real_max_temp = max(real_object_temp)
        # real_min_temp = min(real_object_temp)
        # real_average_temp = s.mean(real_object_temp)
        #
        ################################################## out the data

        # before store new data, save it to old data
        self.New_data_to_old_data()

        self.Number_of_real_part = Number_of_real_temp
        self.condition = condition
        self.max_temp = max(real_object_temp)
        self.min_temp = min(real_object_temp)
        self.average_temp = s.mean(real_object_temp)
        self.times = time.time() - self.initial_time  # we need a time difference

        self.claculate_temperature_change()

        ##################################################
        # print it to terminal

        # print('time:',self.times,'real_part:',self.Number_of_real_part,'max:',self.max_temp ,'min:',self.min_temp,'average:',self.average_temp)
        # print('RiseMax:',self.max_rise_temp ,'RiseMin:',self.min_rise_temp,'RiseAverage:', self.average_rise_temp )

        # write csv file



        str2 = [self.times + self.Number_of_real_part + self.max_temp + self.min_temp + self.average_temp + self.max_rise_temp + self.min_rise_temp + self.average_rise_temp]
        self.csv_wirter(str2)
        str2.clear()
        real_object_temp.clear()

        #     self.wr.writerow([self.times, self.Number_of_real_part, self.max_temp, self.min_temp, self.average_temp,
        #                       self.max_rise_temp, self.min_rise_temp, self.average_rise_temp])
        return refference_temp
    def run2(self, data):

                #write mideel temp to csv file

        real_object_temp = []
        all_object_temp = []

        max_T = np.amax(data)
        min_T = np.amin(data)
        average_T = np.average(data)

        Total_number_of_data = data.shape[0] * data.shape[1]

        Number_of_real_temp = 0  # it is same with area of food
        middle_temperature_sum = 0
        count_middle = 0

        ################################################making real_temp _list

        if min_T > self.room_temperature:
            # room temperature condition
            refference_temp = (4 * average_T + max_T) / 5
            condition = self.Room_temperature_condition
        elif 30 <= min_T < self.room_temperature:
            refference_temp = (3 * average_T + min_T) / 4
            condition = self.refrigeration_termperagrure_condition
        else:
            refference_temp = (2 * average_T + min_T) / 3
            condition = self.icy_termperagrure_condition

        for py in range(data.shape[0]):
            for px in range(data.shape[1]):

                all_object_temp.append(data[py][px])

                if condition == self.Room_temperature_condition and data[py][px] > refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif condition == self.refrigeration_termperagrure_condition and data[py][px] < refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif condition == self.icy_termperagrure_condition and data[py][px] < refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])

    #################################### middle temperature collector #################
        for py in range (10,14):
            for px in range (10,14):
                middle_temperature_sum += data[py][px]
                count_middle += 1

        print("get middle")
    ####################################################################################
    ######################### store data to real ######################################
                # before store new data, save it to old data


       

        self.Number_of_real_part = Number_of_real_temp
        self.condition = condition
        self.max_temp = max(real_object_temp)
        self.min_temp = min(real_object_temp)
        self.average_temp = s.mean(real_object_temp)

        try:
            self.average_middle = middle_temperature_sum / count_middle
        except:
            print("unable to calculate middel termperature")

        self.times = time.time() - self.initial_time  # we need a time difference
        self.claculate_temperature_change()
        self.New_data_to_old_data()    
    ##################################################################################
    ############################# write data to csv_ format
        print("before instat data")
        out_put_data = [ self.times, self.Number_of_real_part, self.max_temp, self.min_temp, self.average_temp,
                         self.max_rise_temp, self.min_rise_temp, self.average_rise_temp , self.average_middle, self.average_rise_middle]
        out_put_data.extend(all_object_temp)
        print("tryto write csv")
        self.csv_wirter(out_put_data)
        print("csv_write")
        
    ###################################################################################
        return refference_temp
    def run3(self , data):

                #write mideel temp to csv file

        real_object_temp = []
        all_object_temp = []

        max_T = np.amax(data)
        min_T = np.amin(data)
        average_T = np.average(data)

        Total_number_of_data = data.shape[0] * data.shape[1]

        Number_of_real_temp = 0  # it is same with area of food
        middle_temperature_sum = 0
        count_middle = 0
        #print("before edge")
        edge_temp = self.edge_temp_claculator(data)

        ################################################making real_temp _list
        if min_T > 1.5 * self.room_temperature:
            # more than 40 degree condition
            refference_temp = (2*edge_temp + max_T) / 3
            condition = self.Room_temperature_condition

        elif min_T > self.room_temperature:
            # room temperature condition
            refference_temp = (4 * average_T + max_T) / 5
            condition = self.Room_temperature_condition
        elif 30 <= min_T < self.room_temperature:
            refference_temp = (3 * average_T + min_T) / 4
            condition = self.refrigeration_termperagrure_condition
        else:
            refference_temp = (2 * average_T + min_T) / 3
            condition = self.icy_termperagrure_condition

        for py in range(data.shape[0]):
            for px in range(data.shape[1]):

                all_object_temp.append(data[py][px])

                if condition == self.Room_temperature_condition and data[py][px] > refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif condition == self.refrigeration_termperagrure_condition and data[py][px] < refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif condition == self.icy_termperagrure_condition and data[py][px] < refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])

    #################################### middle temperature collector #################
        for py in range (10,14):
            for px in range (10,14):
                middle_temperature_sum += data[py][px]
                count_middle += 1

        #print("get middle")
    ####################################################################################
    ######################### store data to real ######################################
                # before store new data, save it to old data


       

        self.Number_of_real_part = Number_of_real_temp
        self.condition = condition
        self.max_temp = max(real_object_temp)
        self.min_temp = min(real_object_temp)
        self.average_temp = s.mean(real_object_temp)

        try:
            self.average_middle = middle_temperature_sum / count_middle
        except:
            print("unable to calculate middel termperature")

        self.times = time.time() - self.initial_time  # we need a time difference
        self.claculate_temperature_change()
        self.New_data_to_old_data()    
    ##################################################################################
    ############################# write data to csv_ format
        #print("before instat data")
        out_put_data = [ self.times, self.Number_of_real_part, self.max_temp, self.min_temp, self.average_temp,
                         self.max_rise_temp, self.min_rise_temp, self.average_rise_temp , self.average_middle, self.average_rise_middle]
        out_put_data.extend(all_object_temp)
        #print("tryto write csv")
        self.csv_wirter(out_put_data)
        print("csv_write_one_line")
        
    ###################################################################################
        return refference_temp
    def run4_assistant(self,num):
        if num < 100 :
            self.T_below10 += 1
        elif num < 200 :
            self.T_10to20 += 1
        elif num < 300 :
            self.T_20to30 += 1
        elif num < 400 :
            self.T_30to40 += 1
        elif num < 500 :
            self.T_40to50 += 1
        elif num < 600 :
            self.T_50to60 += 1
        elif num < 700 :
            self.T_60to70 += 1
        elif num < 800 :
            self.T_70to80 += 1
        elif num < 900 :
            self.T_80to90 += 1
        elif num < 1000 :
            self.T_90to100 += 1
        else:
            self.T_over100 += 1
    def run4(self , data):
    #termperaute gradient unit 10 is applised
        real_object_temp = []
        all_object_temp = []

        max_T = np.amax(data)
        min_T = np.amin(data)
        average_T = np.average(data)

        self.T_below10 = 0
        self.T_10to20 = 0
        self.T_20to30 = 0
        self.T_30to40 = 0
        self.T_40to50 = 0
        self.T_50to60 = 0
        self.T_60to70 = 0
        self.T_70to80 = 0
        self.T_80to90 = 0
        self.T_90to100 = 0
        self.T_over100 = 0

        Number_of_real_temp = 0  # it is same with area of food
        middle_temperature_sum = 0
        count_middle = 0
        #print("before edge")
        edge_temp = self.edge_temp_claculator(data)

        ################################################making real_temp _list
        if min_T > 1.5 * self.room_temperature:
            # more than 40 degree condition
            refference_temp = (2*edge_temp + max_T) / 3
            condition = self.Room_temperature_condition

        elif min_T > self.room_temperature:
            # room temperature condition
            refference_temp = (4 * average_T + max_T) / 5
            condition = self.Room_temperature_condition
        elif 30 <= min_T < self.room_temperature:
            refference_temp = (3 * average_T + min_T) / 4
            condition = self.refrigeration_termperagrure_condition
        else:
            refference_temp = (2 * average_T + min_T) / 3
            condition = self.icy_termperagrure_condition

        for py in range(data.shape[0]):
            for px in range(data.shape[1]):

                all_object_temp.append(data[py][px])
                self.run4_assistant(data[py][px])

                if condition == self.Room_temperature_condition and data[py][px] > refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif condition == self.refrigeration_termperagrure_condition and data[py][px] < refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif condition == self.icy_termperagrure_condition and data[py][px] < refference_temp:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])

    #################################### middle temperature collector #################
        for py in range (10,14):
            for px in range (10,14):
                middle_temperature_sum += data[py][px]
                count_middle += 1

        #print("get middle")
    ####################################################################################
    ######################### store data to real ######################################
                # before store new data, save it to old data



        number_of_temp_geadient = ["below10:",self.T_below10,"10-20:",self.T_10to20,"20-30:",self.T_20to30,"30-40:",self.T_30to40,"40-50:",self.T_40to50,"50-60:",self.T_50to60,"60-70",self.T_60to70,"70-80",self.T_70to80,"80-90:",self.T_80to90,"90-100",self.T_90to100,"over100",self.T_over100]
        self.Number_of_real_part = Number_of_real_temp
        self.condition = condition
        self.max_temp = max(real_object_temp)
        self.min_temp = min(real_object_temp)
        self.average_temp = s.mean(real_object_temp)

        try:
            self.average_middle = middle_temperature_sum / count_middle
        except:
            print("unable to calculate middel termperature")

        self.times = time.time() - self.initial_time  # we need a time difference
        self.claculate_temperature_change()
        self.New_data_to_old_data()
    ##################################################################################
    ############################# write data to csv_ format
        #print("before instat data")
        out_put_data = [ self.times, self.Number_of_real_part, self.max_temp, self.min_temp, self.average_temp,
                         self.max_rise_temp, self.min_rise_temp, self.average_rise_temp , self.average_middle, self.average_rise_middle]
        out_put_data.extend(number_of_temp_geadient)
        out_put_data.extend(all_object_temp)
        #print("tryto write csv")
        self.csv_wirter(out_put_data)
        print("csv_write_one_line")

    ###################################################################################
        return refference_temp
    def run5_assistant_condition_check(self,data,edge_temp):  ##check condition
        max_T = np.amax(data)
        min_T = np.amin(data)

        refference_temp2 = edge_temp

        if max_T > edge_temp * 1.2 and min_T < edge_temp * 0.8:
            self.condition = self.hot_and_cold_condition
            refference_temp1 = (3*edge_temp + max_T) / 4
            refference_temp2 = edge_temp * 0.8

        elif edge_temp > 750:
            self.condition = self.steam_condition
            refference_temp1 = (2*edge_temp + max_T) / 3

        elif max_T > edge_temp * 1.2:
            self.condition = self.hot_condtion
            refference_temp1 = (3*edge_temp + max_T) / 4

        elif min_T < 700:
            self.condition = self.icy_termperagrure_condition
            refference_temp1 = (2*edge_temp + min_T) / 3

        elif min_T < edge_temp * 0.85:
            self.condition = self.refrigeration_termperagrure_condition
            refference_temp1 = (edge_temp + min_T) / 2

        else:
            self.condition = self.Room_temperature_condition
            refference_temp1 = (3 * edge_temp + max_T) / 4

        return [refference_temp1,refference_temp2]
    def run5(self , data):
    #termperaute gradient unit 10 is applised and new analysis
    # run4_assistant is needed
        real_object_temp = []
        all_object_temp = []

        max_T = np.amax(data)
        min_T = np.amin(data)
        average_T = np.average(data)

        self.T_below10 = 0
        self.T_10to20 = 0
        self.T_20to30 = 0
        self.T_30to40 = 0
        self.T_40to50 = 0
        self.T_50to60 = 0
        self.T_60to70 = 0
        self.T_70to80 = 0
        self.T_80to90 = 0
        self.T_90to100 = 0
        self.T_over100 = 0

        Number_of_real_temp = 0  # it is same with area of food
        middle_temperature_sum = 0
        count_middle = 0
        #print("before edge")
        edge_temp = self.edge_temp_claculator(data)
        #############################################analysis condition
        analysis_condition_flag = 0

        max_higher_edeg_1_2_and_min_loewr_edge_0_85 = 1
        max_higeer_edeg_1_2 = 2
        min_lower_edge_0_85 = 3



        ################################################ condition setting
        rftp = self.run5_assistant_condition_check(data,edge_temp)

        ############################################  real analysis
        for py in range(data.shape[0]):
            for px in range(data.shape[1]):

                all_object_temp.append(data[py][px])
                self.run4_assistant(data[py][px])

                if self.condition == self.Room_temperature_condition and data[py][px] > rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])

                elif self.condition == self.refrigeration_termperagrure_condition and data[py][px] < rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])

                elif self.condition == self.icy_termperagrure_condition and data[py][px] < rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition == self.hot_condtion and data[py][px] > rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition == self.steam_condition and data[py][px] > rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition == self.hot_and_cold_condition:
                    if data[py][px] > rftp[0]:
                        Number_of_real_temp += 1
                        real_object_temp.append(data[py][px])
                    elif data[py][px] < rftp[1]:
                        Number_of_real_temp += 1
                        real_object_temp.append(data[py][px])



    #################################### middle temperature collector #################
        for py in range (10,14):
            for px in range (10,14):
                middle_temperature_sum += data[py][px]
                count_middle += 1

        #print("get middle")
    ####################################################################################
    ######################### store data to real ######################################
                # before store new data, save it to old data

        number_of_temp_geadient = ["below10:",self.T_below10,"10-20:",self.T_10to20,"20-30:",self.T_20to30,"30-40:",self.T_30to40,"40-50:",self.T_40to50,"50-60:",self.T_50to60,"60-70",self.T_60to70,"70-80",self.T_70to80,"80-90:",self.T_80to90,"90-100",self.T_90to100,"over100",self.T_over100]
        self.Number_of_real_part = Number_of_real_temp
        self.max_temp = max(real_object_temp)
        self.min_temp = min(real_object_temp)
        self.average_temp = s.mean(real_object_temp)

        try:
            self.average_middle = middle_temperature_sum / count_middle
        except:
            print("unable to calculate middel termperature")

        self.times = time.time() - self.initial_time  # we need a time difference
        self.claculate_temperature_change()
        self.New_data_to_old_data()
    ##################################################################################
    ############################# write data to csv_ format
        #print("before instat data")
        out_put_data = [ self.times, self.Number_of_real_part, self.max_temp, self.min_temp, self.average_temp,
                         self.max_rise_temp, self.min_rise_temp, self.average_rise_temp , self.average_middle, self.average_rise_middle]
        out_put_data.extend(all_object_temp)
        out_put_data.extend(number_of_temp_geadient)
        
        #print("tryto write csv")
        self.csv_wirter(out_put_data)
        print("csv_write_one_line")

    ###################################################################################
        return [rftp[0], self.Number_of_real_part]

    def run6_get_intitial_temp(self,temp):
        self.seven_sec_intital = temp
    def run6_senven_sec_controler(self):

        if (self.times-self.initial_time) > 7 and self.seven_sec_flag == 0 :
            self.seven_sec_flag = 1
            seven_sec_rise = self.max_temp - self.seven_sec_intital
            self.seven_sec_change = (seven_sec_rise/(self.times-self.initial_time))
    def run6(self , data):
    # this fucntion is add 7 sec data. and will show out data.
        real_object_temp = []
        all_object_temp = []

        max_T = np.amax(data)
        min_T = np.amin(data)
        average_T = np.average(data)

        self.T_below10 = 0
        self.T_10to20 = 0
        self.T_20to30 = 0
        self.T_30to40 = 0
        self.T_40to50 = 0
        self.T_50to60 = 0
        self.T_60to70 = 0
        self.T_70to80 = 0
        self.T_80to90 = 0
        self.T_90to100 = 0
        self.T_over100 = 0

        Number_of_real_temp = 0  # it is same with area of food
        middle_temperature_sum = 0
        count_middle = 0
        #print("before edge")
        edge_temp = self.edge_temp_claculator(data)
        #############################################analysis condition
        analysis_condition_flag = 0

        max_higher_edeg_1_2_and_min_loewr_edge_0_85 = 1
        max_higeer_edeg_1_2 = 2
        min_lower_edge_0_85 = 3



        ################################################ condition setting
        rftp = self.run5_assistant_condition_check(data,edge_temp)

        ############################################  real analysis
        for py in range(data.shape[0]):
            for px in range(data.shape[1]):

                all_object_temp.append(data[py][px])
                self.run4_assistant(data[py][px])

                if self.condition == self.Room_temperature_condition and data[py][px] > rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])

                elif self.condition == self.refrigeration_termperagrure_condition and data[py][px] < rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])

                elif self.condition == self.icy_termperagrure_condition and data[py][px] < rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition == self.hot_condtion and data[py][px] > rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition == self.steam_condition and data[py][px] > rftp[0]:
                    Number_of_real_temp += 1
                    real_object_temp.append(data[py][px])
                elif self.condition == self.hot_and_cold_condition:
                    if data[py][px] > rftp[0]:
                        Number_of_real_temp += 1
                        real_object_temp.append(data[py][px])
                    elif data[py][px] < rftp[1]:
                        Number_of_real_temp += 1
                        real_object_temp.append(data[py][px])



    #################################### middle temperature collector #################
        for py in range (10,14):
            for px in range (10,14):
                middle_temperature_sum += data[py][px]
                count_middle += 1

        #print("get middle")
    ####################################################################################
    ######################### store data to real ######################################
                # before store new data, save it to old data

        number_of_temp_geadient = ["below10:",self.T_below10,"10-20:",self.T_10to20,"20-30:",self.T_20to30,"30-40:",self.T_30to40,"40-50:",self.T_40to50,"50-60:",self.T_50to60,"60-70",self.T_60to70,"70-80",self.T_70to80,"80-90:",self.T_80to90,"90-100",self.T_90to100,"over100",self.T_over100]
        self.Number_of_real_part = Number_of_real_temp
        self.max_temp = max(real_object_temp)
        self.min_temp = min(real_object_temp)
        self.average_temp = s.mean(real_object_temp)

        try:
            self.average_middle = middle_temperature_sum / count_middle
        except:
            print("unable to calculate middel termperature")

        self.times = time.time() - self.initial_time  # we need a time difference
        self.claculate_temperature_change()
        self.New_data_to_old_data()
    ###################################################################################
    #########################configure 7sec data $$$$$$$$$$$$$$$$$$$$$$$$run 6
        self.run6_senven_sec_controler()


    ##################################################################################
    ############################# write data to csv_ format
        #print("before instat data")
        out_put_data = [ self.times, self.Number_of_real_part, self.max_temp, self.min_temp, self.average_temp,
                         self.max_rise_temp, self.min_rise_temp, self.average_rise_temp , self.average_middle, self.average_rise_middle]
        out_put_data.extend(all_object_temp)
        out_put_data.extend(number_of_temp_geadient)
        out_put_data.extend([self.seven_sec_change])

        #print("tryto write csv")
        self.csv_wirter(out_put_data)
        print("csv_write_one_line")

    ###################################################################################
        return [rftp[0], self.Number_of_real_part]



    def absolute_HSV_Control5(self,data4):
# cution!!! input data type is changed in this fucntion!!!!
# regardless of size of input data, it will automatically make img

# img range in hsv => 1 = blue / red >> 360 * 2.5 / 7    ==> 127
# color of img has been mdifyed


        img = np.zeros((24, 32, 3), np.uint8)
        thickness = 2
        org = (360, 10) # x =360 Y = 10
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.7
    #print("try to show img")
        for py in range(data4.shape[0]):
            for px in range(data4.shape[1]):
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

        # max_tmp = np.amax(data4) / 10

        #text_for_display = "max_temp: " + str(max_tmp)
        img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
        img = cv2.resize(img, None, fx=15, fy=15, interpolation=cv2.INTER_CUBIC)
        #cv2.putText(img, text_for_display, org, font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)

        ################# display _data ##############################
        display_max_temp = "max:" + str(self.max_temp/10)
        display_mid_temp = "mid:" + str(self.average_temp/10)
        display_min_temp = "min:" + str(self.min_temp/10)
        display_average_middle_temp = "A_M:" + str(self.average_middle/10)
        display_edge_temp = "edge:" + str(self.edge_temp_claculator(data4)/10)
        display_sec_change = "7SEC:" + str(self.seven_sec_change / 10)
        display_logo = "DEUM_yonsei"

        cv2.putText(img, display_max_temp, (360,30), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_mid_temp, (360, 70), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_min_temp, (360, 110), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_average_middle_temp, (360, 150), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_edge_temp, (360, 190), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_sec_change, (360, 230), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(img, display_logo, (360, 270), font, fontScale-0.2, (255, 255, 255), thickness, cv2.LINE_AA)


        #############################################################

        for py in range(24):
            for px in range(24):
                if int(self.min_temp) - 10 <= data4[py][px] <= int(self.min_temp) + 10:
                    img[py * 15][px * 15][0] = 255
                    img[py * 15][px * 15][1] = 255
                    img[py * 15][px * 15][2] = 255
                if int(self.min_temp) <= data4[py][px] :
                    img[py * 15][px * 15][0] = 0
                    img[py * 15][px * 15][1] = 0
                    img[py * 15][px * 15][2] = 0

        cv2.imshow('frame', img)
        try:
            cv2.moveWindow('frame' , 2, 2)
        except:
            print("fail_to move window")
        cv2.waitKey(1)
        return img




def absolute_HSV_Control2(data, img):
    ##this is for uncuted img

    thickness = 2
    org = (2, 478)
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1.2

    for py in range(24):
        for px in range(32):
            value_2 = 255
            value_3 = 255
            if 3000 >= data[py][px] > 1200:  # 2000 = 200C  max = 300
                value_1 = 1
                value_2 = 255 - ((data[py][px] - 1200) * 254 / 1000)  ## 0 = white
            elif data[py][px] > 1000:
                value_1 = 5 - ((data[py][px] - 1000) * 4 / 200)
            elif data[py][px] > 700:
                value_1 = 15 - ((data[py][px] - 700) * 10 / 300)
            elif data[py][px] > 600:
                value_1 = 30 - ((data[py][px] - 600) * 15 / 100)
            elif data[py][px] > 500:
                value_1 = 45 - ((data[py][px] - 500) * 15 / 100)
            elif data[py][px] > 400:
                value_1 = 60 - ((data[py][px] - 400) * 15 / 100)
            elif data[py][px] > 300:
                value_1 = 75 - ((data[py][px] - 300) * 15 / 100)
            elif data[py][px] > 200:
                value_1 = 90 - ((data[py][px] - 200) * 15 / 100)
            elif data[py][px] > 150:
                value_1 = 105 - ((data[py][px] - 150) * 15 / 50)
            elif data[py][px] > -100:
                value_1 = 115 - ((data[py][px] + 100) * 10 / 250)
            elif data[py][px] >= -300:
                value_1 = 120 
                value_3 = ((data[py][px] + 300) * 254 / 200)  ## 0 = black

            img[py][px][0] = 120 - int(value_1)  # 0~180
            img[py][px][1] = int(value_2)
            img[py][px][2] = int(value_3)

    max_tmp = np.amax(data) / 10
    text_for_display = "max_temp: " + str(max_tmp) + "  [deum_Yonsei]"
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    img = cv2.resize(img, None, fx=20, fy=15, interpolation=cv2.INTER_CUBIC)
    cv2.putText(img, text_for_display, org, font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
    # cv2.imshow('frame', img)
    # cv2.waitKey(1)
    return img
def absolute_HSV_Control2_cut(data, img):
    ##this is for cuted img

    thickness = 2
    org = (2, 478)
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1.2
    print("try to show img")
    for py in range(24):
        for px in range(24):
            value_2 = 255
            value_3 = 255
            if 3000 >= data[py][px] > 1200:  # 2000 = 200C  max = 300
                value_1 = 1
                value_2 = 255 - ((data[py][px] - 1200) * 254 / 1000)  ## 0 = white
            elif data[py][px] > 1000:
                value_1 = 5 - ((data[py][px] - 1000) * 4 / 200)
            elif data[py][px] > 700:
                value_1 = 15 - ((data[py][px] - 700) * 10 / 300)
            elif data[py][px] > 600:
                value_1 = 30 - ((data[py][px] - 600) * 15 / 100)
            elif data[py][px] > 500:
                value_1 = 45 - ((data[py][px] - 500) * 15 / 100)
            elif data[py][px] > 400:
                value_1 = 60 - ((data[py][px] - 400) * 15 / 100)
            elif data[py][px] > 300:
                value_1 = 75 - ((data[py][px] - 300) * 15 / 100)
            elif data[py][px] > 200:
                value_1 = 90 - ((data[py][px] - 200) * 15 / 100)
            elif data[py][px] > 150:
                value_1 = 105 - ((data[py][px] - 150) * 15 / 50)
            elif data[py][px] > -100:
                value_1 = 115 - ((data[py][px] + 100) * 10 / 250)
            elif data[py][px] >= -300:
                value_1 = 120
                value_3 = ((data[py][px] + 300) * 254 / 200)  ## 0 = black

            img[py][px][0] = int(value_1)  # 0~120
            img[py][px][1] = int(value_2)
            img[py][px][2] = int(value_3)

    max_tmp = np.amax(data) / 10

    text_for_display = "max_temp: " + str(max_tmp) + "  [deum_Yonsei]"
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    img = cv2.resize(img, None, fx=15, fy=15, interpolation=cv2.INTER_CUBIC)
    cv2.putText(img, text_for_display, org, font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
    cv2.imshow('frame', img)
    cv2.waitKey(1)
    return img
def absolute_HSV_Control3_cut(data, img, min_temp):
    ##this is for cuted img
    # display the min_temperature of data in img

    thickness = 2
    org = (2, 300)
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1.2
    #print("try to show img")
    for py in range(24):
        for px in range(24):
            value_2 = 255
            value_3 = 255
            if 3000 >= data[py][px] > 1200:  # 2000 = 200C  max = 300
                value_1 = 1
                value_2 = 255 - ((data[py][px] - 1200) * 254 / 1000)  ## 0 = white
            elif data[py][px] > 1000:
                value_1 = 5 - ((data[py][px] - 1000) * 4 / 200)
            elif data[py][px] > 700:
                value_1 = 15 - ((data[py][px] - 700) * 10 / 300)
            elif data[py][px] > 600:
                value_1 = 30 - ((data[py][px] - 600) * 15 / 100)
            elif data[py][px] > 500:
                value_1 = 45 - ((data[py][px] - 500) * 15 / 100)
            elif data[py][px] > 400:
                value_1 = 60 - ((data[py][px] - 400) * 15 / 100)
            elif data[py][px] > 300:
                value_1 = 75 - ((data[py][px] - 300) * 15 / 100)
            elif data[py][px] > 200:
                value_1 = 90 - ((data[py][px] - 200) * 15 / 100)
            elif data[py][px] > 150:
                value_1 = 105 - ((data[py][px] - 150) * 15 / 50)
            elif data[py][px] > -100:
                value_1 = 115 - ((data[py][px] + 100) * 10 / 250)
            elif data[py][px] >= -300:
                value_1 = 120
                value_3 = ((data[py][px] + 300) * 254 / 200)  ## 0 = black

            img[py][px][0] = int(value_1)  # 0~120
            img[py][px][1] = int(value_2)
            img[py][px][2] = int(value_3)

    max_tmp = np.amax(data) / 10

    text_for_display = "max_temp: " + str(max_tmp) 
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    img = cv2.resize(img, None, fx=15, fy=15, interpolation=cv2.INTER_CUBIC)
    cv2.putText(img, text_for_display, org, font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
    for py in range(24):
        for px in range(24):
            if int(min_temp) - 10 <= data[py][px] <= int(min_temp) + 10:
                img[py * 15][px * 15][0] = 255
                img[py * 15][px * 15][1] = 255
                img[py * 15][px * 15][2] = 255
            if int(min_temp) <= data[py][px] :
                img[py * 15][px * 15][0] = 0
                img[py * 15][px * 15][1] = 0
                img[py * 15][px * 15][2] = 0

    cv2.imshow('frame', img)
    try:
        cv2.moveWindow('frame' , 2, 2)
    except:
        print("fail_to move window")
    cv2.waitKey(1)
    return img
def absolute_HSV_Control4(data, min_temp):
# cution!!! input data type is changed in this fucntion!!!!
# regardless of size of input data, it will automatically make img

# img range in hsv => 1 = blue / red >> 360 * 2.5 / 7    ==> 127 
# color of img has been mdifyed


    img = np.zeros((24, 24, 3), np.uint8)
    thickness = 2
    org = (2, 300)
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1.2
    #print("try to show img")
    for py in range(data.shape[0]):
        for px in range(data.shape[1]):
            value_2 = 255
            value_3 = 255
            if 3000 >= data[py][px] > 1200:  # 2000 = 200C  max = 300
                value_1 = 1
                value_2 = 255 - ((data[py][px] - 1200) * 254 / 1000)  ## 0 = white
            elif data[py][px] > 1000:
                value_1 = 5 - ((data[py][px] - 1000) * 4 / 200)
            elif data[py][px] > 700:
                value_1 = 15 - ((data[py][px] - 700) * 10 / 300)
            elif data[py][px] > 600:
                value_1 = 30 - ((data[py][px] - 600) * 15 / 100)
            elif data[py][px] > 500:
                value_1 = 45 - ((data[py][px] - 500) * 15 / 100)
            elif data[py][px] > 400:
                value_1 = 60 - ((data[py][px] - 400) * 15 / 100)
            elif data[py][px] > 300:
                value_1 = 75 - ((data[py][px] - 300) * 15 / 100)
            elif data[py][px] > 200:
                value_1 = 90 - ((data[py][px] - 200) * 15 / 100)
            elif data[py][px] > 150:
                value_1 = 105 - ((data[py][px] - 150) * 15 / 50)
            elif data[py][px] > -100:
                value_1 = 115 - ((data[py][px] + 100) * 10 / 250)
            elif data[py][px] >= -300:
                value_1 = 120
                value_3 = ((data[py][px] + 300) * 254 / 200)  ## 0 = black

            img[py][px][0] = 125 - int(value_1)  # 0~120
            img[py][px][1] = int(value_2)
            img[py][px][2] = int(value_3)

    max_tmp = np.amax(data) / 10

    text_for_display = "max_temp: " + str(max_tmp) 
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    img = cv2.resize(img, None, fx=15, fy=15, interpolation=cv2.INTER_CUBIC)
    cv2.putText(img, text_for_display, org, font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
    for py in range(24):
        for px in range(24):
            if int(min_temp) - 10 <= data[py][px] <= int(min_temp) + 10:
                img[py * 15][px * 15][0] = 255
                img[py * 15][px * 15][1] = 255
                img[py * 15][px * 15][2] = 255
            if int(min_temp) <= data[py][px] :
                img[py * 15][px * 15][0] = 0
                img[py * 15][px * 15][1] = 0
                img[py * 15][px * 15][2] = 0

    cv2.imshow('frame', img)
    try:
        cv2.moveWindow('frame' , 2, 2)
    except:
        print("fail_to move window")
    cv2.waitKey(1)
    return img
def what_is_fucking_color():
    checking_img = np.zeros((10,360,3), np.uint8)
    # checking HSV img

    print("left is 1, right is 360")

    for x in range(360):
        for y in range(10):
            checking_img[y][x][0] = x + 1
            checking_img[y][x][1] = 255
            checking_img[y][x][2] = 255

    checking_img = cv2.cvtColor(checking_img, cv2.COLOR_HSV2RGB)
    cv2.imshow('fucking_color',checking_img)
    cv2.waitKey(1)




