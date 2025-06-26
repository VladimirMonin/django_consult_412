"""
Модуль views приложения core.
Содержит классы представлений (CBV) для обработки запросов барбершопа.
"""
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from .data import *
from django.contrib.auth.decorators import login_required
from .models import Order, Master, Service, Review
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Prefetch
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import datetime

from django.contrib import messages
from .forms import ServiceForm, OrderForm, ReviewForm, ServiceEasyForm
import json

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class LandingPageView(TemplateView):
    """Представление для главной (посадочной) страницы сайта."""
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
        """Проверяет, аутентифицирован ли пользователь и является ли сотрудником."""
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        """Обрабатывает отсутствие прав доступа, показывая сообщение об ошибке."""
        messages.error(self.request, "У вас нет доступа к этому разделу.")
        return redirect("landing")


class ServicesListView(StaffRequiredMixin, ListView):
    """Представление для отображения списка услуг с доступом только для персонала."""
    model = Service
    template_name = "core/services_list.html"
    context_object_name = "services"
    extra_context = {
        "title": "Управление услугами",
    }

class MasterDetailView(DetailView):
    """
    Представление для отображения детальной информации о мастере и его услугах.
    Реализует:
    - Жадную загрузку связанных услуг и отфильтрованных отзывов для решения проблемы N+1
    - Атомарное обновление счетчика просмотров с использованием F-выражений
    - Кэширование просмотренных мастеров в сессии для избежания повторного счетчика
    """
    model = Master
    template_name = "core/master_detail.html"
    context_object_name = "master"

    def get_queryset(self):
        """
        Возвращает QuerySet с жадной загрузкой связанных услуг и опубликованных отзывов.
        Использует Prefetch для фильтрации отзывов по статусу публикации и сортировки.
        """
        return Master.objects.prefetch_related(
            'services',
            Prefetch('reviews', queryset=Review.objects.filter(is_published=True).order_by("-created_at"))
        )

    def get_object(self, queryset=None):
        """
        Получает объект мастера и атомарно увеличивает счетчик просмотров,
        если мастер еще не был просмотрен в текущей сессии.
        """
        master = super().get_object(queryset)
        
        master_id = master.id
        viewed_masters = self.request.session.get("viewed_masters", [])

        if master_id not in viewed_masters:
            # Атомарное обновление счетчика просмотров в БД
            Master.objects.filter(id=master_id).update(view_count=F("view_count") + 1)
            
            # Обновляем сессию и счетчик в объекте для немедленного отображения
            viewed_masters.append(master_id)
            self.request.session["viewed_masters"] = viewed_masters
            master.view_count += 1

        return master

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст связанные отзывы, услуги и заголовок страницы.
        Данные уже загружены благодаря `prefetch_related` в `get_queryset`.
        """
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        context['services'] = self.object.services.all()
        context['title'] = f"Мастер {self.object.first_name} {self.object.last_name}"
        return context






class ThanksView(TemplateView):
    """
    Представление для страницы благодарности после успешного действия пользователя.
    Формирует контекст с информацией о количестве активных мастеров и сообщением,
    зависящим от источника перехода (заказ, отзыв и т.д.).
    """
    template_name = "core/thanks.html"

    def get_context_data(self, **kwargs):
        """
        Формирует контекст для страницы благодарности:
        - masters_count: количество активных мастеров
        - additional_message: статическое сообщение
        - source_message: динамическое сообщение в зависимости от источника
        """
        context = super().get_context_data(**kwargs)

        masters_count = Master.objects.filter(is_active=True).count()
        context["masters_count"] = masters_count
        context["additional_message"] = "Спасибо, что выбрали наш первоклассный сервис!"

        # Определяем сообщение в зависимости от источника
        if "source" in kwargs:
            source_page = kwargs["source"]
            if source_page == "order":
                context["source_message"] = "Ваш заказ успешно создан и принят в обработку."
            elif source_page == "review":
                context["source_message"] = "Ваш отзыв успешно отправлен и будет опубликован после модерации."
            else:
                context["source_message"] = f"Благодарим вас за ваше действие, инициированное со страницы: {source_page}."
        else:
            context["source_message"] = "Благодарим вас за посещение!"

        return context


class OrdersListView(StaffRequiredMixin, ListView):
    """
    Представление для отображения списка заказов с возможностью фильтрации.
    Доступно только для персонала. Реализует поиск по телефону, имени и комментарию.
    """
    model = Order
    template_name = "core/orders_list.html"
    context_object_name = "orders"
    paginate_by = 1

    def get_queryset(self):
        """
        Возвращает QuerySet заказов с жадной загрузкой связанных данных.
        Поддерживает фильтрацию по поисковому запросу и выбранным полям (телефон, имя, комментарий).
        """
        all_orders = Order.objects.select_related("master").prefetch_related("services").all()
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


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для детального просмотра заказа.
    Доступно только для сотрудников. Проверяет права доступа в методе dispatch.
    """
    model = Order
    template_name = "core/order_detail.html"
    pk_url_kwarg = "order_id"

    def dispatch(self, request, *args, **kwargs):
        """Проверяет, является ли пользователь сотрудником, иначе перенаправляет."""
        if not request.user.is_staff:
            messages.error(request, "У вас нет доступа к этой странице.")
            return redirect("landing")
        return super().dispatch(request, *args, **kwargs)


