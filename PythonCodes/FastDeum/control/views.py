from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, StreamingHttpResponse
from .status_io import *

import time #sleep함수를쓰기위해

from django.views.decorators.csrf import csrf_exempt

'''
status: 
    mode  0: 수동   1: 자동
    on/off  0: off   1: on
    duration 초
    power    
    
device:
    0: display   1: phone
'''



def index(request):

    write_status(0, 0, 0, 0, 0)
    return render(request, 'control/index.html')


def manual(request):
    write_status(0, 0, 0, 0, 0)
    return render(request, 'control/manual.html')

def auto(request):
    write_status(0, 0, 0, 0, 0)

    return render(request, 'control/auto.html')


@csrf_exempt
def result(request):
    device = int(request.POST['device'])
    power = int(request.POST['power'])
    duration = int(request.POST['duration'])
    mode = int(request.POST['mode'])
    on = int(request.POST['on'])
    write_status(mode, on, duration, power, device)

    print(mode, on, duration, power, device)
    print("device:", device)

    if device == 0:  # request from display
        return render(request, 'control/result.html')
    else:            # request from app
        return HttpResponse(1)


@csrf_exempt
def status(request):

    st = read_status()

    return HttpResponse(st["on"])














