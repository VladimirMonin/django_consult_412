from django.shortcuts import render
from django.http import HttpResponse
from .data import *
from django.contrib.auth.decorators import login_required
from .models import Order
from django.shortcuts import get_object_or_404

def landing(request):
    context = {
        "title": "Главная - Барбершоп Арбуз",
        "services": services, # Из data.py
        "masters": masters,   # Из data.py
        "years_on_market": 50
    }
    return render(request, "core/landing.html", context)


def master_detail(request, master_id):
    try:
        master = [m for m in masters if m["id"] == master_id][0]
    except IndexError:
        return HttpResponse("Мастера не найдено")
    return HttpResponse(f"<h1>{master['name']}</h1>")


def thanks(request):
    masters_count = len(masters)

    context = {
        "masters_count": masters_count,
    }

    return render(request, "core/thanks.html", context)


@login_required
def orders_list(request):
    orders = Order.objects.all()

    context = {"orders": orders, "title": "Список заказов"}
    return render(request, "core/orders_list.html", context)


@login_required
def order_detail(request, order_id: int):

    order = get_object_or_404(Order, id=order_id)

    # Если заказ не найден, возвращаем 404 - данные не найдены

    context = {"title": f"Заказ №{order_id}", "order": order}

    return render(request, "core/order_detail.html", context)
