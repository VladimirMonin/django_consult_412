from django.contrib import admin
from .models import Order, Master, Service, Review

# Регистрация в одну строку
admin.site.register(Order)
admin.site.register(Service)
admin.site.register(Review)

# Класс для кастомного фильтра для фильтрации по рейтингу мастера
# Создаем кастомный фильтр по рейтингу
class RatingFilter(admin.SimpleListFilter):
    # Название параметра в URL
    parameter_name = 'avg_rating'
    # Заголовок фильтра в админке
    title = 'Средний рейтинг'
    
    def lookups(self, request, model_admin):
        """Определяем варианты фильтрации, которые будут отображаться в админке"""
        return (
            ('no_rating', '❌'),
            ('low', '⭐⭐'),
            ('medium', '⭐⭐⭐'),
            ('high', '⭐⭐⭐⭐'),
            ('perfect', '⭐⭐⭐⭐⭐'),
        )
    
    def queryset(self, request, queryset):
        """Логика фильтрации мастеров по выбранному значению"""
        # Если не выбран фильтр, возвращаем все записи
        if not self.value():
            return queryset
            
        # Получаем всех мастеров
        filtered_masters = []
        
        # Фильтруем мастеров в зависимости от выбранного значения
        for master in queryset:
            rating = master.avg_rating()
            
            if self.value() == 'no_rating' and rating == 0:
                filtered_masters.append(master.pk)
            elif self.value() == 'low' and 0 < rating < 3:
                filtered_masters.append(master.pk)
            elif self.value() == 'medium' and 3 <= rating < 4:
                filtered_masters.append(master.pk)
            elif self.value() == 'high' and 4 <= rating < 5:
                filtered_masters.append(master.pk)
            elif self.value() == 'perfect' and rating == 5:
                filtered_masters.append(master.pk)
        
        # Возвращаем отфильтрованный queryset
        return queryset.filter(pk__in=filtered_masters)


class MasterAdmin(admin.ModelAdmin):
    # Список полей, которые будут отображаться в админке в виде таблицы (в этом же порядке!)
    list_display = ("first_name", "last_name", "phone", "experience",  "avg_rating_display", "is_active")
    # Кликабельные поля - имя и фамилия мастера
    list_display_links = ("first_name", "last_name")
    # Фильтры которые Django сделает автоматически сбоку
    list_filter = ("is_active", "services", "experience", RatingFilter)
    # Поля, по которым можно будет искать
    search_fields = ("first_name", "last_name", "phone")
    # Порядок сортировки
    ordering = ("last_name", "first_name")
    # Редактируемые поля в админке (не должны быть в list_display_links)
    list_editable = ("is_active", "experience")
    # Подключение кастомных действий
    actions = ("make_active", "make_inactive")

    
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
        
    # Кастомное действие для админки (Сделать Активным)

    @admin.action(description="Сделать активными")
    def make_active(self, request, queryset):
        """Метод для активации выбранных мастеров"""
        queryset.update(is_active=True)

    @admin.action(description="Сделать неактивными")
    def make_inactive(self, request, queryset):
        """Метод для деактивации выбранных мастеров"""
        queryset.update(is_active=False)


    # Регистрация модели Master с кастомной админкой
admin.site.register(Master, MasterAdmin)