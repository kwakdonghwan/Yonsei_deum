from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, StreamingHttpResponse

from django.views.decorators import gzip
from socket import *
import numpy as np
import struct
import cv2
import threading

from .microwave import maxheat

from .microwave import manual
from .microwave import Temp_process
from .streaming import camera


import RPi.GPIO as GPIO
import time #sleep함수를쓰기위해




# ip = '192.168.219.118'
ip = '127.0.0.1'
port = 8880
cam = camera.VideoCamera()
cam.init_socket(ip, port)

manual_controller = manual.ManualController()
current_max = 0

stop_thread = True


def gen(camera):
    while True:
        if stop_thread:
            break
        frame = cam.get_frame()
        # temperature_controller.run(current_max)
        manual_controller.run()


        if manual_controller.stop_flag == True:
            try:
                cam.close_record()
            except:
                print("fali to close record stream")

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def index(request):
    global stop_thread
    stop_thread = True
    return render(request, 'control/index.html', {})




@gzip.gzip_page
def run(request):
    global temperature_controller
    temperature_controller.on()
    try:
        return StreamingHttpResponse(gen(camera.VideoCamera()),
                                     content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        print("getting image fail")
        pass



@gzip.gzip_page
def manual(request):
    global manual_controller
    global cam
    power = int(request.POST['power'])
    duration = int(request.POST['duration'])

    manual_controller.reset_param(power, duration)
    print("duration: ", power, duration)
    try:
        cam.start_record()
        print("record_data start")
    except:
        print("fail to start record")



    global stop_thread
    stop_thread = True
    try:
        return StreamingHttpResponse(gen(camera.VideoCamera()),
                                     content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        print("getting image fail")
        pass
