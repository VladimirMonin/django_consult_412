from django.contrib import admin
from .models import Order, Master, Service

# Регистрация в одну строку
admin.site.register(Order)
admin.site.register(Master)
admin.site.register(Service)