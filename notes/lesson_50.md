# Lesson 50 - Lookups в Django

## Определение
- Lookups - это способ фильтрации данных в Django ORM, который позволяет использовать различные операторы сравнения и логические операции для создания сложных запросов к базе данных.


## Таблица доступных Lookups в Django

| Lookup | Описание | Пример использования |
|--------|----------|----------------------|
| **exact** | Точное совпадение (регистрозависимый) | `Model.objects.filter(name__exact='Александр')` |
| **iexact** | Точное совпадение (регистронезависимый) | `Model.objects.filter(name__iexact='александр')` |
| **contains** | Содержит подстроку (регистрозависимый) | `Model.objects.filter(name__contains='екс')` |
| **icontains** | Содержит подстроку (регистронезависимый) | `Model.objects.filter(name__icontains='екс')` |
| **in** | Значение находится в списке | `Model.objects.filter(id__in=[1, 3, 5])` |
| **gt** | Больше чем (greater than) | `Model.objects.filter(price__gt=1000)` |
| **gte** | Больше или равно (greater than or equal) | `Model.objects.filter(price__gte=1000)` |
| **lt** | Меньше чем (less than) | `Model.objects.filter(price__lt=1000)` |
| **lte** | Меньше или равно (less than or equal) | `Model.objects.filter(price__lte=1000)` |
| **startswith** | Начинается с (регистрозависимый) | `Model.objects.filter(name__startswith='Алек')` |
| **istartswith** | Начинается с (регистронезависимый) | `Model.objects.filter(name__istartswith='алек')` |
| **endswith** | Заканчивается на (регистрозависимый) | `Model.objects.filter(name__endswith='др')` |
| **iendswith** | Заканчивается на (регистронезависимый) | `Model.objects.filter(name__iendswith='ДР')` |
| **range** | Значение находится в диапазоне | `Model.objects.filter(price__range=(1000, 2000))` |
| **date** | Для полей даты/времени - только дата | `Model.objects.filter(created_at__date='2025-04-17')` |
| **year** | Для полей даты/времени - год | `Model.objects.filter(created_at__year=2025)` |
| **month** | Для полей даты/времени - месяц | `Model.objects.filter(created_at__month=4)` |
| **day** | Для полей даты/времени - день | `Model.objects.filter(created_at__day=17)` |
| **week** | Для полей даты/времени - неделя | `Model.objects.filter(created_at__week=15)` |
| **week_day** | Для полей даты/времени - день недели (1-7) | `Model.objects.filter(created_at__week_day=2)` |
| **quarter** | Для полей даты/времени - квартал (1-4) | `Model.objects.filter(created_at__quarter=2)` |
| **time** | Для полей даты/времени - только время | `Model.objects.filter(created_at__time='14:30:00')` |
| **hour** | Для полей даты/времени - час | `Model.objects.filter(created_at__hour=14)` |
| **minute** | Для полей даты/времени - минута | `Model.objects.filter(created_at__minute=30)` |
| **second** | Для полей даты/времени - секунда | `Model.objects.filter(created_at__second=45)` |
| **isnull** | Проверка на NULL | `Model.objects.filter(phone__isnull=True)` |
| **regex** | Соответствие регулярному выражению (регистрозависимый) | `Model.objects.filter(name__regex=r'^А.*р$')` |
| **iregex** | Соответствие регулярному выражению (регистронезависимый) | `Model.objects.filter(name__iregex=r'^а.*р$')` |


