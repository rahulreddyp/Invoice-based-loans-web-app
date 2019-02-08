from django.contrib.auth import views as auth_views
from django.contrib import admin
from firstapp import views
from django.urls import path, include

urlpatterns = [
    path('register/', views.register, name='signup'),
    path('home/', views.home, name='home'),
]

