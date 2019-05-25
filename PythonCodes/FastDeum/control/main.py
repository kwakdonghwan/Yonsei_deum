from status_io import *
import auto_contorol as auto_control
import Temp_process_developer as Temp_process
import advanced_thermal_control as atc
from microwave.manual_controller import ManualController


from socket import *
import struct
import numpy as np
import cv2
import time

ip = '127.0.0.1'
port = 8888
max_power = 10

print("wait for camera connection")

clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect((ip, port))
print("connect success")


def auto_run():


    ICC = atc.Initial_condition_checker()
    ATD = atc.Advanced_thermal_data_control()

    bin_data1 = clientSock.recv(1536)
    count = int(len(bin_data1) / 2)
    initial_data = struct.unpack('<' + ('h' * count), bin_data1)
    np.asarray(initial_data)
    initial_data = np.reshape(initial_data, (24, 32))

    ATD.run_initialization(ICC.run(initial_data))
    time.sleep(2)
    bin_data1 = clientSock.recv(1536)
    count = int(len(bin_data1) / 2)
    initial_data = struct.unpack('<' + ('h' * count), bin_data1)
    np.asarray(initial_data)
    initial_data = np.reshape(initial_data, (24, 32))

    ATD.run_initialization(ICC.run(initial_data))
    ATD.run_reset_time()

    #######################################################

    print("----------------start_microwave_over--------------")

    while True:
        bin_data = clientSock.recv(1536)
        count = int(len(bin_data) / 2)
        short_arr = struct.unpack('<' + ('h' * count), bin_data)
        np.asarray(short_arr)
        short_arr = np.reshape(short_arr, (24, 32))

        lets_stop = ATD.run(short_arr)

        if lets_stop:
            break

    print("turn_off_microwave(auto_mode)")


def manual_run():

    manual_controller = ManualController()
    manual_controller.reset_param(0, 0)
    print("reset_the_manual_controller")
    TD = Temp_process.Thermal_Data(255)

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
        Temp_process.absolute_HSV_Control5(Newdata, min_tem)


        stop_wave = manual_controller.run()

        if stop_wave:
            break


while True:

    status = read_status()
    if status["on"] == 1:
        if status["mode"] == 1:   # 자동모드
            auto_run()

        elif status["mode"] == 0: # 수동모드
            manual_run()

        write_status(0, 0, 0, 0)
        cv2.destroyAllWindows()

    # 소켓 버퍼 비우기
    bin_data = clientSock.recv(1536)
    # count = int(len(bin_data) / 2)
    # _ = struct.unpack('<' + ('h' * count), bin_data)




