from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from .data import *
from django.contrib.auth.decorators import login_required
from .models import Order, Master, Service, Review
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
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

#TODO - Тут подойдет DetailView
def master_detail(request, master_id):
    # Получаем мастера по id
    master = get_object_or_404(Master, id=master_id)

    # Проверяем, просматривал ли пользователь этого мастера ранее
    viewed_masters = request.session.get("viewed_masters", [])

    # Если этот мастер ещё не был просмотрен этим пользователем в текущей сессии
    if master_id not in viewed_masters:

        # Увеличиваем счетчик просмотров мастера
        # F - это специальный объект, который позволяет ссылаться на поля модели

        Master.objects.filter(id=master_id).update(view_count=F("view_count") + 1)

        # Добавляем мастера в список просмотренных
        viewed_masters.append(master_id)
        request.session["viewed_masters"] = viewed_masters

        # Обновляем объект после изменения в БД
        master.refresh_from_db()  # Получаем связанные услуги мастера
    services = master.services.all()

    # Получаем опубликованные отзывы о мастере, сортируем по дате создания (сначала новые)
    reviews = master.reviews.filter(is_published=True).order_by("-created_at")

    context = {
        "title": f"Мастер {master.first_name} {master.last_name}",
        "master": master,
        "services": services,
        "reviews": reviews,
    }

    return render(request, "core/master_detail.html", context)

class MasterDetailView(DetailView):
    model = Master
    template_name = "core/master_detail.html"
    context_object_name = "master"

    def get_object(self, queryset=None):
        """
        Получает объект мастера по ID из URL жадной загрузкой добывает связанные данные и обновляет счетчик просмотров если мастер еще не был просмотрен в текущей сессии.
        """
        master_id = self.kwargs.get("pk")
        
        # Жадная подгрузка Мастера + отзывы + услуги
        master = Master.objects.get(id=master_id)
        self.reviews = master.reviews.filter(is_published=True).order_by("-created_at")
        self.services = master.services.all()

        # Получаем список просмотренных мастеров из сессии
        viewed_masters = self.request.session.get("viewed_masters", [])

        # Если мастер еще не был просмотрен в текущей сессии, увеличиваем счетчик просмотров
        if master_id not in viewed_masters:
            Master.objects.filter(id=master_id).update(view_count=F("view_count") + 1)

            # Добавляем мастера в список просмотренных
            viewed_masters.append(master_id)
            self.request.session["viewed_masters"] = viewed_masters

            # Обновляем объект после изменения в БД
            master.refresh_from_db()  # Получаем связанные услуги мастера

        return master

    def get_context_data(self, **kwargs):
        """
        Формирует и возвращает словарь контекста для шаблона "Детали мастера".
        """
        context = super().get_context_data(**kwargs)
        context["reviews"] = self.reviews
        context["services"] = self.services






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



def service_update(request, service_id):
    # Вне зависимости от метода - получаем услугу
    service = get_object_or_404(Service, id=service_id)

    # Если метод GET - возвращаем форму
    if request.method == "GET":
        # У нас форма связана с моделью. Рендер всех полей
        # Просто ложим в форму объект услуги
        form = ServiceForm(instance=service)

        context = {
            "title": f"Редактирование услуги {service.name}",
            "form": form,
            "button_txt": "Обновить",
        }
        return render(request, "core/service_form.html", context)

    elif request.method == "POST":
        # Создаем форму и передаем в нее POST данные, FILES для загрузки файлов и экземпляр для обновления
        form = ServiceForm(request.POST, request.FILES, instance=service)

        # Если форма валидна:
        if form.is_valid():
            # Форма связана с моделью, просто сохраним ее
            form.save()

            service_name = form.cleaned_data.get("name")
            # Даем пользователю уведомление об успешном обновлении
            messages.success(request, f"Услуга {service_name} успешно обновлена!")

            # Перенаправляем на страницу со всеми услугами
            return redirect("orders_list")
        else:
            # Если данные не валидны, возвращаем ошибку
            messages.error(request, "Ошибка: вы что-то сделали не так.")

            context = {
                "title": f"Редактирование услуги {service.name}",
                "form": form,
                "button_txt": "Обновить",
            }

            return render(request, "core/service_form.html", context)

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

