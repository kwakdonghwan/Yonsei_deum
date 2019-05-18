from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('manual/', views.manual, name='manual'),
    path('auto/', views.auto, name='auto'),
    path('result/', views.result, name='result'),
    path('status/', views.status, name='status'),

]
