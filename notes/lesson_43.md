# Lesson 43
**Тема: Django Templates. Подключение статики. Базовый синтаксис шаблонов.  Урок: 43**

## Типы данных и шаблоны в Django

```python
# core/views.py
# Так же был сделан тестовый маршрут для проверки работы шаблонов test/
def test(request):
    
    class TestClass:
        def __init__(self, name):
            self.name = name
        
        def __str__(self):
            return f'Экземпляр класса {self.__class__.__name__} с именем {self.name}'
        
        def say_my_name(self):
            return f'Меня зовут {self.name}'
    
    test_instance = TestClass('Тестовый экземпляр')
    
    context = {
        "string": "Мастер по усам",
        "number": 42,
        "list": ["Стрижка бороды", "Усы-таракан", "Укладка бровей"],
        "dict": {"best_master": "Алевтина Арбузова"},
        "class": test_instance
    }
    return render(request, 'test.html', context)
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <h1>Эксперименты с данными в шаблонизаторе Django</h1>
    <p>Строка: {{string}}</p>
    <p>Число: {{number}}</p>
    <p>Список: {{list}}</p>
    <p>Список обращение к индексу 0: {{list.0}}</p>
    <p>Словарь: {{dict}}</p>
    <p>Словарь обращение к ключу: {{dict.best_master}}</p>
    <p>Экземпляр класса: {{class}}</p>
    <p>Экземпляр класса обращение к атрибуту: {{class.name}}</p>
    <p>Экземпляр класса обращение к методу: {{class.say_my_name}}</p>"
</body>
</html>
```

Мы попробовали как будут отрабатывать разные типы данных при передаче их в шаблон.
Работает все, кроме вызова методов экземпляра с аргументами! Без аргументов будет работать отлично!

### Знакомство с условными операторами

```python
    class Employee:
        def __init__(self, name: str, is_active: bool):
            self.name = name
            self.is_active = is_active
        
        def __str__(self):
            return f'Экземпляр класса {self.__class__.__name__} с именем {self.name}'
        
        def say_my_name(self):
            return f'Меня зовут {self.name}'
    
    employee = Employee('Алевтина', True)

        context = {
        "employee": employee
    }
```

```html
    <p>Сотрудник: {{employee.name}}</p>
    <p>Статус: {{employee.is_active}}</p>
    {% if employee.is_active %}
        <p>Сотрудник работает</p>
    {% else %}
        <p>Сотрудник уволен</p>
    {% endif %}
```

#### Ветвление с `elif`

```python
# core/views.py
class Employee:
    def __init__(self, name: str, is_active: bool, is_married: bool, age: int, salary: float, position: str, hobbies: list):
        self.name = name
        self.is_active = is_active
        self.is_married = is_married
        self.age = age
        self.salary = salary
        self.position = position
        self.hobbies = hobbies

    def __str__(self):
        return f'Имя: {self.name}.\nВозраст: {self.age}.\nЗарплата: {self.salary}.\nДолжность: {self.position}.'


def test(request):
    
    employee = Employee('Алевтина', True, True, 42, 100000, 'manager', ['Журналы про усы', 'Компьютерные игры', 'Пиво'])
    employee2 = Employee('Бородач', True, False, 25, 50000, 'master', ['Садоводство', 'Пиво', 'Компьютерные игры'])
    
    context = {
        "string": "Мастер по усам",
        "number": 42,
        "list": ["Стрижка бороды", "Усы-таракан", "Укладка бровей"],
        "dict": {"best_master": "Алевтина Арбузова"},
        "employee": employee,
        "employee2": employee2

    }
    return render(request, 'test.html', context)
```

```html
  <h3>Вариант 2</h3>
    <div class="employee">
      <p>Имя: {{employee.name}}</p>
      <p>Статус: {{employee.is_active}}</p>
      {% comment %} Вветвление с проверкой на равенство строк {% endcomment %}
      {% if employee.position == "manager" %}
      <p class="yellow-position">Менеджер барбершопа</p>
      {% elif employee.position == "master" %}
      <p class="blue-position">Мастер барбершопа</p>
      {% else %}
      <p>Неизвестная должность</p>
      {% endif %} {% comment %} Вветвление с проверкой на больше меньше{%endcomment %} 
      {% if employee.salary > 90000 %}
      <p>Зарплата зарплата руководящей должности: {{employee.position}}</p>
      {% elif employee.salary > 50000 %}
      <p>Зарплата зарплата мастера: {{employee.position}}</p>
      {% endif %}
```html

### Подключение статики

Для подключения статики в Django, нужно создать папку `static` в корне проекта и в ней создать папку `css` и файл `style.css`

В файле `settings.py` нужно добавить путь к папке со статикой и URL для статики:

```python
# Указали путь к статическим файлам в проекте. Это адрес на сервере, по которому будут доступны статические файлы
STATIC_URL = 'static/'

# Указали путь к папке, где будут храниться статические файлы
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

В шаблоне мы можем получить доступ к этим файлам.
Пути пишем относительно папки `static`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <link rel="stylesheet" href="{% static 'css/test.css' %}">
    <script src="{% static 'js/test.js' %}"></script>
  </head>
  <body>
    <h1>Эксперименты с данными в шаблонизаторе Django</h1>
    <p>Строка: {{string}}</p>
........
```

### Знакомство с циклом шаблонизатора

```python
# core/views.py
def test(request):
    
    employee = Employee('Алевтина', True, True, 42, 100000, 'manager', ['Журналы про усы', 'Компьютерные игры', 'Пиво'])
    employee2 = Employee('Бородач', True, False, 25, 50000, 'master', ['Садоводство', 'Пиво', 'Компьютерные игры'])
    employee3 = Employee("Барбарис", True, False, 30, 60000, 'master', ['Газонокосилки', 'Пиво', 'Стрельба из арбалета'])
    employee4 = Employee("Сифон", True, True, 35, 70000, 'master', ['Брендовый шмот', 'Походы в ГУМ', 'Аниме'])

    # Список сотрудников
    employees = [employee, employee2, employee3, employee4]
    
    context = {
        "string": "Мастер по усам",
        "number": 42,
        "list": ["Стрижка бороды", "Усы-таракан", "Укладка бровей"],
        "dict": {"best_master": "Алевтина Арбузова"},
        "employee": employee,
        "employee2": employee2,
        "employees": employees

    }
    return render(request, 'test.html', context)
```

```html
    <h2>Циклы</h2>
    {% for employee  in employees %}
    <div class="employee">
        <p>Имя: {{employee.name}}</p>
        <p>Статус: {{employee.is_active}}</p>
        {% comment %} Вветвление с проверкой на равенство строк {% endcomment %}
        {% if employee.position == "manager" %}
        <p class="yellow-position">Менеджер барбершопа</p>
        {% elif employee.position == "master" %}
        <p class="blue-position">Мастер барбершопа</p>
        {% else %}
        <p>Неизвестная должность</p>
        {% endif %} {% comment %} Вветвление с проверкой на больше меньше{%endcomment %} 
        {% if employee.salary > 90000 %}
        <p>Зарплата зарплата руководящей должности: {{employee.position}}</p>
        {% elif employee.salary < 90000 and employee.salary > 10000 %}
        <p>Зарплата зарплата мастера: {{employee.position}}</p>
        {% endif %}
      </div>
    {% endfor %}
```