#TODO - Тут подойдет обычная View
def masters_services_by_id(request, master_id=None):
    """
    Вью для ajax запросов фронтенда, для подгрузки услуг конкретного мастера в форму
    m2m выбора услуг
    """
    # Если master_id не передан в URL, пробуем получить его из POST-запроса
    if master_id is None:
        data = json.loads(request.body)
        master_id = data.get("master_id")

    # Получаем мастера по id
    master = get_object_or_404(Master, id=master_id)

    # Получаем услуги
    services = master.services.all()

    # Формируем ответ в виде JSON
    response_data = []

    for service in services:
        # Добавляем в ответ id и название услуги
        response_data.append(
            {
                "id": service.id,
                "name": service.name,
            }
        )
    # Возвращаем ответ в формате JSON
    return HttpResponse(
        json.dumps(response_data, ensure_ascii=False, indent=4),
        content_type="application/json",
    )

# #TODO - Тут подойдет CreateView
def order_create(request):
    """
    Вью для создания заказа
    """
    if request.method == "GET":
        # Если метод GET - возвращаем пустую форму
        form = OrderForm()

        context = {
            "title": "Создание заказа",
            "form": form,
            "button_text": "Создать",
        }
        return render(request, "core/order_form.html", context)

    if request.method == "POST":
        # Создаем форму и передаем в нее POST данные
        form = OrderForm(request.POST)

        # Если форма валидна:
        if form.is_valid():
            # Сохраняем форму в БД
            form.save()
            client_name = form.cleaned_data.get("client_name")
            # Даем пользователю уведомление об успешном создании
            messages.success(
                request, f"Заказ для {client_name} успешно создан!"
            )  # Перенаправляем на страницу благодарности с указанием источника
            return redirect("thanks_with_source", source="order")

        # В случае ошибок валидации Django автоматически заполнит form.errors
        # и отобразит их в шаблоне, поэтому просто возвращаем форму
        context = {
            "title": "Создание заказа",
            "form": form,
            "button_text": "Создать",
        }
        return render(request, "core/order_form.html", context)

# #TODO - Тут подойдет CreateView
def create_review(request):
    """
    Представление для создания отзыва о мастере
    """
    if request.method == "GET":
        # При GET-запросе показываем форму, если указан ID мастера, устанавливаем его в поле мастера
        master_id = request.GET.get("master_id")

        initial_data = {}
        if master_id:
            try:
                master = Master.objects.get(pk=master_id)
                initial_data["master"] = master
            except Master.DoesNotExist:
                pass

        form = ReviewForm(initial=initial_data)

        context = {
            "title": "Оставить отзыв",
            "form": form,
            "button_text": "Отправить",
        }
        return render(request, "core/review_form.html", context)

    elif request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)

        if form.is_valid():
            review = form.save(
                commit=False
            )  # Не сохраняем сразу, чтобы установить is_published=False
            review.is_published = False  # Отзыв по умолчанию не опубликован
            review.save()  # Сохраняем отзыв

            # Сообщаем пользователю, что его отзыв успешно добавлен и будет опубликован после модерации
            messages.success(
                request,
                "Ваш отзыв успешно добавлен! Он будет опубликован после проверки модератором.",
            )  # Перенаправляем на страницу благодарности с указанием источника
            return redirect("thanks_with_source", source="review")

        # В случае ошибок валидации возвращаем форму с ошибками
        context = {
            "title": "Оставить отзыв",
            "form": form,
            "button_text": "Отправить",
        }
        return render(request, "core/review_form.html", context)

#TODO - Тут подойдет либо DetailView, либо View
def get_master_info(request):
    """
    Универсальное представление для получения информации о мастере через AJAX.
    Возвращает данные мастера в формате JSON.
    """
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        master_id = request.GET.get("master_id")
        if master_id:
            try:
                master = Master.objects.get(pk=master_id)
                # Формируем данные для ответа
                master_data = {
                    "id": master.id,
                    "name": f"{master.first_name} {master.last_name}",
                    "experience": master.experience,
                    "photo": master.photo.url if master.photo else None,
                    "services": list(master.services.values("id", "name", "price")),
                }
                return JsonResponse({"success": True, "master": master_data})
            except Master.DoesNotExist:
                return JsonResponse({"success": False, "error": "Мастер не найден"})
        return JsonResponse({"success": False, "error": "Не указан ID мастера"})
    return JsonResponse({"success": False, "error": "Недопустимый запрос"})


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
