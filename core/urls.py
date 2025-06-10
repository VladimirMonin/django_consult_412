# core/urls.py
from django.contrib import admin
from django.urls import path
from .views import (
    ThanksView,
    MastersServicesAjaxView,
    OrderCreateView,
    ReviewCreateView,
    MasterInfoAjaxView,
    GreetingView,  # Добавили импорт GreetingView
    SimplePageView,  # Добавили импорт SimplePageView
    AboutUsView,  # Добавили импорт AboutUsView
    ServiceDetailView,
    OrderDetailView,
    ServicesListView,
    OrdersListView,
    ServiceCreateView,
    ServiceUpdateView,
    MasterDetailView,
)

# Эти маршруты будут доступны с префиксом /barbershop/

urlpatterns = [
    path("masters/<int:pk>/", MasterDetailView.as_view(), name="master_detail"),
    path("thanks/", ThanksView.as_view(), name="thanks"),
    path("thanks/<str:source>/", ThanksView.as_view(), name="thanks_with_source"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order_detail"),
    path(
        "services/", ServicesListView.as_view(), name="services_list"
    ),  # Это FBV, оставим пока
    # path("services_cbv/", ServiceListView.as_view(), name="services_list_cbv"), # Закомментируем, т.к. ServiceListView еще не создан
    path("service/<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),
    path("service_create/<str:form_mode>/", ServiceCreateView.as_view(), name="service_create"),
    path("service_update/<int:pk>/", ServiceUpdateView.as_view(), name="service_update"),
    path(
        "masters_services/", MastersServicesAjaxView.as_view(), name="masters_services_by_id_ajax"
    ),
    path("order_create/", OrderCreateView.as_view(), name="order_create"),
    path("review/create/", ReviewCreateView.as_view(), name="create_review"),
    path("api/master-info/", MasterInfoAjaxView.as_view(), name="get_master_info"),
    # --- Этап 1: Базовые CBV ---
    path("greeting/", GreetingView.as_view(), name="greeting"),
    path("simple-page/", SimplePageView.as_view(), name="simple_page"),
    path("about-us/", AboutUsView.as_view(), name="about_us"),
]
