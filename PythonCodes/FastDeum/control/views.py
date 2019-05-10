from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, StreamingHttpResponse

import time #sleep함수를쓰기위해


def index(request):

    return render(request, 'control/index.html')


def manual(request):
    status = open("control/status.txt", "w")
    status.write("0 0 0")
    status.close()
    return render(request, 'control/manual.html')


def result(request):
    status = open("control/status.txt", "w")
    power = request.POST['power']
    duration = request.POST['duration']
    status.write("1 " + power + " " + duration)
    status.close()

    return render(request, 'control/result.html')


def status(requset):
    f = open("control/status.txt", "r")
    line = f.readline()
    runnig_state = line.split(" ")[0]
    f.close()
    return HttpResponse(runnig_state)
