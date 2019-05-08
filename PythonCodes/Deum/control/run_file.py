from .microwave import Temp_process
import RPi.GPIO as GPIO
import time #sleep함수를쓰기위해
from socket import *
import numpy as np
import struct
import cv2
import threading

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


        # t = int(input("enter time (s): "))
        # power = int(input("enter power(1-{}): ".format(max_power)))

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

    def run(self):

        if self.stop_flag:
            return 8888

        GPIO.output(self.fan_pin, False)
        GPIO.output(self.magnetron_pin, False)
        time.sleep(self.power/(self.max_power*self.control_time))
        GPIO.output(self.magnetron_pin, True)
        time.sleep((self.max_power-self.power)/(self.max_power*self.control_time))
        GPIO.output(self.magnetron_pin, False)

        current_time = time.time()
        if(current_time - self.start_time > self.duration):
            GPIO.output(self.magnetron_pin, True)
            GPIO.output(self.fan_pin, True)
            self.stop_flag = True
            print("micro_wave_is_duen")


        return 0


print("open new terminal key : Ctrl + Shift + T")

print("camera operation using terminal")
print("sudo /home/pi/Yonsei_deum/camera_MLX90640/MLX90640 0.0625 8888")
print("or in camera_path")
print("sudo ./MLX90640 0.0625 8888")

ip = '127.0.0.1'
port = 8888

clientSock = socket(AF_INET, SOCK_STREAM)
print("connect start")
clientSock.connect((ip, port))
print("connect success")
# temperature_controller = maxheat.TemperatureController(70)
manual_controller = ManualController()
print("micro wave controller setup")

TD = Temp_process.Thermal_Data(200)
print("thermal_data_set_up")

print("input_your_time(min is 1s) and power(max is 10)")
print("only 'int' type will be accepted")
duration = int(input("enter time (s) ex) 15: "))
power = int(input("enter power(1-{}): ex) 7 "))

manual_controller.reset_param(power, duration)

lets_stop = 0

while True:
    bin_data = clientSock.recv(1536)
    count = int(len(bin_data) / 2)
    short_arr = struct.unpack('<' + ('h' * count), bin_data)
    np.asarray(short_arr)

    try:
        short_arr = np.reshape(short_arr, (24, 32))
        img = np.zeros((24, 24, 3), np.uint8)
        Newdata= np.zeros((24,24),np.int8)
        Newdata =  TD.Thermal_data_cut(short_arr)
        Temp_process.absolute_HSV_Control2_cut(Newdata,img)
        TD.run1(Newdata)

    except:
        print("Fail_in_camera")

    try:
        lets_stop = manual_controller.run()

    except:
        print("Fail_in_manual_controller")


    if lets_stop == 8888:
        print("turn_off_micro_wave")
        str1 = input("enter_the_object_name(in english):")
        TD.csv_write_add(str1)
        break

