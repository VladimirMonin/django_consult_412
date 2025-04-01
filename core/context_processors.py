from .data import MENU_ITEMS

def menu_context(request):
    """
    Контекстный процессор для передачи меню в контекст шаблона.
    """
    return {
        'menu_items': MENU_ITEMS
    }