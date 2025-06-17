# Урок 62: Магия Django Class-Based Views (CBV)

Django Class-Based Views (CBV) — это мощный инструмент, который позволяет писать более структурированный, переиспользуемый и расширяемый код для обработки веб-запросов по сравнению с традиционными Function-Based Views (FBV). Они предоставляют набор готовых классов, которые можно наследовать и настраивать, значительно ускоряя разработку и улучшая читаемость кода.

## 1. Базовая View (`django.views.View`)

Базовый класс `View` является основой для всех Class-Based Views в Django. Он не предоставляет никакой специфической функциональности, кроме диспетчеризации HTTP-методов. Это означает, что вы можете определить методы с именами HTTP-глаголов (например, `get()`, `post()`, `put()`, `delete()`), и Django автоматически вызовет соответствующий метод в зависимости от типа входящего запроса.

### Методы

*   **`get(self, request, *args, **kwargs)`**: Вызывается при получении GET-запроса.
*   **`post(self, request, *args, **kwargs)`**: Вызывается при получении POST-запроса.
*   **`put(self, request, *args, **kwargs)`**: Вызывается при получении PUT-запроса.
*   **`delete(self, request, *args, **kwargs)`**: Вызывается при получении DELETE-запроса.
*   **`dispatch(self, request, *args, **kwargs)`**: Это основной метод, который обрабатывает входящий запрос. Он определяет тип HTTP-метода и вызывает соответствующий метод (`get`, `post` и т.д.). Вы можете переопределить `dispatch` для добавления логики, которая должна выполняться независимо от HTTP-метода (например, проверки аутентификации или разрешений).

### Когда будет полезна?

Базовая `View` полезна, когда вам нужна полная гибкость и контроль над обработкой запросов, и вы не хотите использовать более специализированные CBV. Она идеально подходит для:

*   Создания API-эндпоинтов, где логика сильно зависит от HTTP-метода.
*   Обработки сложных форм, требующих различной логики для GET и POST.
*   Интеграции с внешними сервисами, где требуется специфическая обработка запросов.

### Пример из кода (`core/views.py`)

Рассмотрим `GreetingView`:

```python
# core/views.py
from django.views import View
from django.http import HttpResponse

class GreetingView(View):
    """
    Простое представление на основе базового класса View.
    Демонстрирует обработку GET и POST запросов.
    """
    greeting_get_message = "Привет, мир! Это GET запрос из GreetingView."
    greeting_post_message = "Вы успешно отправили POST запрос в GreetingView!"

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запросы.
        Возвращает простое HTTP-сообщение.
        """
        return HttpResponse(self.greeting_get_message)

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запросы.
        Возвращает простое HTTP-сообщение.
        """
        return HttpResponse(self.greeting_post_message)
```

В `core/urls.py` это представление привязано так:

```python
# core/urls.py
from django.urls import path
from .views import GreetingView

urlpatterns = [
    path("greeting/", GreetingView.as_view(), name="greeting"),
]
```

Метод `.as_view()` преобразует класс представления в вызываемую функцию, которую Django ожидает для URL-маршрутизации.

## 2. TemplateView (`django.views.generic.TemplateView`)

`TemplateView` — это специализированный CBV, предназначенный для отображения статических страниц или страниц, которые требуют минимальной логики для формирования контекста. Это отличная замена для простых Function-Based Views, которые просто рендерят шаблон.

### Атрибуты

*   **`template_name`**: **Обязательный** атрибут, указывающий имя шаблона, который будет отображен.
*   **`extra_context`**: Словарь, содержащий статические данные, которые будут добавлены в контекст шаблона.

### Расширяемые методы

*   **`get_context_data(self, **kwargs)`**: Метод для добавления динамического контекста в шаблон. Он должен возвращать словарь. Важно вызвать `super().get_context_data(**kwargs)`, чтобы получить базовый контекст от родительского класса.
*   **`get_template_names(self)`**: Позволяет динамически определять имя шаблона на основе логики. Если не переопределен, используется `template_name`.
*   **`dispatch(self, request, *args, **kwargs)`**: Как и в базовой `View`, может быть переопределен для выполнения логики до вызова `get()` (или других методов HTTP).

### Когда будет полезна?

*   Для страниц "О нас", "Контакты", "Политика конфиденциальности" и других статических страниц.
*   Для страниц, где контекст формируется из нескольких простых источников или не требует сложной логики запросов к БД.

### Примеры из кода (`core/views.py`)

#### Пример 1: Простой `TemplateView` (`SimplePageView`)

