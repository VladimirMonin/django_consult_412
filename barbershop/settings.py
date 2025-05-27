from pathlib import Path

# Установили python dotenv и импортировали
from dotenv import load_dotenv
import os


# Загрузили переменные окружения
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Добавляем разрешенные хосты для нашего домена и IP
ALLOWED_HOSTS = [
    'vladimirmonin-django-consult-412-1cdd.twc1.net',  # Основной домен
    'www.vladimirmonin-django-consult-412-1cdd.twc1.net',  # С www
    '37.220.80.53',  # Публичный IP
    'localhost',  # Для локальной разработки
    '127.0.0.1',  # Для локальной разработки
    '0.0.0.0',
]

# ...existing code...

# Настройки безопасности для продакшена
# Настройки CSRF для разрешения запросов с нашего домена
CSRF_TRUSTED_ORIGINS = [
    'https://vladimirmonin-django-consult-412-1cdd.twc1.net',
    'http://vladimirmonin-django-consult-412-1cdd.twc1.net',
    'https://www.vladimirmonin-django-consult-412-1cdd.twc1.net',
    'http://www.vladimirmonin-django-consult-412-1cdd.twc1.net',

]


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "debug_toolbar",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "barbershop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.menu_context",  # Добавили наш контекстный процессор
            ],
        },
    },
]

WSGI_APPLICATION = "barbershop.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

# "en-us" - это код языка, который используется в проекте. Он указывает, что язык по умолчанию - английский (США).
# "ru" - это код языка, который используется для перевода текстов на русский язык.
LANGUAGE_CODE = "ru"

# Список часовых зон для этого параметра
# Asia/Almaty - это код часовой зоны для Алматы, Казахстан.
# Europe/Moscow - это код часовой зоны для Москвы, Россия.
# Europe/Moscow (Москва)
# Europe/Kaliningrad (Калининград)
# Europe/Samara (Самара)
# Europe/Volgograd (Волгоград)
# Europe/Astrakhan (Астрахань)
# Europe/Ulyanovsk (Ульяновск)
# Asia/Yekaterinburg (Екатеринбург)
# Asia/Omsk (Омск)
# Asia/Novosibirsk (Новосибирск)
# Asia/Barnaul (Барнаул)
# Asia/Tomsk (Томск)
# Asia/Novokuznetsk (Новокузнецк)
# Asia/Krasnoyarsk (Красноярск)
# Asia/Irkutsk (Иркутск)
# Asia/Chita (Чита)
# Asia/Yakutsk (Якутск)
# Asia/Khandyga (Хандыга)
# Asia/Vladivostok (Владивосток)
# Asia/Ust-Nera (Усть-Нера)
# Asia/Magadan (Магадан)
# Asia/Sakhalin (Сахалин)
# Asia/Srednekolymsk (Среднеколымск)
# Asia/Kamchatka (Камчатка)
# Asia/Anadyr (Анадырь)
TIME_ZONE = "Asia/Almaty"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Указали путь к статическим файлам в проекте. Это адрес на сервере, по которому будут доступны статические файлы
STATIC_URL = "static/"

# Указали путь к папке, где будут храниться статические файлы
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Настройки для медиа-файлов (загружаемые пользователями)
# URL-путь для доступа к медиа файлам
MEDIA_URL = "/media/"
# Физический путь хранения файлов на сервере
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Настройка маршрут для авторизации
LOGIN_URL = "/admin/"

# Настройка для отладки в локальной сети
INTERNAL_IPS = [
    "127.0.0.1",
]

# Файл settings.py
# Куки будет жить даже после закрытия браузера
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Время жизни куки в секундах (2 недели)
SESSION_COOKIE_AGE = 1209600  # 60 * 60 * 24 * 14 (секунд в двух неделях)


MISTRAL_MODERATIONS_GRADES = {
        'hate_and_discrimination': 0.1, # ненависть и дискриминация
        'sexual': 0.1, # сексуальный
        'violence_and_threats': 0.1, # насилие и угрозы
        'dangerous_and_criminal_content': 0.1, # опасный и криминальный контент
        'selfharm': 0.1, # самоповреждение
        'health': 0.1, # здоровье
        'financial': 0.1, # финансовый
        'law': 0.1, # закон
        'pii': 0.1, # личная информация
}


TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")