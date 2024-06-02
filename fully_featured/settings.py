import os
from pathlib import Path

from decouple import config, Csv
from dj_database_url import parse as dburl
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import firebase_admin

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

BASE_URL = config("BASE_URL", default="http://localhost:8000")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

CORS_ORIGIN_ALLOW_ALL = True

#  CORS_ORIGIN_WHITELIST = (
    #  'http://localhost:5000',
#  )

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv())
# tetst
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
SESSION_COOKIE_SECURE=False

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)
CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)


EMAIL_BACKEND = config("EMAIL_BACKEND")
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = config('SERVER_EMAIL')  # default from-email for Django errors
ANYMAIL = {
    'BREVO_API_KEY': config('BREVO_API_KEY'),
}
FROM_EMAIL = config('FROM_EMAIL')

cred = firebase_admin.credentials.Certificate(
    config('PATH_FIREBASE_PUSH_NOTIFICATION_SERVICE_ACCOUNT_KEY')
)
firebase_admin.initialize_app(cred)

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django_extensions",
    'rest_framework',
    'rest_framework.authtoken',
    "corsheaders",
    "fully_featured.core.apps.CoreConfig",
    "fully_featured.user.apps.UserConfig",
    "fully_featured.payment.apps.PaymentConfig",
    "anymail",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    #  "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


ROOT_URLCONF = "fully_featured.urls"

WSGI_APPLICATION = "fully_featured.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
default_dburl = "sqlite:///" / BASE_DIR / "db.sqlite3"
DATABASES = {"default": config("DATABASE_URL", default=default_dburl, cast=dburl)}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    #  'DEFAULT_THROTTLE_CLASSES': [
        #  'rest_framework.throttling.AnonRateThrottle',
        #  'rest_framework.throttling.UserRateThrottle'
    #  ],
    #  'DEFAULT_THROTTLE_RATES': {
        #  'anon': '60/min',
        #  'user': '10/second'
    #  }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

#  LANGUAGE_CODE = "pt-BR"
LANGUAGE_CODE =  'en-us'

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True

USE_L10N = True


# Sentry
SENTRY_DSN = config("SENTRY_DSN", default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        #  traces_sample_rate=1.0,
        traces_sample_rate=0.1,
        profiles_sample_rate=0,
        send_default_pii=True,
    )

# Stripe
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_PAYMENT_LINK = config("STRIPE_PAYMENT_LINK")
STRIPE_ENDPOINT_SECRET = config("STRIPE_ENDPOINT_SECRET")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/usuario/login"

AUTH_USER_MODEL = "user.UserModel"

# Celery
CELERY_BROKER_URL = config("CELERY_URL", default="redis://localhost:6379")
accept_content = ["application/json"]
result_serializer = "json"
timezone = TIME_ZONE

TASK__MAX_RETRIES = config("TASK__MAX_RETRIES", default=2)
TASK__DEFAULT_RETRY_DELAY = config(
    "TASK__DEFAULT_RETRY_DELAY", default=60
)
