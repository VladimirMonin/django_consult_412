from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from .data import *
from django.contrib.auth.decorators import login_required
from .models import Order, Master, Service, Review
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Prefetch
from django.views import View  # Импортируем базовый View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# messages - это встроенный модуль Django для отображения сообщений пользователю
from django.contrib import messages
from .forms import ServiceForm, OrderForm, ReviewForm, ServiceEasyForm
import json

# Импорт LoginRequiredMixin для использования в CBV
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class LandingPageView(TemplateView):
    template_name = "core/landing.html"
    extra_context = {
        "title": "Главная - Барбершоп Арбуз",
        "years_on_market": 50,
        "masters": Master.objects.all(),
        "services": Service.objects.all(),
    }



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
        return redirect(
            "landing"
        )  # Предполагаем, что 'landing' - это имя URL главной страницы


class ServicesListView(StaffRequiredMixin, ListView):
    model = Service
    template_name = "core/services_list.html"
    context_object_name = "services"
    extra_context = {
        "title": "Управление услугами",
    }

class MasterDetailView(DetailView):
    model = Master
    template_name = "core/master_detail.html"
    context_object_name = "master"

    def get_queryset(self):
        """
        Переопределяем queryset, чтобы сразу включить жадную загрузку
        связанных услуг и опубликованных отзывов.
        Это решает проблему N+1 запросов.
        """
        # prefetch_related - для Many-to-Many и обратных ForeignKey связей
        return Master.objects.prefetch_related(
            'services', 
            # Мы можем даже фильтровать предзагруженные данные
            Prefetch('reviews', queryset=Review.objects.filter(is_published=True).order_by("-created_at"))
        )

    def get_object(self, queryset=None):
        """
        Получаем объект и обновляем счетчик просмотров.
        """
        # super().get_object() вызовет .get(pk=...) на нашем get_queryset()
        master = super().get_object(queryset)
        
        master_id = master.id
        viewed_masters = self.request.session.get("viewed_masters", [])

        if master_id not in viewed_masters:
            # Используем F-выражение для атомарного увеличения счетчика
            Master.objects.filter(id=master_id).update(view_count=F("view_count") + 1)
            
            viewed_masters.append(master_id)
            self.request.session["viewed_masters"] = viewed_masters
            
            # Обновляем счетчик в текущем объекте, чтобы он сразу отобразился в шаблоне
            master.view_count += 1
            # master.refresh_from_db() больше не нужен, если мы обновляем поле вручную

        return master

    def get_context_data(self, **kwargs):
        """
        Добавляем связанные данные в контекст.
        Теперь они уже загружены и не вызывают новых запросов к БД.
        """
        context = super().get_context_data(**kwargs)
        # self.object - это наш 'master', уже со всеми предзагруженными данными
        # Обратите внимание, что reviews уже отфильтрованы в get_queryset
        context['reviews'] = self.object.reviews.all()
        context['services'] = self.object.services.all()
        context['title'] = f"Мастер {self.object.first_name} {self.object.last_name}"
        return context






class ThanksView(TemplateView):  # Существующий класс, дорабатываем его
    template_name = "core/thanks.html"

    def get_context_data(self, **kwargs):
        """
        Формирует и возвращает словарь контекста для шаблона "Спасибо".
        Добавляет количество активных мастеров, дополнительное сообщение
        и обрабатывает параметр 'source' из URL.
        """
        context = super().get_context_data(**kwargs)

        # Получаем количество активных мастеров из базы данных
        # Это полезная информация, которую можно отобразить на странице благодарности.
        masters_count = Master.objects.filter(is_active=True).count()
        context["masters_count"] = masters_count

        # Добавим новый статический элемент в контекст для демонстрации
        context["additional_message"] = "Спасибо, что выбрали наш первоклассный сервис!"

        # Проверим, передан ли параметр 'source' в URL.
        # kwargs содержит именованные аргументы, захваченные из URL-шаблона.
        # Например, если URL /thanks/order/, то kwargs будет {'source': 'order'}
        if "source" in kwargs:
            source_page = kwargs["source"]
            if source_page == "order":
                context["source_message"] = (
                    "Ваш заказ успешно создан и принят в обработку."
                )
            elif source_page == "review":
                context["source_message"] = (
                    "Ваш отзыв успешно отправлен и будет опубликован после модерации."
                )
            else:
                # Общий случай, если источник не 'order' и не 'review'
                context["source_message"] = (
                    f"Благодарим вас за ваше действие, инициированное со страницы: {source_page}."
                )
        else:
            # Если параметр 'source' не передан
            context["source_message"] = "Благодарим вас за посещение!"

        return context



class OrdersListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "core/orders_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        """
        Переопределяем метод get_queryset для получения всех заказов с жадной загрузкой мастеров и услуг.
        А так же обработкой всех вариантов фильтрации и поиска.
        """
        # Получаем все заказы
        # Используем жадную загрузку для мастеров и услуг
        all_orders = (
            Order.objects.select_related("master").prefetch_related("services").all()
        )

        # Получаем строку поиска
        search_query = self.request.GET.get("search", None)

        if search_query:
            # Получаем чекбоксы
            check_boxes = self.request.GET.getlist("search_in")

            # Проверяем Чекбоксы и добавляем Q объекты в запрос
            # |= это оператор "или" для Q объектов
            filters = Q()

            if "phone" in check_boxes:
                # Полная запись где мы увеличиваем фильтры
                filters = filters | Q(phone__icontains=search_query)

            if "name" in check_boxes:
                # Сокращенная запись через inplace оператор
                filters |= Q(client_name__icontains=search_query)

            if "comment" in check_boxes:
                filters |= Q(comment__icontains=search_query)

            if filters:
                # Если фильтры появились. Если Q остался пустым, мы не попадем сюда
                all_orders = all_orders.filter(filters)

        # Возвращаем отфильтрованный QuerySet
        return all_orders


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "core/order_detail.html"
    pk_url_kwarg = "order_id"  # Указываем, что pk будет извлекаться из order_id в URL

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


class ServiceUpdateView(UpdateView):
    form_class = ServiceForm
    model = Service
    template_name = "core/service_form.html"
    success_url = reverse_lazy("services_list")
    extra_context = {
        "button_txt": "Обновить",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f'Редактирование услуги: {self.object.name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f"Услуга '{form.cleaned_data['name']}' успешно обновлена!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Ошибка формы: проверьте ввод данных.")
        return super().form_invalid(form)


class ServiceCreateView(CreateView):
    """
    Вью для создания услуги.
    service_create/<str:form_mode>
    Через метод get_form_class выбираем форму в зависимости от параметра form_mode
    """
    form_class = ServiceForm
    template_name = "core/service_form.html"
    success_url = reverse_lazy("services_list")
    extra_context = {
        "title": "Создание услуги",
        "button_txt": "Создать",
    }

    def form_valid(self, form):
        """
        Метод вызывается, когда форма валидна
        form: Django помещает в эту переменную данные из формы
        """
        messages.success(self.request, f"Услуга '{form.cleaned_data['name']}' успешно создана!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Ошибка формы: проверьте ввод данных.")
        return super().form_invalid(form)
    
    def get_form_class(self):
        """
        Обрабатывает параметр form_mode в URL и возвращает нужную форму
        2 варианта: "normal" и "easy"
        """
        form_mode = self.kwargs.get("form_mode")
        if form_mode == "normal":
            return ServiceForm
        
        elif form_mode == "easy":
            return ServiceEasyForm

class MastersServicesAjaxView(View):
    def get(self, request, *args, **kwargs):
        master_id = request.GET.get("master_id")
        return self.get_services_json_response(master_id)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        master_id = data.get("master_id")
        return self.get_services_json_response(master_id)

    def get_services_json_response(self, master_id):
        if not master_id:
            return JsonResponse({"error": "master_id is required"}, status=400)

        master = get_object_or_404(Master, id=master_id)
        services = master.services.all()
        response_data = [{"id": service.id, "name": service.name} for service in services]
        return JsonResponse(response_data, safe=False)

class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = "core/order_form.html"
    
    def get_success_url(self):
        return reverse_lazy("thanks_with_source", kwargs={"source": "order"})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создание заказа"
        context["button_text"] = "Создать"
        return context

    def form_valid(self, form):
        client_name = form.cleaned_data.get("client_name")
        messages.success(self.request, f"Заказ для {client_name} успешно создан!")
        return super().form_valid(form)


class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "core/review_form.html"

    def get_success_url(self):
        return reverse_lazy("thanks_with_source", kwargs={"source": "review"})

    def get_initial(self):
        initial = super().get_initial()
        master_id = self.request.GET.get("master_id")
        if master_id:
            try:
                initial["master"] = Master.objects.get(pk=master_id)
            except Master.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Оставить отзыв"
        context["button_text"] = "Отправить"
        return context

    def form_valid(self, form):
        review = form.save(commit=False)
        review.is_published = False
        review.save()
        
        messages.success(
            self.request,
            "Ваш отзыв успешно добавлен! Он будет опубликован после проверки модератором.",
        )
        return redirect(self.get_success_url())

class MasterInfoAjaxView(View):
    def get(self, request, *args, **kwargs):
        if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": "Недопустимый запрос"}, status=400)

        master_id = request.GET.get("master_id")
        if not master_id:
            return JsonResponse({"success": False, "error": "Не указан ID мастера"}, status=400)

        try:
            master = Master.objects.get(pk=master_id)
            master_data = {
                "id": master.id,
                "name": f"{master.first_name} {master.last_name}",
                "experience": master.experience,
                "photo": master.photo.url if master.photo else None,
                "services": list(master.services.values("id", "name", "price")),
            }
            return JsonResponse({"success": True, "master": master_data})
        except Master.DoesNotExist:
            return JsonResponse({"success": False, "error": "Мастер не найден"}, status=404)


# --- Этап 1: Базовые CBV ---
# 1. GreetingView на основе django.views.View
class GreetingView(View):
    """
    Простое представление на основе базового класса View.
    Демонстрирует обработку GET и POST запросов.
    """

    # Сообщения для разных типов запросов
    greeting_get_message = "Привет, мир! Это GET запрос из GreetingView."
    greeting_post_message = "Вы успешно отправили POST запрос в GreetingView!"

    # Атрибут http_method_names определяет, какие HTTP-методы разрешены для этого View.
    # По умолчанию он включает 'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'.
    # Мы можем его переопределить, если хотим ограничить поддерживаемые методы.
    # http_method_names = ['get', 'post'] # В данном случае это избыточно, т.к. мы реализуем get и post

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запросы.
        Возвращает простое HTTP-сообщение.
        """
        # request - это объект HttpRequest
        # args и kwargs - это позиционные и именованные аргументы, захваченные из URL
        return HttpResponse(self.greeting_get_message)

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запросы.
        Возвращает простое HTTP-сообщение.
        """
        # Здесь могла бы быть логика обработки данных из POST-запроса,
        # например, сохранение данных формы.
        return HttpResponse(self.greeting_post_message)


# 2. TemplateView - Отображение шаблонов с контекстом


# Пример 1: Простой TemplateView ("View в 2 строки")
class SimplePageView(TemplateView):
    """
    Простейшее представление для отображения статической страницы.
    Использует атрибут template_name для указания шаблона.
    """

    template_name = "core/simple_page.html"
    # Для этого View не требуется передавать дополнительный контекст,
    # поэтому метод get_context_data() не переопределяется.


# Пример 2: TemplateView с дополнительным контекстом
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
        # Сначала получаем базовый контекст от родительского класса (TemplateView).
        # Это важно, так как родительский класс может добавлять в контекст полезные данные,
        # например, экземпляр самого View (`view`).
        context = super().get_context_data(**kwargs)

        # Добавляем наши собственные данные в контекст.
        # Эти данные будут доступны в шаблоне по указанным ключам.
        context["company_name"] = "Барбершоп 'Арбуз'"
        context["start_year"] = 2010
        # Динамически вычисляем текущий год и количество лет на рынке.
        # Для этого импортируем модуль datetime.
        import datetime  # Лучше импортировать в начале файла, но для примера здесь

        context["current_year"] = datetime.date.today().year
        context["years_on_market"] = datetime.date.today().year - context["start_year"]
        context["page_title"] = "О нас - Барбершоп 'Арбуз'"
        context["contact_email"] = "contact@arbuz-barbershop.com"

        # Возвращаем обновленный словарь контекста.
        return context


class ServiceDetailView(DetailView):
    """
    Представление для отображения детальной информации об услуге.
    Использует модель Service и явно указанное имя шаблона.
    В шаблон будет передан объект service (имя по умолчанию для контекстной переменной).
    """

    model = Service  # Указываем, какую модель мы хотим отобразить
    template_name = "core/service_detail.html"  # Указываем шаблон

    # Если template_name не указать, Django будет искать:
    # 'core/service_detail.html' (т.е. <app_label>/<model_name_lowercase>_detail.html)


# --- Этап 2: Работа со списками и отдельными объектами - ListView и DetailView ---

# 3. ListView - Отображение списков объектов


# Пример 1: Базовый ServiceListView
class ServiceListView(ListView):
    """
    Базовое представление для отображения списка всех услуг.
    Использует модель Service и явно указанное имя шаблона.
    В шаблон будет передан object_list (имя по умолчанию для контекстной переменной списка).
    """

    model = Service  # Указываем, какую модель мы хотим отобразить
    template_name = "core/service_list_cbv.html"
    # Если template_name не указать, Django будет искать:
    # 'core/service_list.html' (т.е. <app_label>/<model_name_lowercase>_list.html)


# Пример 2: Кастомизированный ServiceListViewAdvanced
class ServiceListViewAdvanced(ListView):
    """
    Расширенное представление для отображения списка услуг с кастомизацией:
    - Показывает только популярные услуги, отсортированные по цене (через get_queryset).
    - Использует кастомное имя для списка объектов в контексте ('services') через context_object_name.
    - Включает пагинацию (3 объекта на страницу) через paginate_by.
    - Добавляет дополнительную информацию в контекст (через get_context_data).
    """

    model = Service  # Указываем модель
    template_name = "core/service_list_advanced_cbv.html"  # Указываем шаблон
    context_object_name = "services"  # Имя переменной в шаблоне будет {{ services }} вместо {{ object_list }}
    paginate_by = 3  # Количество объектов на странице для пагинации
    # ordering = ['name'] # Можно было бы задать сортировку по умолчанию здесь, но мы ее переопределим в get_queryset

    def get_queryset(self):
        """
        Возвращает QuerySet только для популярных услуг, отсортированных по цене.
        Этот метод переопределяет стандартное поведение (которое было бы Service.objects.all()).
        """
        # Мы хотим показать только те услуги, у которых поле is_popular=True,
        # и отсортировать их по полю price.
        queryset = Service.objects.filter(is_popular=True).order_by("price")
        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительную информацию в контекст шаблона.
        """
        # Сначала получаем базовый контекст от родительского ListView.
        # Он уже будет содержать:
        # - 'services' (так как мы указали context_object_name)
        # - 'paginator' (объект Paginator)
        # - 'page_obj' (объект Page, представляющий текущую страницу)
        # - 'is_paginated' (True, если включена пагинация и объектов больше, чем на одной странице)
        context = super().get_context_data(**kwargs)

        # Добавляем свои кастомные данные в контекст
        context["page_title"] = "Наши самые популярные и выгодные услуги"

        # Общее количество всех услуг в системе (для справки)
        context["total_services_in_system"] = Service.objects.count()

        # Количество услуг, которые фактически отображаются (т.е. популярных)
        # self.get_queryset() вернет отфильтрованный queryset (популярные, отсортированные по цене)
        # .count() на нем даст общее число таких услуг до пагинации.
        context["popular_services_total_count"] = self.get_queryset().count()

        return context
