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


def index(request):
    global stop_thread
    stop_thread = True
    return render(request, 'control/index.html', {})


def run(request):

    return


def manual(request):
    status = open("status", "w")
    power = request.POST['power']
    duration = request.POST['duration']

    status.write(power + " " + duration + " " + "1")
    return render(request, 'control/index.html', {})