# core/urls.py
from django.contrib import admin
from django.urls import path
from .views import (
    master_detail,
    thanks,
    orders_list,
    order_detail,
    service_create,
    service_update,
    services_list,
    masters_services_by_id,
)

# Эти маршруты будут доступны с префиксом /barbershop/

urlpatterns = [
    path("masters/<int:master_id>/", master_detail),
    path("thanks/", thanks, name="thanks"),
    path("orders/", orders_list, name="orders_list"),
    path("orders/<int:order_id>/", order_detail, name="order_detail"),
    path("services/", services_list, name="services_list"),
    path("service_create/", service_create, name="service_create"),
    path("service_update/<int:service_id>/", service_update, name="service_update"),
    path("masters_services/<int:master_id>/", masters_services_by_id, name="masters_services_by_id"),
]
