# Lesson 46. Контекстные процессоры. Собственные фильтры и теги шаблона. Переменные User, Requst, Система Messages

## Контекстные процессоры

Контекстные процессоры - это функции, которые возвращают словарь, добавляющий переменные в контекст шаблона. Они позволяют передавать данные во все шаблоны проекта без необходимости добавлять их в каждое представление.

Определили в Джанго приложении `core` файл `context_processors.py`, в котором создали функцию `menu_context`, возвращающую список словарей с названиями и URL-адресами пунктов меню. Затем добавили этот процессор в настройки проекта, чтобы он был доступен во всех шаблонах.

## Собственные фильтры шаблона

Фильтры шаблона - это функции, которые принимают значение и возвращают его в измененном виде. Они позволяют форматировать данные перед их отображением в шаблонах.

Нам надо обязательно создать пакет `templatetags` в приложении `core`, чтобы иметь возможность использовать собственные фильтры и теги. В этом пакете создаем файл `__init__.py`, чтобы он стал пакетом, и файл `price_extras.py`, в котором определяем собственные фильтры.

Код фильтра `price_extras.py`:

```python
from django import template

register = template.Library()

@register.filter(name='format_price')
def format_price(value, currency='₽'):
    """Форматирует цену добавляя знак рубля"""
    # Преобразуем значение в число, если оно пришло строкой
    try:
        numeric_value = float(value)
        formatted_number = '{:,.0f}'.format(numeric_value).replace(',', ' ')
        # Добавляем символ рубля
        return f"{formatted_number} {currency}"
    except (ValueError, TypeError):
        # Если не удалось преобразовать в число, возвращаем исходное значение
        return value
```

Пример использования фильтра в шаблоне:

```html
{{ price|format_price }}

Или с параметром:

{{ price|format_price:"$" }}
```

## Собственные теги шаблона
Теги шаблона - это функции, которые могут выполнять более сложные операции, чем фильтры. Они могут принимать аргументы и возвращать HTML-код.

Есть простые теги, которые возвращают значение, и сложные теги, которые могут включать другие шаблоны.

Начнем с простого тега, который принимает position а так же param1 и param2 и возвращает форматированное значение:

```python
@register.simple_tag(name='format_position')
def format_position(position, param1, param2):
    """Форматирует позицию, добавляя перед ней 'Должность:'"""
    if not position:
        return ""
    return f'Должность: {position.capitalize()} {param1} {param2}'
```

Пример использования тега в шаблоне:

```html
{% load price_extras %}
<p>Должность через тег: {% format_position employee.position "параметр1" "параметр2" %}</p>
```

## Собственный инклюзивный тег

Инклюзивные теги позволяют включать другие шаблоны и передавать им контекст. Это полезно для создания повторяющихся элементов интерфейса.
Пример инклюзивного тега, который включает шаблон карточки мастера:

```python
@register.inclusion_tag('core/employee_card.html')
def employee_card(employee, card_type='standard'):
    """
    Инклюзивный тег для отображения карточки сотрудника.
    Принимает объект сотрудника и тип карточки.
    
    Пример использования:
    {% employee_card employee "vip" %}
    
    :param employee: Объект сотрудника с атрибутами (name, position, salary и т.д.)
    :param card_type: Тип карточки (standard, vip, compact)
    :return: Контекст для шаблона employee_card.html
    """
    # Определяем CSS-класс в зависимости от типа карточки
    css_class = 'card-standard'
    if card_type == 'vip':
        css_class = 'card-vip'
    elif card_type == 'compact':
        css_class = 'card-compact'
    
    # Определяем статус занятости для отображения
    status_text = 'Работает' if employee.is_active else 'Не работает'
    status_class = 'text-success' if employee.is_active else 'text-danger'
    
    # Создаем контекст для шаблона
    return {
        'employee': employee,
        'css_class': css_class,
        'status_text': status_text,
        'status_class': status_class,
        'card_type': card_type
    }
```

Пример шаблона сделанного под инклюзивный тег `employee_card.html`:

```html
{% load price_extras %}
<div class="employee-card {{ css_class }}">
    <div class="card mb-3">
        <div class="card-header d-flex justify-content-between">
            <h5 class="card-title">{% format_name employee.name %}</h5>
            <span class="badge {{ status_class }}">{{ status_text }}</span>
        </div>
        <div class="card-body">
            {% if card_type == 'vip' %}
                <div class="vip-badge">⭐ ВИП-мастер ⭐</div>
            {% endif %}
            
            <p class="card-text">
                {% if employee.position == "manager" %}
                <span class="yellow-position">Менеджер барбершопа</span>
                {% elif employee.position == "master" %}
                <span class="blue-position">Мастер барбершопа</span>
                {% else %}
                <span>{{ employee.position }}</span>
                {% endif %}
            </p>
            
            <p class="card-text">Зарплата: {{ employee.salary|format_price }}</p>
            
            {% if employee.hobbies %}
            <p class="card-text">
                <small class="text-muted">Увлечения: 
                    {% for hobby in employee.hobbies %}
                        {% if not forloop.first %}, {% endif %}
                        {{ hobby }}
                    {% endfor %}
                </small>
            </p>
            {% endif %}
            
            {% if extra_content %}
            <div class="extra-content mt-3 border-top pt-3">
                {{ extra_content|safe }}
            </div>
            {% endif %}
        </div>
        
        {% if card_type != 'compact' %}
        <div class="card-footer text-end">
            <button class="btn btn-sm btn-dark">Записаться к мастеру</button>
        </div>
        {% endif %}
    </div>
</div>
```

А так же стили для карточки мастера:

```css

/* Можно добавить в static/css/test.css */
.employee-card .card {
    transition: transform 0.3s ease;
}

.employee-card .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.card-vip {
    border: 2px solid gold;
}

.card-vip .card-header {
    background-color: #ffd700;
    color: #333;
}

.vip-badge {
    text-align: center;
    font-weight: bold;
    color: #d4af37;
    margin-bottom: 10px;
}

.card-compact .card-body {
    padding: 0.5rem;
}
```

Смысл инклюзивного тега в том, что он позволяет использовать один и тот же шаблон для разных типов карточек, передавая ему разные параметры. Это упрощает поддержку кода и делает его более читаемым.