```python
# core/views.py
from django.views.generic import TemplateView

class SimplePageView(TemplateView):
    """
    Простейшее представление для отображения статической страницы.
    Использует атрибут template_name для указания шаблона.
    """
    template_name = "core/simple_page.html"
```

В `core/urls.py`:

```python
# core/urls.py
from django.urls import path
from .views import SimplePageView

urlpatterns = [
    path("simple-page/", SimplePageView.as_view(), name="simple_page"),
]
```

Это "View в 2 строки", так как все, что нужно, это указать имя шаблона.

#### Пример 2: `TemplateView` с дополнительным контекстом (`AboutUsView`)

```python
# core/views.py
from django.views.generic import TemplateView
import datetime # Импортируем datetime для динамического контекста

class AboutUsView(TemplateView):
    """
    Представление для страницы "О нас".
    Демонстрирует передачу как статического, так и динамического контекста в шаблон
    через переопределение метода get_context_data().
    """
    template_name = "core/about_us.html"

    def get_context_data(self, **kwargs):
        """
        Формирует и возвращает словарь контекста для шаблона.
        """
        context = super().get_context_data(**kwargs)
        
        context['company_name'] = "Барбершоп 'Арбуз'"
        context['start_year'] = 2010
        context['current_year'] = datetime.date.today().year
        context['years_on_market'] = datetime.date.today().year - context['start_year']
        context['page_title'] = "О нас - Барбершоп 'Арбуз'"
        context['contact_email'] = "contact@arbuz-barbershop.com"
        
        return context
```

В `core/urls.py`:

```python
# core/urls.py
from django.urls import path
from .views import AboutUsView

urlpatterns = [
    path("about-us/", AboutUsView.as_view(), name="about_us"),
]
```

Здесь `get_context_data` используется для добавления как статических (`company_name`), так и динамически вычисляемых (`years_on_market`) данных в контекст шаблона.

#### Пример 3: Переписывание существующего FBV на `TemplateView` (`ThanksView`)

Изначально `thanks` мог быть Function-Based View, но его переписали на `TemplateView` для лучшей структурированности:

```python
# core/views.py
from django.views.generic import TemplateView
from django.db.models import Count # Для masters_count
from .models import Master # Для masters_count

class ThanksView(TemplateView):
    template_name = "core/thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        masters_count = Master.objects.filter(is_active=True).count()
        context["masters_count"] = masters_count
        context["additional_message"] = "Спасибо, что выбрали наш первоклассный сервис!"
        
        if 'source' in kwargs:
            source_page = kwargs['source']
            if source_page == 'order':
                context['source_message'] = "Ваш заказ успешно создан и принят в обработку."
            elif source_page == 'review':
                context['source_message'] = "Ваш отзыв успешно отправлен и будет опубликован после модерации."
            else:
                context['source_message'] = f"Благодарим вас за ваше действие, инициированное со страницы: {source_page}."
        else:
            context['source_message'] = "Благодарим вас за посещение!"
            
        return context
```

В `core/urls.py`:

```python
# core/urls.py
from django.urls import path
from .views import ThanksView

urlpatterns = [
    path("thanks/", ThanksView.as_view(), name="thanks"),
    path("thanks/<str:source>/", ThanksView.as_view(), name="thanks_with_source"),
]
```

Здесь `get_context_data` также используется для добавления динамических данных (количество активных мастеров) и обработки параметров URL (`source`).

## 3. DetailView (`django.views.generic.DetailView`)

`DetailView` предназначен для отображения детальной информации об одном конкретном объекте из базы данных. Он автоматически извлекает объект на основе первичного ключа (PK) или slug, переданного в URL.

### Атрибуты

*   **`model`**: **Обязательный** атрибут, указывающий модель, из которой будет извлекаться объект.
*   **`template_name`**: Имя шаблона для отображения. Если не указано, Django по умолчанию ищет шаблон по пути `<app_label>/<model_name_lowercase>_detail.html` (например, `core/order_detail.html`).
*   **`pk_url_kwarg`**: Имя именованного аргумента URL, который содержит первичный ключ объекта. По умолчанию `'pk'`. Если в URL используется другое имя (например, `order_id`), его нужно указать здесь.
*   **`slug_url_kwarg`**: Имя именованного аргумента URL, который содержит slug объекта. По умолчанию `'slug'`.
*   **`slug_field`**: Имя поля модели, которое содержит slug. По умолчанию `'slug'`.
*   **`context_object_name`**: Имя переменной, под которой объект будет доступен в контексте шаблона. По умолчанию это имя модели в нижнем регистре (например, `order` для модели `Order`).
*   **`extra_context`**: Словарь со статическими данными для добавления в контекст.

