
from django.contrib import admin
from django.urls import path, include
from users.views import chat, customer_home, engineer_home, index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('users.urls')),
]
