from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.register, name='signup'),
    path('', views.home, name='home'),
]

