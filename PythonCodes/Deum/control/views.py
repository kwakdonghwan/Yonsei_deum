from django.shortcuts import render
from django.http import HttpResponse
import time
import cv2

# Create your views here.


def index(request):

    return render(request, 'control/index.html', {})


def run(request):

    for i in range(10):
        print(i)
        time.sleep(1)

    return HttpResponse('hihi')