#new TD.run2 version


import Temp_process_developer as Temp_process
import RPi.GPIO as GPIO
import time #sleep함수를쓰기위해
from socket import *
import numpy as np
import struct
import cv2
import threading


import subprocess
import argparse
import os

#from .microwave import Temp_process

class CPP_open(threading.Thread):
    def __init__(self):

        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)
        print("camera_threading init")
    # try:
    #     self.cpp_camera = threading.Thread(target=self.camera_CPP, args=())
    #     self.cpp_camera.start()
    #
    #     sleep(2)
    #
    #     print("camera_cpp is started")
    # except:
    #     print("fail to open MLX90640 file (in thread level)")
    #     print("Please open it manualy")

    def run(self):

        CPP_path = "/home/pi/Yonsei_deum/camera_MLX90640/MLX90640"
        operator = "sudo "+ CPP_path + " 0.0625 8888"
        print(operator)
        if not os.path.isfile(CPP_path):
            print("CPP_file_ doesn`t exixt!!!!! did you make it?")
            print("please check:",CPP_path)

        try:

            self.p = subprocess.Popen([operator],
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            #print("subprocess_start")    
        except:

            print("fail to poen CPP_file_ in subprocess level")


    def camera_CPP(self):
        CPP_path = "/home/pi/Yonsei_deum/camera_MLX90640/MLX90640"
        operator = "sudo "+ CPP_path + " 0.0625 8888"  ## if you want use other program need to change
        try:
            subprocess.Popen([operator], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            #print("fail to open MLX90640`s CPP file (in subprocess level)")
            time.sleep(0.025)


class ManualController:
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

        self.refference_time = 10   ## this is roop for magnetron_control


        # t = int(input("enter time (s): "))
        # power = int(input("enter power(1-{}): ".format(max_power)))

        self.start_time = time.time()
        self.duration = 0
        self.power = 0
        self.stop_flag = False

    def reset_origin(self):

        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)
        self.start_time = time.time()
        self.duration = 0
        self.power = 0
        self.stop_flag = False


    def reset_param(self, power, duration):
        self.start_time = time.time()
        self.duration = duration
        self.power = power
        self.stop_flag = False
        GPIO.output(self.magnetron_pin, True)
        GPIO.output(self.fan_pin, True)
        print("target duration:", duration)

    def run(self,start_time2):


        if self.stop_flag:
            return True

        current_time = time.time()
        operation_time = current_time - start_time2
        operation_time2 = int(operation_time)
        operation_range = operation_time2 % self.refference_time
        if operation_range < self.power * self.refference_time / 10:
            GPIO.output(self.fan_pin, False)
            GPIO.output(self.magnetron_pin, False)
        else:
            GPIO.output(self.fan_pin, False)
            GPIO.output(self.magnetron_pin, True)

        if(operation_time > self.duration):
            GPIO.output(self.magnetron_pin, True)
            GPIO.output(self.fan_pin, True)
            self.stop_flag = True
            print("micro_wave_is_duen")


        return False

#while True:
#    Temp_process.what_is_fucking_color()

print("open new terminal key : Ctrl + Shift + T")

print("camera operation using terminal")
print("sudo /home/pi/Yonsei_deum/camera_MLX90640/MLX90640 0.0625 8888")
print("or in camera_path")
print("sudo ./MLX90640 0.0625 8888")

print("try to open cpp file automatically")
try:
    CPPfile = CPP_open()
    CPPfile.start()
    #CPPfile.run()
except:
    print("fail to open CPP MLX90640")

manual_controller = ManualController()
print("micro wave controller setup")

ip = '127.0.0.1'
port = 8888



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
    count = int(len(bin_data) / 2)
    trash_Data = struct.unpack('<' + ('h' * count), bin_data)

    bin_data1 = clientSock.recv(1536)
    count = int(len(bin_data) / 2)
    inditial_data = struct.unpack('<' + ('h' * count), bin_data)

    OPENTHEDOOR = IC8888.run(inditial_data)
    print("number_of_realpart:",OPENTHEDOOR[1],"edge_temp:",OPENTHEDOOR[2])
#



    manual_controller.reset_origin()
    print("reset_the_manual_controller")

    TD = Temp_process.Thermal_Data(OPENTHEDOOR[2])
    print("thermal_data_set_up")

    start_time = TD.initial_time

    #######################################################
        # check this this data stored in OPENTHEDOOR[0]
        # self.over_reffernce = 1
        # self.room_condition = 2
        # self.cool_condition = 3
        # self.icy_condtion = 4
        # self.hot_and_cold_condtion = 5
        # steam condtion will be 6




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
            #img = np.zeros((24, 24, 3), np.uint8)
            Newdata = np.zeros((24,24),np.int16)
            Newdata = TD.Thermal_data_cut(short_arr)
            #print("datcut complite")
            # min_tem = TD.run1(Newdata)
            run_output = TD.run5(Newdata)
            print("run5")
            # Temp_process.absolute_HSV_Control3_cut(Newdata, img,min_tem )
            #Temp_process.absolute_HSV_Control4(Newdata ,min_tem )
    
    
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

    trash = input("did you want run more? : (Y/N)")

    if trash == 'N' or trash == 'n':
        os.system("clear")
        print("turn off program")
        print("Good bye")
        break

