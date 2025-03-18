## Lesson 42

### Структура проекта Django

![Структура проекта Django](.\images\2025-03-18_20-57-54.png)

### Отладка Django в Visual Studio Code

```json
{
    "version": "0.2.0",
    "configurations": [
      {
        "name": "Django: Запуск через Poetry",
        "type": "debugpy",
        "request": "launch",
        "program": "${workspaceFolder}/manage.py",
        "args": ["runserver"],
        "django": true,
        "justMyCode": true,
        "console": "integratedTerminal",
        "env": {
          "PYTHONPATH": "${workspaceFolder}"
        }
      },
      {
        "name": "Django: Отладка представлений",
        "type": "debugpy",
        "request": "launch",
        "program": "${workspaceFolder}/manage.py",
        "args": ["runserver", "--noreload"],
        "django": true,
        "justMyCode": false,
        "console": "integratedTerminal",
        "env": {
          "PYTHONPATH": "${workspaceFolder}"
        }
      }
    ]
  }
```

### Первый маршрут и функция View
Это похоже на адресную книгу. Мы заходим на главную страницу, и в `urls.py` Django ищет соответствующий маршрут. Если находит, то вызывает функцию View, которая возвращает ответ.

![Первый маршрут и функция View](.\images\2025-03-18_21-22-09.png)

```python
# barbershop/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main), # Новый код
]
```

Функция View - это обычная функция Python, которая принимает объект запроса и возвращает объект ответа. В ответе мы можем вернуть HTML-страницу, JSON-данные, файл и многое другое.

```python
# core/views.py
def main(request):
    return HttpResponse("""
<h1>Barbershop</h1>
<p>Приветсвую путник. Ты находишься на сайте барбершопа. Здесь ты можешь записаться на стрижку, узнать цены и многое другое.</p>
""")
```

### Знакомство с конвертерами маршрутов

#### Int

Это похоже на аннотацию типов и переменную, прямо внутри маршрута!

Мы говорим Django, что ожидаем в этом месте целое число. Если в URL передано что-то другое, Django вернёт ошибку 404.

![Int](.\images\2025-03-18_21-49-27.png)

```python
path('masters/<int:master_id>/', master_detail),
```

```python
masters = [
    {"id": 1, "name": "Эльдар 'Бритва' Рязанов"},
    {"id": 2, "name": "Зоя 'Ножницы' Космодемьянская"},
    {"id": 3, "name": "Борис 'Фен' Пастернак"},
    {"id": 4, "name": "Иннокентий 'Лак' Смоктуновский"},
    {"id": 5, "name": "Раиса 'Бигуди' Горбачёва"},
]
```

Django вызовет функцию, которая отвечает за этот маршрут, и передаст ей объект запроса и значение master_id. Мы можем использовать это значение, чтобы найти нужного мастера в списке.

```python

def main(request):
    return HttpResponse("""
<h1>Barbershop</h1>
<p>Приветсвую путник. Ты находишься на сайте барбершопа. Здесь ты можешь записаться на стрижку, узнать цены и многое другое.</p>
""")

def master_detail(request, master_id):
    try:
        master = [m for m in masters if m['id'] == master_id][0]
    except IndexError:
        return HttpResponse("Мастера не найдено")
    return HttpResponse(f"<h1>{master['name']}</h1>")
```

### Папка Templates в корне проекта

Стандартные пути, по которым Django ищет шаблоны это все папки `templates` внутри КАЖДОГО приложения. Но мы можем добавить папку `templates` в корень проекта и Django будет искать шаблоны в ней.


```python
# barbershop/settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
...
```

Теперь можно сделать папку `templates` в корне проекта и создать в ней файл `thanks.html`.

`./templates/thanks.html`
```html
<h1>Спасибо!</h1>
<p>Ваша заявка принята.</p>
```

![Папка Templates в корне проекта](.\images\2025-03-18_22-23-24.png)


### Первая переменная шаблонизатора и контекст

Мы можем передать переменные в шаблон, чтобы использовать их в HTML-коде. Для этого в функции View возвращаем объект `render`, который принимает объект запроса, имя шаблона и словарь с переменными.

Контекст всегда должен быть словарем, даже если в нём всего одна переменная.

Переменная в шаблоне оформляется в двойные фигурные скобки `{{ переменная }}`.

А на уровне контекста это ключ словаря.

В нашем случае это `masters_count`.

![Первая переменная шаблонизатора и контекст](.\images\2025-03-18_23-52-41.png)

```python
# core/views.py
def thanks(request):
    masters_count = len(masters)

    context = {
        'masters_count': masters_count
    }

    return render(request, 'thanks.html', context)
```

`.templates/thanks.html`
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
  </head>
  <body>
    {% comment %} Коммент шаблонизатора {% endcomment %}
    <!-- Это тоже комментарий -->
    <h1>Спасибо!</h1>
    <p>
      Ваша заявка принята. Один из {{ masters_count }} мастеров будет рад вас
      принять в ближайшее время!
    </p>
  </body>
</html>
```

### Все типы конвертеров

`str` - принимает любую непустую строку, исключая символ '/'
`path('masters/<str:name>/', views.master_detail)   /masters/ivan-petrov/`

`int` - принимает положительные целые числа (0, 1, 2, ...)
`path('masters/<int:id>/', views.master_detail)   /masters/42/`

`slug` - буквы, цифры, дефисы и подчеркивания (для URL-friendly строк)
`path('articles/<slug:title>/', views.article)   /articles/novaya-pricheska-2024/`

`uuid` - принимает UUID строки (например, для уникальных идентификаторов)
` path('orders/<uuid:order_id>/', views.order)   /orders/123e4567-e89b-12d3-a456-426614174000/`

`path` - принимает любые непустые строки, включая символ '/'
`path('files/<path:file_path>/', views.download)   /files/2024/03/photo.jpg/`