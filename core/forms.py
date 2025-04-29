# Импорт служебных объектов Form
from django import forms
from django.core.exceptions import ValidationError
from .models import Service

# Форма создания услуги - делаем форму связанную с моделью


class ServiceForm(forms.ModelForm):
    # Расширим инициализатор для добавления form-control к полям формы

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс form-control к каждому полю формы
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    name = forms.CharField(
        label="Название услуги",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Введите название услуги"}),
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