class ServiceUpdateView(UpdateView):
    """Представление для обновления существующей услуги."""
    form_class = ServiceForm
    model = Service
    template_name = "core/service_form.html"
    success_url = reverse_lazy("services_list")
    extra_context = {
        "button_txt": "Обновить",
    }

    def get_context_data(self, **kwargs):
        """Добавляет заголовок страницы в контекст."""
        context = super().get_context_data(**kwargs)
        context["title"] = f'Редактирование услуги: {self.object.name}'
        return context
    
    def form_valid(self, form):
        """Обрабатывает успешное обновление услуги, показывает сообщение."""
        messages.success(self.request, f"Услуга '{form.cleaned_data['name']}' успешно обновлена!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Обрабатывает невалидную форму, показывает сообщение об ошибке."""
        messages.error(self.request, "Ошибка формы: проверьте ввод данных.")
        return super().form_invalid(form)


class ServiceCreateView(CreateView):
    """
    Представление для создания новой услуги.
    Поддерживает два режима формы: обычный (normal) и упрощенный (easy).
    """
    form_class = ServiceForm
    template_name = "core/service_form.html"
    success_url = reverse_lazy("services_list")
    extra_context = {
        "title": "Создание услуги",
        "button_txt": "Создать",
    }

    def form_valid(self, form):
        """Обрабатывает успешное создание услуги, показывает сообщение."""
        messages.success(self.request, f"Услуга '{form.cleaned_data['name']}' успешно создана!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Обрабатывает невалидную форму, показывает сообщение об ошибке."""
        messages.error(self.request, "Ошибка формы: проверьте ввод данных.")
        return super().form_invalid(form)
    
    def get_form_class(self):
        """Возвращает класс формы в зависимости от параметра form_mode в URL."""
        form_mode = self.kwargs.get("form_mode")
        if form_mode == "normal":
            return ServiceForm
        elif form_mode == "easy":
            return ServiceEasyForm

class MastersServicesAjaxView(View):
    """
    AJAX-представление для получения списка услуг мастера.
    Поддерживает GET и POST запросы. Возвращает данные в формате JSON.
    """
    def get(self, request, *args, **kwargs):
        """Обрабатывает GET-запрос с параметром master_id."""
        master_id = request.GET.get("master_id")
        return self.get_services_json_response(master_id)

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос с JSON-телом, содержащим master_id."""
        data = json.loads(request.body)
        master_id = data.get("master_id")
        return self.get_services_json_response(master_id)

    def get_services_json_response(self, master_id):
        """Возвращает JSON-ответ со списком услуг мастера или ошибку."""
        if not master_id:
            return JsonResponse({"error": "master_id is required"}, status=400)

        master = get_object_or_404(Master, id=master_id)
        services = master.services.all()
        response_data = [{"id": service.id, "name": service.name} for service in services]
        return JsonResponse(response_data, safe=False)

class OrderCreateView(CreateView):
    """Представление для создания нового заказа."""
    model = Order
    form_class = OrderForm
    template_name = "core/order_form.html"
    
    def get_success_url(self):
        """Возвращает URL для перенаправления после успешного создания заказа."""
        return reverse_lazy("thanks_with_source", kwargs={"source": "order"})

    def get_context_data(self, **kwargs):
        """Добавляет заголовок и текст кнопки в контекст."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Создание заказа"
        context["button_text"] = "Создать"
        return context

    def form_valid(self, form):
        """Обрабатывает успешное создание заказа, показывает сообщение."""
        client_name = form.cleaned_data.get("client_name")
        messages.success(self.request, f"Заказ для {client_name} успешно создан!")
        return super().form_valid(form)


class ReviewCreateView(CreateView):
    """Представление для создания нового отзыва."""
    model = Review
    form_class = ReviewForm
    template_name = "core/review_form.html"

    def get_success_url(self):
        """Возвращает URL для перенаправления после успешной отправки отзыва."""
        return reverse_lazy("thanks_with_source", kwargs={"source": "review"})

    def get_initial(self):
        """Устанавливает начальное значение мастера, если передан master_id."""
        initial = super().get_initial()
        master_id = self.request.GET.get("master_id")
        if master_id:
            try:
                initial["master"] = Master.objects.get(pk=master_id)
            except Master.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        """Добавляет заголовок и текст кнопки в контекст."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Оставить отзыв"
        context["button_text"] = "Отправить"
        return context

    def form_valid(self, form):
        """
        Сохраняет отзыв с флагом is_published=False и показывает сообщение.
        """
        review = form.save(commit=False)
        review.is_published = False
        review.save()
        
        messages.success(
            self.request,
            "Ваш отзыв успешно добавлен! Он будет опубликован после проверки модератором.",
        )
        return redirect(self.get_success_url())

class MasterInfoAjaxView(View):
    """
    AJAX-представление для получения информации о мастере.
    Возвращает данные в формате JSON. Требует заголовок X-Requested-With.
    """
    def get(self, request, *args, **kwargs):
        """Обрабатывает GET-запрос, проверяет AJAX-запрос и параметр master_id."""
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
    greeting_get_message = "Привет, мир! Это GET запрос из GreetingView."
    greeting_post_message = "Вы успешно отправили POST запрос в GreetingView!"

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET-запросы, возвращает простое HTTP-сообщение."""
        return HttpResponse(self.greeting_get_message)

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запросы, возвращает простое HTTP-сообщение."""
        return HttpResponse(self.greeting_post_message)


# 2. TemplateView - Отображение шаблонов с контекстом


# Пример 1: Простой TemplateView ("View в 2 строки")
class SimplePageView(TemplateView):
    """
    Простейшее представление для отображения статической страницы.
    Использует атрибут template_name для указания шаблона.
    """
    template_name = "core/simple_page.html"


# Пример 2: TemplateView с дополнительным контекстом
class AboutUsView(TemplateView):
    """
    Представление для страницы "О нас".
    Демонстрирует передачу как статического, так и динамического контекста в шаблон.
    """
    template_name = "core/about_us.html"

    def get_context_data(self, **kwargs):
        """
        Формирует контекст для страницы "О нас", включая:
        - Название компании
        - Год основания
        - Текущий год
        - Количество лет на рынке
        - Заголовок страницы
        - Контактный email
        """
        context = super().get_context极端的_data(**kwargs)
        context["company_name"] = "Барбершоп 'Арбуз'"
        context["start_year"] = 2010
        context["current_year"] = datetime.date.today().year
        context["years_on_market"] = datetime.date.today().year - context["start_year"]
        context["page_title"] = "О нас - Барбершоп 'Арбуз'"
        context["contact_email"] = "contact@arbuz-barbershop.com"
        return context


class ServiceDetailView(DetailView):
    """
    Представление для отображения детальной информации об услуге.
    Использует модель Service и явно указанное имя шаблона.
    """
    model = Service
    template_name = "core/service_detail.html"


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
