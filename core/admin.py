"""
filter_horizontal — для выбора ManyToMany через горизонтальный список.
filter_vertical — аналогично, но вертикальный список.
raw_id_fields — для ForeignKey и ManyToMany, чтобы выбирать связанные объекты по ID (без выпадающего списка).
autocomplete_fields — для ForeignKey и ManyToMany, чтобы выбирать связанные объекты через автодополнение (поиск).
formfield_overrides — позволяет задать виджет для конкретного типа поля (например, для всех CharField использовать Textarea).
form — можно указать свою форму (ModelForm) с любыми виджетами и логикой.
readonly_fields — позволяет сделать поле только для чтения (например, для отображения картинки или вычисляемого значения).
"""

from django.contrib import admin
from .models import Order, Master, Service, Review

# Регистрация в одну строку
admin.site.register(Service)

# Класс OrderAdmin для кастомизации админки для модели Order
class OrderAdmin(admin.ModelAdmin):
    # Список отображаемых полей в админке
    list_display = ("client_name", "phone", "status", "appointment_date", "master")
    # Редактируемые поля в админке
    list_editable = ("status", "master")
    filter_horizontal = ("services",)
    autocomplete_fields = ("master",)
    # Поля, по которым можно будет искать
    search_fields = ("client_name", "phone", "comment")
    # Фильтры которые Django сделает автоматически сбоку
    list_filter = ("status", "master", "appointment_date")

    # Нередактируемые поля в админке
    readonly_fields = ("date_created", "date_updated")


    list_per_page = 25
    actions = ("make_approved", "make_not_approved", "make_spam", "make_completed", "make_canceled")

    # Кастомные действия 
    @admin.action(description="Подтвердить")
    def make_approved(self, request, queryset):
        """Метод для подтверждения выбранных заказов"""
        queryset.update(status="approved")

    @admin.action(description="Не подтвержденные")
    def make_not_approved(self, request, queryset):
        """Метод для перевода выбранных заказов в статус "Не подтвержденные" """
        queryset.update(status="not_approved")

    @admin.action(description="Спам")
    def make_spam(self, request, queryset):
        """Метод для перевода выбранных заказов в статус "Спам" """
        queryset.update(status="spam")

    @admin.action(description="Завершить")
    def make_completed(self, request, queryset):
        """Метод для завершения выбранных заказов"""
        queryset.update(status="completed")

    @admin.action(description="Отменить")
    def make_canceled(self, request, queryset):
        """Метод для отмены выбранных заказов"""
        queryset.update(status="canceled")


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
    # Настройка для пагинатора (сколько мастеров на одной странице)
    list_per_page = 25

    # Кастомизация детального представления мастера
    readonly_fields = ("view_count",)
    # Поле многие ко многим для услуг мастера 
    filter_horizontal = ("services",)


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
# Регистрация модели Order с кастомной админкой
admin.site.register(Order, OrderAdmin)