### Методы

*   **`get_queryset(self)`**: Возвращает QuerySet, из которого будет извлекаться объект. Полезно для добавления фильтрации, `select_related` или `prefetch_related` для оптимизации запросов.
*   **`get_object(self, queryset=None)`**: Возвращает конкретный объект для отображения. Если нужно изменить логику получения объекта (например, получить его не по PK/slug, а по другим параметрам), можно переопределить этот метод.
*   **`get_context_data(self, **kwargs)`**: Возвращает контекст для шаблона. Используется для добавления дополнительных данных, не связанных напрямую с основным объектом.

### Защита представлений

#### Как защитить от неавторизованных пользователей?

Используйте `LoginRequiredMixin` из `django.contrib.auth.mixins`. Этот миксин перенаправит неавторизованных пользователей на страницу входа.

```python
# core/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from .models import Order

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "core/order_detail.html"
    pk_url_kwarg = "order_id"  # Указываем, что pk будет извлекаться из order_id в URL
```

#### Как защитить от НЕ `is_staff`?

Есть два основных варианта:

1.  **Использовать `UserPassesTestMixin`**: Этот миксин позволяет определить метод `test_func()`, который возвращает `True` или `False`. Если `False`, вызывается `handle_no_permission()`.

    ```python
    # core/views.py
    from django.contrib.auth.mixins import UserPassesTestMixin
    from django.shortcuts import redirect
    from django.contrib import messages

    class StaffRequiredMixin(UserPassesTestMixin):
        """
        Миксин для проверки, является ли пользователь сотрудником (is_staff).
        Если проверка не пройдена, пользователь перенаправляется на главную страницу
        с сообщением об ошибке.
        """
        def test_func(self):
            # Проверяем, аутентифицирован ли пользователь и является ли он сотрудником
            return self.request.user.is_authenticated and self.request.user.is_staff

        def handle_no_permission(self):
            # Этот метод вызывается, если test_func вернул False
            messages.error(self.request, "У вас нет доступа к этому разделу.")
            return redirect("landing") # Предполагаем, что 'landing' - это имя URL главной страницы
    ```

    Затем вы можете использовать этот миксин в своих CBV:

    ```python
    # core/views.py
    class OrderDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
        model = Order
        template_name = "core/order_detail.html"
        pk_url_kwarg = "order_id"
    ```

2.  **Переопределить метод `dispatch`**: Вы можете добавить логику проверки прямо в метод `dispatch` вашего представления.

    ```python
    # core/views.py
    from django.contrib.auth.mixins import LoginRequiredMixin
    from django.views.generic import DetailView
    from django.shortcuts import redirect
    from django.contrib import messages
    # from django.http import Http403 # Можно импортировать для Http403

    class OrderDetailView(LoginRequiredMixin, DetailView):
        model = Order
        template_name = "core/order_detail.html"
        pk_url_kwarg = "order_id"

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

### Примеры из кода (`core/views.py`)

#### `OrderDetailView`

```python
# core/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from .models import Order
from django.shortcuts import redirect
from django.contrib import messages

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "core/order_detail.html"
    pk_url_kwarg = "order_id"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "У вас нет доступа к этой странице.")
            return redirect("landing") 
        return super().dispatch(request, *args, **kwargs)
```

В `core/urls.py`:

```python
# core/urls.py
from django.urls import path
from .views import OrderDetailView

urlpatterns = [
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order_detail"),
]
```

Здесь `pk_url_kwarg` явно указывает, что первичный ключ будет извлекаться из параметра `order_id` в URL. Метод `dispatch` используется для проверки прав доступа пользователя (`is_staff`).

#### `ServiceDetailView`

```python
# core/views.py
from django.views.generic import DetailView
from .models import Service

class ServiceDetailView(DetailView):
    """
    Представление для отображения детальной информации об услуге.
    Использует модель Service и явно указанное имя шаблона.
    В шаблон будет передан объект service (имя по умолчанию для контекстной переменной).
    """
    model = Service
    template_name = 'core/service_detail.html'
```

В `core/urls.py`:

```python
# core/urls.py
from django.urls import path
from .views import ServiceDetailView