```python
# Наши модели
from doctest import master
from django.db import models
"""

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
    phone = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    # Для поля choices будет добавлен метод get_<field>_display() - в данном случае get_status_display() - возвращает человеческое название статуса
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="not_approved")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    # Один ко многим
    master = models.ForeignKey("Master", on_delete=models.SET_NULL, null=True, related_name="orders")
    services = models.ManyToManyField("Service", related_name="orders", blank=True)
    # Дата времени, когда клиент хочет записаться на услугу
    appointment_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Заказ {self.id} от {self.client_name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        # Сортировка по-умолчанию минус это по убыванию
        ordering = ["-date_created"]

        # Создаем индексы
        indexes = [
            # Индекс по полю status
            models.Index(fields=['status'], name='status_idx'),
            # Индекс по полю date_created (хотя для сортировки он может создаться и так,
            # но явное указание не повредит и поможет при фильтрации)
            models.Index(fields=['date_created'], name='created_at_idx'),
            # Пример составного индекса, если бы мы часто искали заказы мастера за период
            # models.Index(fields=['client_name', 'phone'], name='master_created_idx'),
        ]
            


class Master(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="images/masters/", blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    experience = models.PositiveIntegerField()
    # Многие ко многим
    services = models.ManyToManyField("Service", related_name="masters")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена услуги")
    duration = models.PositiveIntegerField(help_text="Время в минутах", verbose_name="Время выполнения услуги")
    is_popular = models.BooleanField(default=False, verbose_name="Популярная услуга")
    image = models.ImageField(upload_to="images/services/", blank=True, null=True, verbose_name="Изображение услуги")

    def __str__(self):
        return f'{self.name} - {self.price} руб.'

    
    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
```

## Примеры использования Lookups

```python
# Найти все заказы, где мастера зовут "Анна"
annas_orders = Order.objects.filter(master__first_name="Анна")

# А можно искать по фамилии
ivanov_orders = Order.objects.filter(master__last_name="Иванов")

# Или даже комбинировать (Тут будет логическое И)
anna_ivanova_orders = Order.objects.filter(
    master__first_name="Анна", 
    master__last_name="Иванова"
)

# Имя похожее на "Анна"
similar_orders = Order.objects.filter(master__first_name__icontains="Ан")

# Найти всех мастеров, оказывающих маникюр
manicure_masters = Master.objects.filter(services__name="Маникюр")

# А может, тебе нужны все мастера, оказывающие популярные услуги?
popular_service_masters = Master.objects.filter(services__is_popular=True)

# Или даже мастера, которые оказывают услуги дороже 1000 рублей
expensive_service_masters = Master.objects.filter(services__price__gt=1000)


# Найти все заказы, которые были созданы после 1 января 2023 года
experienced_manicure_masters = Master.objects.filter(
    experience__gt=3,
    services__name__icontains="маник"
)

# Допустим, клиент хочет записаться на 20 апреля 2025, 15:00
target_date = datetime(2025, 4, 20, 15, 0)

# Сначала найдём мастеров, у которых уже есть заказы на это время
busy_masters_ids = Order.objects.filter(
    appointment_date=target_date,
    status__in=["approved", "in_awaiting"]  # Только подтверждённые заказы и ожидающие
).values_list('master_id', flat=True)

# Теперь найдём всех свободных мастеров маникюра
available_manicure_masters = Master.objects.filter(
    services__name="Маникюр",
    is_active=True
).exclude(
    id__in=busy_masters_ids
).distinct()
```

Запуск shell-plus
```bash
poetry run python manage.py shell_plus --print-sql
```

## Практика

```python
# №1. Найдите мастера с id 1 в переменную master_1
master_1 = Master.objects.get(pk=1)

# Положите его имя в переменную master_1_name
master_1_name = master_1.first_name

# №2. C помощью лукапа найдите все услуги которые он оказывает (по имени)
.all
master_1.services.all() - вернет QuerySet с объектами Service, которые он оказывает

Service.objects.filter(masters__first_name=master_1_name) - вернет QuerySet с объектами Service, которые он оказывает

Service.objects.filter(masters__first_name__icontains=master_1_name) - вернет QuerySet с объектами Service, которые он оказывает (регистронезависимый)

# №3. Через таблицу услуг, найдите все заказы которые выполняет master_1_name
filter(services__...)
master_1.orders.all() - вернет QuerySet с объектами Order, которые он выполняет
Service.objects.filter(orders__master__first_name=master_1_name) - вернет QuerySet с объектами Order, которые он выполняет
```
