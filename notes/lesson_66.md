# Тема Django. Корпоративный блог. Посты. Пагинатор.  Урок 66

## Корпоративный блог. Посты. Категории. Теги. Комментарии

### Создание и настройка приложения

- создадим приложение `blog`
`poetry run python manage.py startapp blog`

- Подключим приложение в `settings.py`
`INSTALLED_APPS = [ ... , 'blog', ]`

- Создадим ему `urls.py` и неймспейс `blog`

- В нем создал неймсейс и первый маршрут
```python
# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
]
```

- Регистрация маршрутов в конфигурационном `urls.py`
`path("blog/", include("blog.urls")), # Подключили URL-ы приложения blog`


Делаем коммит:
lesson_66:
- Создание и настройка приложения blog
- Подключили урлы приложения blog
- Создали неймспейс blog