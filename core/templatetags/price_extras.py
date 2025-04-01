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
    

# Мы можем сделать простой и инклюзивный тег для шаблонизатора
@register.simple_tag(name='format_name')
def format_name(name):
    """Форматирует имя, делая первую букву заглавной и добавляет перед именем Мастер"""
    if not name:
        return ""
    return f'Мастер {name.capitalize()}'


# Мы можем сделать простой тег с параметрами для position
@register.simple_tag(name='format_position')
def format_position(position, param1, param2):
    """Форматирует позицию, добавляя перед ней 'Должность:'"""
    if not position:
        return ""
    return f'Должность: {position.capitalize()} {param1} {param2}'



@register.inclusion_tag('core/employee_card.html', takes_context=True)
def employee_card(context, employee, card_type='standard'):
    """
    Инклюзивный тег для отображения карточки сотрудника.
    Принимает объект сотрудника и тип карточки.
    
    Пример использования:
    {% employee_card employee "vip" %}
        <p>Дополнительная информация о сотруднике</p>
    {% endemployee_card %}
    
    :param context: Контекст шаблона (автоматически передается Django)
    :param employee: Объект сотрудника с атрибутами (name, position, salary и т.д.)
    :param card_type: Тип карточки (standard, vip, compact)
    :return: Контекст для шаблона employee_card.html
    """
    # Получаем содержимое между тегами, если оно есть
    nodelist = context.get('nodelist', None)
    extra_content = nodelist.render(context) if nodelist else ''
    
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
        'extra_content': extra_content,
        'card_type': card_type
    }