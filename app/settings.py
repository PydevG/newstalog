from decouple import config
import dj_database_url
from pathlib import Path
import django_daraja

import pymysql
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)



ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    # 'django_plotly_dash',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blogs',
    'rest_framework', 
    'channels',  # optional for real-time functionality
    'jwt',
    'ckeditor',
    'django_daraja',
    'mpesa',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Other middlewares...
    'blogs.tracking_middleware.PageVisitMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blogs.context_processors.categories_processor',
                'blogs.context_processors.posts_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Change this from 'postgresql' to 'mysql'
        'NAME': 'blogs',
        'USER': 'adminuser',
        'PASSWORD': '@abc123AC',
        'HOST': 'localhost',
        'PORT': '3306',  # Default MySQL port
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
    }
}






# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

import os
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static/')
    
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'blogs.CustomUser'


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.zoho.com"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = 'wyi9 qM1i V69h'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER



INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]



AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'blogs.backends.EmailAuthBackend', 
    
]

BREVO_API_KEY = config('API_KEY')


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}

OPENAI_API_KEY = config("OPENAI_API_KEY")

DARAJA_CONSUMER_KEY = "your_consumer_key"
DARAJA_CONSUMER_SECRET = "your_consumer_secret"
DARAJA_SHORTCODE = "600998"  # Use 600998 for sandbox
DARAJA_PASSKEY = "your_lipa_na_mpesa_passkey"
DARAJA_ENVIRONMENT = "sandbox"  # Change to "production" when live

MPESA_ENVIRONMENT = "sandbox"  # Change to "production" when live
MPESA_CONSUMER_KEY = "your_consumer_key"
MPESA_CONSUMER_SECRET = "your_consumer_secret"
MPESA_SHORTCODE = "600998"  # Use test shortcode
MPESA_PASSKEY = "your_lipa_na_mpesa_passkey"
MPESA_CALLBACK_URL = "https://yourdomain.com/mpesa/stk-callback/"

CSRF_TRUSTED_ORIGINS = ['https://3a3d-41-89-96-143.ngrok-free.app', 'http://localhost']



