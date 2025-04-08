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
    # id - генерируется автоматически
    client_name = models.CharField(max_length=100)
    services = models.CharField(max_length=200)
    master_id = models.IntegerField()
    date = models.DateField()
    status = models.CharField(max_length=50)