# core/urls.py
from django.contrib import admin
from django.urls import path
from .views import master_detail, thanks, test
# Эти маршруты будут доступны с префиксом /barbershop/

urlpatterns = [
    path('masters/<int:master_id>/', master_detail),
    path('thanks/', thanks),
    path('test/', test),

]
