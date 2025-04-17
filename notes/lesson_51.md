## Lesson 51 - Lookups в Django и Qbjects



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

```python
# Варианты логического И
# Вариант 1, перечисление условий через запятую

# Записи к мастерам чьи имена начинаются на А и Б
s1 = Service.objects.filter(masters__first_name__startswith="А", masters__last_name__startswith="Б")

s11 = Master.objects.filter(first_name__startswith="А", last_name__startswith="Б")

# Накинуть второй фильтр позже
s2 = Service.objects.filter(masters__first_name__startswith="А")
s2 = s2.filter(masters__last_name__startswith="Б")


```

Это будет работать отлично с логическим И.
Но для логического ИЛИ и НЕ надо использовать Q-объекты.

```python
from django.db.models import Q

# Вариант 1 сразу 2 условия формата ИЛИ
s3 = Service.objects.filter(Q(masters__first_name__startswith="А") | Q(masters__last_name__startswith="Б"))

# Вариант 2, где у нас есть выборка а потом через IF мы накидываем фильтры

search_query = "Стрижка под монаха"
check_box_phone = True
check_box_name = True
check_box_comment = True

s4 = Service.objects.all()

if check_box_phone:
    s4 = Q(s4, phone__icontains=search_query)

if check_box_name:
    s4 = Q(s4, client_name__icontains=search_query)

if check_box_comment:
    s4 = Q(s4, comment__icontains=search_query)

```

Операторы Q-объектов:
- `&` - логическое И
- `|` - логическое ИЛИ
- `~` - логическое НЕ

