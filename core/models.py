from django.db import models
"""
CharField - строковое поле, которое может хранить текстовые данные.
TextField - текстовое поле, которое может хранить большие объемы текста.
IntegerField - целочисленное поле, которое может хранить целые числа.
DateField - поле для хранения даты.
BooleanField - логическое поле, которое может хранить значения True или False.
JsonField - поле для хранения JSON-данных.

"""


class Order(models.Model):

    # Статусы заказов
    STATUS_CHOICES = [
        ("not_approved", "Не подтвержден"),
        ("moderated", "Прошел модерацию"),
        ("spam", "Спам"),
        ("approved", "Подтвержден"),
        ("in_awaiting", "В ожидании"),
        ("completed", "Завершен"),
        ("canceled", "Отменен"),
    ]

    client_name = models.CharField(max_length=100)
    services = models.CharField(max_length=200)
    master_id = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="not_approved")