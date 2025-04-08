# Lesson 48

## Знакомство с ORM
Django ORM - это инструмент, который позволяет работать с базой данных, используя Python-код вместо SQL-запросов. Он позволяет создавать, читать, обновлять и удалять записи в базе данных с помощью объектов Python.

ORM (Object-Relational Mapping) - это метод, который позволяет работать с реляционными базами данных, используя объектно-ориентированный подход. Он позволяет разработчикам работать с базой данных, используя объекты и классы, а не SQL-запросы.

## Создание таблицы

```python
class Order(models.Model):
    # id - генерируется автоматически
    client_name = models.CharField(max_length=100)
    services = models.CharField(max_length=200)
    master_id = models.IntegerField()
    date = models.DateField()
    status = models.CharField(max_length=50)
```

`models.Model` - это базовый класс, от которого наследуются все модели Django. Он предоставляет методы и атрибуты для работы с базой данных.

`models.CharField` - это поле, которое хранит строку фиксированной длины. `max_length` - это максимальная длина строки.

## Другие типы полей
- `TextField` - для хранения длинных текстов
- `SlugField` - для хранения коротких строк, обычно используемых в URL
- `CharField` - для хранения коротких строк
- `IntegerField` - для хранения целых чисел
- `FloatField` - для хранения чисел с плавающей точкой
- `BooleanField` - для хранения логических значений (True/False)
- `DateField` - для хранения дат
- `DateTimeField` - для хранения даты и времени
- `EmailField` - для хранения адресов электронной почты
- `URLField` - для хранения URL-адресов

## Типы валидаторов и свойств

- `max_length` - максимальная длина строки
- `min_length` - минимальная длина строки
- `blank` - позволяет ли поле быть пустым
- `null` - позволяет ли поле быть NULL в базе данных
- `choices` - позволяет задать список допустимых значений для поля
- `default` - значение по умолчанию для поля
- `unique` - уникальность значения в базе данных
- `db_index` - создание индекса для поля в базе данных
- `validators` - список валидаторов для поля

## Создание и применение миграций

После создания модели необходимо создать миграцию, которая создаст таблицу в базе данных. Для этого нужно выполнить команду:

```bash
python manage.py makemigrations
```

Эта команда создаст файл миграции в папке `migrations` вашего приложения. Файл миграции содержит информацию о том, какие изменения были внесены в модели.

После создания миграции необходимо применить ее к базе данных. Для этого нужно выполнить команду:

```bash
python manage.py migrate
```

Миграции **обязательно пушим на GitHub**. Это позволяет другим разработчикам видеть изменения в базе данных и применять их к своей локальной базе данных. Также это позволяет избежать конфликтов при работе с базой данных в команде.

## Django Shell Plus

Django Shell Plus - это расширенная версия Django Shell, которая автоматически импортирует все модели вашего проекта. Это позволяет вам работать с моделями и выполнять запросы к базе данных без необходимости вручную импортировать каждую модель.

Для установки Django Shell Plus необходимо установить пакет `django-extensions`. Для этого выполните команду:

```bash
pip install django-extensions
```

Или через poetry:

```bash
poetry add django-extensions
```

И подключить его в `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'django_extensions',
]
```

После этого вы можете запустить Django Shell Plus с помощью команды:

```bash
poetry run python manage.py shell_plus
```

Или с флагом отвечающим за вывод SQL запросов:

```bash
poetry run python manage.py shell_plus --print-sql
```

## Первые запросы к базе данных
В Django ORM есть несколько основных методов для работы с базой данных:
- `all()` - возвращает все записи из таблицы
- `filter()` - возвращает записи, которые соответствуют заданным условиям
- `exclude()` - возвращает записи, которые не соответствуют заданным условиям
- `get()` - возвращает одну запись, которая соответствует заданным условиям
- `create()` - создает новую запись в таблице
- `update()` - обновляет существующую запись в таблице
- `delete()` - удаляет запись из таблицы
- `count()` - возвращает количество записей в таблице
- `first()` - возвращает первую запись из таблицы

Наша таблица `Order` сейчас выглядит так:
```python
class Order(models.Model):
    # id - генерируется автоматически
    client_name = models.CharField(max_length=100)
    services = models.CharField(max_length=200)
    master_id = models.IntegerField()
    date = models.DateField()
    status = models.CharField(max_length=50)
```

```python
# Создание новой записи
order = Order.objects.create(
    client_name='Сергей Бурунов',
    services='Стрижка',
    master_id=1,
    date='2023-10-01',
    status='Завершен'
)

# Получим
order.status
order.client_name

# Получение всех записей
orders = Order.objects.all()

# Мы получили QuerySet - это специальный объект, который позволяет работать с набором данных. QuerySet можно фильтровать, сортировать и преобразовывать в списки и другие форматы.

# <QuerySet [<Order: Order object (1)>]>

orders[0] # Получим первую запись из QuerySet
orders[0].client_name # Получим имя клиента из первой записи

# Получим запись по id
order = Order.objects.get(id=1) # id - первичный ключ
order = Order.objects.get(pk=5) # pk - первичный ключ

order = Order.objects.filter(id=5) # Вернет QuerySet с одной записью

# Фильтр всегда вернет QuerySet, даже если он содержит только одну запись. Если в БД ни одной записи не будет, то вернет пустой QuerySet.
# get вернет объект, а если записи не будет, то вернет ошибку DoesNotExist. Если будет несколько записей, то вернет ошибку MultipleObjectsReturned.

# Создали заяку с таким же именем

order = Order.objects.get(client_name='Сергей Бурунов') # Вернет запись с именем клиента 'Сергей Бурунов'

# Получили MultipleObjectsReturned

order = Order.objects.filter(client_name='Сергей Бурунов').first()
```

##  get_object_or_404

```python
from django.shortcuts import get_object_or_404
order = get_object_or_404(Order, id=order_id)
```

`get_object_or_404` - это функция, которая пытается получить объект из базы данных. Если объект не найден, она возвращает ошибку 404 (Not Found). Это удобно использовать в представлениях, когда вы хотите вернуть 404 ошибку, если объект не найден.

```python
from django.shortcuts import get_object_or_404
# ...

@login_required
def order_detail(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    
    context = {"title": f"Заказ №{order_id}", "order": order}
    return render(request, "core/order_detail.html", context)
```