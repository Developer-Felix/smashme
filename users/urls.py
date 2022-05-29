
from django.contrib import admin
from django.urls import path, include
from users.views import chat, customer_home, engineer_home, index
app_name = 'users'

urlpatterns = [
    path('',index, name='index'),
    path('customer/home/',customer_home, name='customer_home'),
    path('engineer/home/',engineer_home, name='engineer_home'),
    path('customer/chat',chat, name='chat'),
]