urlpatterns = [
    path("service/<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),
]
```

Здесь используется стандартное имя параметра `pk` в URL, поэтому `pk_url_kwarg` не требуется.

## 4. ListView (`django.views.generic.ListView`)

`ListView` предназначен для отображения списка объектов из базы данных. Он предоставляет функциональность для получения QuerySet, пагинации и добавления контекста.

### Атрибуты

*   **`model`**: **Обязательный** атрибут, указывающий модель, объекты которой будут отображаться.
*   **`queryset`**: Можно явно указать QuerySet вместо `model`. Если указан, `model` игнорируется.
*   **`template_name`**: Имя шаблона для отображения. По умолчанию Django ищет шаблон по пути `<app_label>/<model_name_lowercase>_list.html` (например, `core/order_list.html`).
*   **`context_object_name`**: Имя переменной, под которой список объектов будет доступен в контексте шаблона. По умолчанию это `object_list`.
*   **`paginate_by`**: Целое число, указывающее количество объектов на страницу для пагинации.
*   **`ordering`**: Список строк или кортеж, указывающий порядок сортировки QuerySet. Например, `['name', '-price']`.
*   **`extra_context`**: Словарь со статическими данными для добавления в контекст.

### Методы

*   **`get_queryset(self)`**: Возвращает QuerySet объектов для отображения. Это наиболее часто переопределяемый метод для добавления фильтрации, поиска, сортировки или оптимизации запросов (`select_related`, `prefetch_related`).
*   **`get_context_data(self, **kwargs)`**: Возвращает контекст для шаблона. Используется для добавления дополнительных данных, не связанных напрямую со списком объектов (например, заголовки, счетчики).

### Примеры из кода (`core/views.py`)

#### `ServicesListView`

Это представление заменяет Function-Based View `services_list`.

```python
# core/views.py
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView
from .models import Service
from django.shortcuts import redirect
from django.contrib import messages

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет доступа к этому разделу.")
        return redirect("landing")

class ServicesListView(StaffRequiredMixin, ListView):
    model = Service
    template_name = "core/services_list.html"
    context_object_name = "services"
    extra_context = {
        "title": "Управление услугами",
    }
```

В `core/urls.py`:

```python
# core/urls.py
from django.urls import path
from .views import ServicesListView

urlpatterns = [
    path("services/", ServicesListView.as_view(), name="services_list"),
]
```

Здесь используется `StaffRequiredMixin` для ограничения доступа только для сотрудников. `context_object_name` установлен в `'services'`, чтобы в шаблоне можно было обращаться к списку как `{{ services }}`. `extra_context` добавляет статический заголовок.

#### `OrdersListView`

Это представление заменяет Function-Based View `orders_list` и включает сложную логику поиска и фильтрации.

```python
# core/views.py
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView
from .models import Order, Master, Service # Убедитесь, что все модели импортированы
from django.db.models import Q, F # Для Q-объектов и F-выражений
from django.shortcuts import redirect
from django.contrib import messages

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет доступа к этому разделу.")
        return redirect("landing")

class OrdersListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "core/orders_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        """
        Переопределяем метод get_queryset для получения всех заказов с жадной загрузкой мастеров и услуг.
        А так же обработкой всех вариантов фильтрации и поиска.
        """
        all_orders = (
            Order.objects.select_related("master").prefetch_related("services").all()
        )

        search_query = self.request.GET.get("search", None)

        if search_query:
            check_boxes = self.request.GET.getlist("search_in")
            filters = Q()

            if "phone" in check_boxes:
                filters |= Q(phone__icontains=search_query)
            if "name" in check_boxes:
                filters |= Q(client_name__icontains=search_query)
            if "comment" in check_boxes:
                filters |= Q(comment__icontains=search_query)

            if filters:
                all_orders = all_orders.filter(filters)

        return all_orders
```

В `core/urls.py`:

```python
# core/urls.py
from django.urls import path
from .views import OrdersListView

urlpatterns = [
    path("orders/", OrdersListView.as_view(), name="orders_list"),
]
```

Здесь `get_queryset` переопределен для реализации логики поиска и фильтрации, которая ранее была в Function-Based View. Используются `select_related` и `prefetch_related` для оптимизации запросов к базе данных, что является хорошей практикой при работе со связанными объектами.

## Заключение

Class-Based Views в Django предоставляют мощный и гибкий способ организации логики представлений. Используя базовые `View`, `TemplateView`, `DetailView` и `ListView`, а также различные миксины, разработчики могут создавать чистый, переиспользуемый и легко поддерживаемый код. Понимание их атрибутов и методов позволяет эффективно настраивать поведение представлений под конкретные нужды проекта, значительно повышая продуктивность разработки.
