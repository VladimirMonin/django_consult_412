from math import e
import re
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from .data import *
from django.contrib.auth.decorators import login_required
from .models import Order, Master, Service, Review
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from django.views.generic import TemplateView

# messages - это встроенный модуль Django для отображения сообщений пользователю
from django.contrib import messages
from .forms import ServiceForm, OrderForm, ReviewForm
import json


def landing(request):
    # Получаем всех мастеров из базы данных (включая неактивных)
    masters_db = Master.objects.all()

    # Получаем все услуги из базы данных вместо только популярных
    all_services = Service.objects.all()

    context = {
        "title": "Главная - Барбершоп Арбуз",
        "services": all_services,  # Все услуги из базы данных
        "masters": masters_db,  # Из базы данных
        "years_on_market": 50,
    }
    return render(request, "core/landing.html", context)


@login_required
def services_list(request):
    """
    Представление для отображения списка всех услуг
    с возможностью их редактирования или удаления
    """
    # Получаем все услуги из базы данных
    services = Service.objects.all()

    context = {
        "title": "Управление услугами",
        "services": services,
    }

    return render(request, "core/services_list.html", context)


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



# Перепишем представление thanks на TemplateView
class ThanksView(TemplateView):
    template_name = "core/thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем количество активных мастеров из базы данных
        masters_count = Master.objects.filter(is_active=True).count()
        context["masters_count"] = masters_count
        
        return context

@login_required
def orders_list(request):
    # Проверяем, что пользователь является сотрудником
    if not request.user.is_staff:
        # Если пользователь не сотрудник, перенаправляем его на главную
        messages.error(request, "У вас нет доступа к этому разделу")
        return redirect("landing")

    if request.method == "GET":
        # Получаем все заказы
        # Используем жадную загрузку для мастеров и услуг
        all_orders = (
            Order.objects.select_related("master").prefetch_related("services").all()
        )

        # Получаем строку поиска
        search_query = request.GET.get("search", None)

        if search_query:
            # Получаем чекбоксы
            check_boxes = request.GET.getlist("search_in")

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

        # Отправляем все заказы в контекст
        context = {
            "title": "Заказы",
            "orders": all_orders,
        }

        return render(request, "core/orders_list.html", context)


@login_required
def order_detail(request, order_id: int):
    # Проверяем, что пользователь является сотрудником
    if not request.user.is_staff:
        # Если пользователь не сотрудник, перенаправляем его на главную
        messages.error(request, "У вас нет доступа к этой странице")
        return redirect("landing")

    order = get_object_or_404(Order, id=order_id)

    # Если заказ не найден, возвращаем 404 - данные не найдены

    context = {"title": f"Заказ №{order_id}", "order": order}

    return render(request, "core/order_detail.html", context)


def service_create(request):

    # Если метод GET - возвращаем пустую форму
    if request.method == "GET":
        form = ServiceForm()
        context = {
            "title": "Создание услуги",
            "form": form,
            "button_txt": "Создать",
        }
        return render(request, "core/service_form.html", context)

    elif request.method == "POST":
        # Создаем форму и передаем в нее POST данные и FILES для загрузки файлов
        form = ServiceForm(request.POST, request.FILES)

        # Если форма валидна:
        if form.is_valid():
            # Так как это ModelForm - нам не надо извлекать поля по отдельности
            # Сохраняем форму в БД
            form.save()
            service_name = form.cleaned_data.get("name")
            # Даем пользователю уведомление об успешном создании
            messages.success(request, f"Услуга {service_name} успешно создана!")

            # Перенаправляем на страницу со всеми услугами
            return redirect("orders_list")

        # В случае ошибок валидации Django автоматически заполнит form.errors
        # и отобразит их в шаблоне, поэтому просто возвращаем форму
        context = {
            "title": "Создание услуги",
            "form": form,
            "button_txt": "Создать",
        }
        return render(request, "core/service_form.html", context)


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
