from .data import MENU_ITEMS


def menu_context(request):
    """
    Контекстный процессор для передачи меню в контекст шаблона.
    Также добавляет информацию о текущем пользователе.
    """
    # Копируем базовое меню, чтобы не изменять оригинал
    menu = MENU_ITEMS.copy()

    # Если пользователь - сотрудник (is_staff), добавляем пункт "Список заказов"
    if request.user.is_authenticated and request.user.is_staff:
        menu.append({"name": "Список заказов", "url_name": "orders_list"})

    return {
        "menu_items": menu,
        "user": request.user,  # Добавляем пользователя в контекст
    }
