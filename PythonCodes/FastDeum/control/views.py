from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, StreamingHttpResponse

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

def read_status():

    f = open("control/status.txt", "r")
    line = f.readline()
    f.close()
    mode = int(line.split(" ")[0])
    on = int(line.split(" ")[1])
    duration = int(line.split(" ")[2])
    power = int(line.split(" ")[3])

    return {"mode": mode, "on": on, "duration": duration, "power": power}


def write_status(mode, on, duration, power):
    f = open("control/status.txt", "w")
    f.write("{} {} {} {}".format(mode, on, duration, power))
    f.close()


def index(request):

    return render(request, 'control/index.html')


def manual(request):
    write_status(0, 0, 0, 0)

    return render(request, 'control/manual.html')

def auto(request):
    write_status(0, 0, 0, 0)

    return render(request, 'control/auto.html')


@csrf_exempt
def result(request):
    device = int(request.POST['device'])
    power = int(request.POST['power'])
    duration = int(request.POST['duration'])
    mode = int(request.POST['mode'])
    on = int(request.POST['on'])
    write_status(mode, on, duration, power)

    if device == 0:
        return render(request, 'control/result.html')
    else:
        return HttpResponse(1)



def status(request):

    st = read_status()

    return HttpResponse(st["on"])













