from django.contrib import admin
from django.urls import path
from probeData import views


urlpatterns = [
    path('index', views.index),
    path('probesqlsave', views.probesqlsave),
    path('transport', views.transport),
    path('get24HourData', views.get24HourData),
    path('getSites', views.getSites),
    path('selectSite', views.selectSite),
    path('sendData', views.sendData),
    path('warningRealTime', views.warningRealTime),
    path('historyWarning', views.historyWarning),
    path('rtSite', views.rtSite),
    path('ugPerson', views.ugPerson),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
]
