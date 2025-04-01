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