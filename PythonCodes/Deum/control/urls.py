from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('run/', views.run, name='run'),
]
