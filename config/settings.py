import os
from datetime import timedelta
from pathlib import Path

# from celery.schedules import crontab
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка переменных окружения из файла .env
load_dotenv(override=True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")  # Ключ Django для подписи сессий
# STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")  # Ключ API для Stripe

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv("DEBUG") == "True" else False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "django_celery_beat",
    'corsheaders',

    "users",
    "habits_tracker",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Путь к шаблонам
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

REST_FRAMEWORK = {
    # Настройки JWT-токенов
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    # Настройки глобальных разрешений по умолчанию. Доступ для всех API-views только для авторизованных пользователей
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # Настройки по умолчанию для пагинации
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
}


# Настройка JWT-токенов (для авторизации в приложении users)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),  # Время жизни токена доступа
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # Время жизни токена обновления
}

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER", default="postgres"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST", default="localhost"),
        "PORT": os.getenv("DATABASE_PORT", default="5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"  # Настройка временной зоны

USE_I18N = True  # Включает поддержку интернационализации.

USE_L10N = (
    True  # Включает поддержку локализации, применяя форматирование даты и времени.
)

USE_TZ = True  # Включение поддержки временных зон

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"  # Маршрут к папке со статическими файлами
STATICFILES_DIRS = (
    BASE_DIR / "static",
)  # Список папок на диске, из которых будут подгружаться статические файлы

MEDIA_URL = "/media/"  # Путь к папке с медиафайлами
MEDIA_ROOT = os.path.join(
    BASE_DIR, "media"
)  # Путь к папке на диске с медиафайлами, загружаемыми пользователем

# Максимальный размер загружаемых файлов
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # По умолчанию используется BigAutoField для первичных ключей

# Авторизация в приложении users (для использования собственного класса пользователя)
AUTH_USER_MODEL = "users.User"  # Для аутентификации используется собственный класс User


# Настройки для Celery

# URL-адрес брокера сообщений
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")  # Например, Redis, который по умолчанию работает на порту 6379
# URL-адрес брокера результатов, также Redis
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
# Часовой пояс для работы Celery
CELERY_TIMEZONE = TIME_ZONE  # временная зона (совпадает с временной зоной в Django)
# Флаг отслеживания выполнения задач
CELERY_TASK_TRACK_STARTED = True
# Максимальное время на выполнение задачи
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 минут

# Настройка расписания выполнения задач для Celery
CELERY_BEAT_SCHEDULE = {
    "send-habit-reminders": {
        "task": "habits_tracker.tasks.send_reminder_message",  # Путь к задаче
        "schedule": 60,  # Каждые 60 секунд (1 минута)
    },
}

TELEGRAM_URL = "https://api.telegram.org/bot"  # URL для отправки сообщений в Telegram
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")  # Токен бота Telegram

CORS_ALLOWED_ORIGINS = [
    'https://read-only.example.com',
    'https:// read-and-write.example.com',
]
CSRF_TRUSTED_ORIGINS = [
    "https://read-and-write.example.com",

]
CORS_ALLOW_ALL_ORIGINS = False
