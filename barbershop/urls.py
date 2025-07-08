# barbershop/urls.py
from django.contrib import admin
from django.urls import path, include # Добавили include
from core.views import LandingPageView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import PostSitemap, StaticViewSitemap

sitemaps = {
    'posts': PostSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", LandingPageView.as_view(), name="landing"),
    # Подключаем маршруты из приложения core
    path("barbershop/", include("core.urls")),
    path("users/", include("users.urls")), # Подключили URL-ы приложения users
    path("blog/", include("blog.urls")), # Подключили URL-ы приложения blog
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

    # Добавляем обслуживание медиа-файлов в режиме разработки
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
