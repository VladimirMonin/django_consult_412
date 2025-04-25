# Импорт служебных объектов Form
from django import forms
from django.core.exceptions import ValidationError


# Форма создания услуги - пока делаем самый простой варинат 3 обязательных поля
# name
# description
# price


class ServiceForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        label="Название услуги",
        widget=forms.TextInput(
            attrs={"placeholder": "Введите название услуги", "class": "form-control"}
        ),
        error_messages={
            "required": "Пожалуйста, укажите название услуги",
            "max_length": "Название услуги не должно превышать 200 символов",
        },
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Введите описание услуги", "class": "form-control"}
        ),
        label="Описание услуги",
        error_messages={
            "required": "Необходимо добавить описание услуги",
        },
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Цена услуги",
        widget=forms.NumberInput(
            attrs={"placeholder": "Введите цену услуги", "class": "form-control"}
        ),
        error_messages={
            "required": "Пожалуйста, укажите стоимость услуги",
            "invalid": "Введите корректную стоимость (например: 1500.00)",
            "max_digits": "Стоимость не может содержать более 10 цифр",
            "max_decimal_places": "Стоимость не может содержать более 3 знаков после запятой",
        },
    )

    # Серия методов валидации которая начинается с clean_ и заканчивается на имя поля
    def clean_description(self):
        # Получаем значение поля description
        description = self.cleaned_data.get("description")
        # Проверяем, что в нем нет слова "плохое"
        if "плохое" in description.lower():
            raise ValidationError("В описании не должно быть слова 'плохое'")
        # Важно возвращать значение поля!
        return description
