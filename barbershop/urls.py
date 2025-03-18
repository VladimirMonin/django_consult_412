from django.contrib import admin
from django.urls import path
from core.views import main, master_detail, thanks


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main),
    # Конвертер путей <int:master_id> преобразует часть URL в целое число и передаст его как аргумент в функцию master_detail
    path('masters/<int:master_id>/', master_detail),
    path('thanks/', thanks),

]
