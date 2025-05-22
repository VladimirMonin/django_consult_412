from django.contrib import admin
from .models import Order, Master, Service, Review

# Регистрация в одну строку
admin.site.register(Order)
admin.site.register(Service)
admin.site.register(Review)

# Создание кастомной админки для модели Master


class MasterAdmin(admin.ModelAdmin):
    # Список полей, которые будут отображаться в админке в виде таблицы (в этом же порядке!)
    list_display = ("first_name", "last_name", "phone", "experience",  "avg_rating_display", "is_active")
    # Кликабельные поля - имя и фамилия мастера
    list_display_links = ("first_name", "last_name")
    # Фильтры которые Django сделает автоматически сбоку
    list_filter = ("is_active", "services", "experience")
    # Поля, по которым можно будет искать
    search_fields = ("first_name", "last_name", "phone")
    # Порядок сортировки
    ordering = ("last_name", "first_name")

    
    # Какое название будет у поля в админке
    @admin.display(description="Средняя оценка")
    def avg_rating_display(self, obj) -> str:
        """Форматированное отображение средней оценки"""
        # Obj = Экземпляр модели Master
        rating = obj.avg_rating()
        if 0 < rating < 1:
            return "🎃"
        elif 1 <= rating < 2:
            return "⭐"
        elif 2 <= rating < 3:
            return "⭐⭐"
        elif 3 <= rating < 4:
            return "⭐⭐⭐"
        elif 4 <= rating < 5:
            return "⭐⭐⭐⭐"
        elif rating == 5:
            return "⭐⭐⭐⭐⭐"
        else:
            return "❌"


# Регистрация модели Master с кастомной админкой
admin.site.register(Master, MasterAdmin)