# core/urls.py
from django.contrib import admin
from django.urls import path
from .views import master_detail, thanks, test, orders_list, order_detail
# Эти маршруты будут доступны с префиксом /barbershop/

urlpatterns = [
    path('masters/<int:master_id>/', master_detail),
    path('thanks/', thanks),
    path('orders/', orders_list),
    path('orders/<int:order_id>/', order_detail),

    # path('test/', test),

]
