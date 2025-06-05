# Урок 62: Магия Django Class-Based Views (CBV)

## Базовая View

- Методы `get`, `post`, `put`, `delete` и т.д. в классе представления.
- Метод `get` вызывается при GET-запросе, `post` — при POST-запросе и т.д.
- При необходимости можно переопределить методы `dispatch`

Когда будет полезна?

## TemplateView

- Используется для отображения статических страниц.
- Атрибуты:
  - `template_name`: имя шаблона для отображения.
  - `extra_context`: дополнительный контекст, передаваемый в шаблон.

Расширяются методы
- `get_context_data`: для добавления дополнительного контекста в шаблон.
- `get_template_names`: для указания имени шаблона.
- `dispatch`: для обработки запросов.

## DetailView

- template_name: имя шаблона для отображения.
- pk_url_kwarg: альтернативный ключ для извлечения объекта из базы данных.
- slug_url_kwarg: альтернативный ключ для извлечения объекта по slug.
- model: модель, из которой извлекается объект.
- context_object_name: имя объекта в контексте шаблона.
- extra_context: дополнительный контекст, передаваемый в шаблон.


Методы
- get_queryset: возвращает набор объектов для отображения. Тут можно переопределить запрос к базе, добавить фильтрацию или или select_related.
- get_object: возвращает конкретный объект для отображения из queryset. Тут можно переопределить логику получения объекта.
- get_context_data: возвращает контекст для шаблона. Тут можно добавить дополнительные данные в контекст.


```python
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "core/order_detail.html"
    pk_url_kwarg = "order_id"  # Указываем, что pk будет извлекаться из order_id в URL
```

Как защитить от неавторизованных пользователей?
- Использовать `LoginRequiredMixin` для защиты представления от неавторизованных пользователей.

Как защитить от НЕ `is_staff`?
- Классический вариант - `UserPassesTestMixin` для проверки, является ли пользователь `is_staff`.
- Второй вариант - расширить `dispatch` и добавить проверку на `is_staff`.


```python
    def dispatch(self, request, *args, **kwargs):
    # Сначала проверяем, аутентифицирован ли пользователь (это делает LoginRequiredMixin,
    # но если бы его не было, проверка была бы здесь: if not request.user.is_authenticated:)
    # Затем проверяем, является ли пользователь сотрудником
        if not request.user.is_staff:
            messages.error(request, "У вас нет доступа к этой странице.")
            return redirect("landing") 
            # Или можно было бы вызвать Http403: from django.http import Http403; raise Http403("Доступ запрещен")
        
        # Если все проверки пройдены, вызываем родительский метод dispatch,
        # который уже вызовет get(), post() и т.д.
        return super().dispatch(request, *args, **kwargs)
```