from math import e
import re
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .data import *
from django.contrib.auth.decorators import login_required
from .models import Order, Master, Service
from django.shortcuts import get_object_or_404
from django.db.models import Q, F

# messages - это встроенный модуль Django для отображения сообщений пользователю
from django.contrib import messages
from .forms import ServiceForm


def landing(request):
    context = {
        "title": "Главная - Барбершоп Арбуз",
        "services": services,  # Из data.py
        "masters": masters,  # Из data.py
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
        master.refresh_from_db()

    # Получаем связанные услуги мастера
    services = master.services.all()

    context = {
        "title": f"Мастер {master.first_name} {master.last_name}",
        "master": master,
        "services": services,
    }

    return render(request, "core/master_detail.html", context)


def thanks(request):
    masters_count = len(masters)

    context = {
        "masters_count": masters_count,
    }

    return render(request, "core/thanks.html", context)


@login_required
def orders_list(request):

    if request.method == "GET":
        # Получаем все заказы
        # Используем жадную загрузку для мастеров и услуг
        # all_orders = Order.objects.prefetch_related("master", "services").all()
        # all_orders = Order.objects.all()
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
