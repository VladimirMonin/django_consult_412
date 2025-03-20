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