# Импорт служебных объектов Form
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ClearableFileInput
from .models import Service

# Форма создания услуги - делаем форму связанную с моделью


class ServiceForm(forms.ModelForm):
    # Расширим инициализатор для добавления form-control к полям формы

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс form-control к каждому полю формы (кроме чекбоксов)
        for field_name, field in self.fields.items():
            if field_name != 'is_popular':  # Пропускаем чекбокс
                field.widget.attrs.update({"class": "form-control"})
            else:  # Для чекбокса добавляем класс переключателя
                field.widget.attrs.update({"class": "form-check-input"})

    name = forms.CharField(
        label="Название услуги",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Введите название услуги"}),
    )
    
    # Переопределяем поле изображения, чтобы убрать ненужные элементы
    image = forms.ImageField(
        label="Изображение услуги",
        required=False, 
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": "image/*"  # Разрешаем только изображения
        })
    )

    # Валидатор deля поля description
    def clean_description(self):
        description = self.cleaned_data.get("description")
        if len(description) < 10:
            raise ValidationError("Описание должно содержать не менее 10 символов.")
        return description

    class Meta:
        model = Service
        # # Поля, которые будут отображаться в форме
        fields = ["name", "description", "price", "duration", "is_popular", "image"]
