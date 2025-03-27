# Lesson 45 Фильтры и знакомство с наследованием

## Фильтры в шаблонизаторе Django

### Значение по-умолчанию
{{ user.bio|default:"О себе пока ничего не рассказал..." }}



```html
<img src="{{ user.avatar|default:'img/default_avatar.png' }}" alt="Аватар пользователя {{ user.username|default:'Аноним' }}">
```

### Обрезание текста 
{{ post.content|truncatewords:100 }}

### Форматирование даты и времени

В базе данных время хранится в формате UTC, а в шаблонах отображается в локальном формате.

Пример времени из БД - `2024-03-27 14:30:00`

Мы можем преобразовать это в человеко-читаемый формат, используя фильтр `date`
```html
{{ post.created_at|date:"d.m.Y H:i" }}
```

Пример вывода: 
```
27.03.2024 14:30
```

### Фильтр длина коллекции
```html
{{ post.comments|length }}
```

### Использование нескольких фильтров одновременно
```html
{{ post.content|truncatewords:100|default:"Пост пустой" }}
```

## Наследование шаблонов

Мы создаем "базовый" шаблон. Вы можете представить его как "шаблон для шаблона". Он содержит общие элементы, которые будут использоваться на всех страницах сайта.

- Подключение статики
- Подключение основных скриптов
- Подключение Bootstrap 5 

А дальше, мы сможем использовать систему наследования шаблонов Django. Это похоже на наследование классов в Python. Мы создаем базовый шаблон, а затем создаем дочерние шаблоны, которые наследуют от него.

Наш базовый шаблон будет выглядеть так:
```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <link rel="stylesheet" href="{% static 'css/test.css' %}" />
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
      crossorigin="anonymous"
    />
  </head>
  <body>
    <div class="container">
        {% comment %} Тут будет контекнт! {% endcomment %}
        {% block content %}
        {% endblock %}
        
    </div>
    <script
      src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
      integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
      crossorigin="anonymous"
    ></script>
    <script src="{% static 'js/test.js' %}"></script>
  </body>
</html>
```
### Создание дочернего шаблона

Теперь мы можем создать дочерний шаблон, который будет наследовать от базового. Например, создадим шаблон для страницы "О нас".

```html
{% extends 'base.html' %}

{% block content %}
<h1>О нас</h1>
<p>Мы - команда разработчиков, которые любят создавать крутые проекты!</p>
{% endblock %}
```

### Добавление блока для скриптов

Мы можем в базовом шаблоне сделать вот так:

```html
    <script
      src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
      integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
      crossorigin="anonymous"
    ></script>
    <script src="{% static 'js/test.js' %}"></script>
    {% block scripts %}
    {% endblock scripts %}
  </body>
</html>
```

А в дочернем шаблоне сделать вот так:
```html
{% block scripts %}

<script src="{% static 'js/order_detail.js' %}"></script>
{% endblock scripts %}
```

Главное не забыть загрузить статику, раз уж мы явно используем обращение к ней.
В этом варианте, у нас будет использованы скрипты из базового шаблона и дочернего.