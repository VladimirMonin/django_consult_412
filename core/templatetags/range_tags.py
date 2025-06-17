from django import template

register = template.Library()

@register.filter
def to_range(value):
    """
    Фильтр для создания диапазона чисел в шаблоне.
    Использование: {{ 5|to_range }}
    """
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)
