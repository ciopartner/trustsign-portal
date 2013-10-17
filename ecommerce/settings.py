# -*- coding: utf-8 -*-
# Django settings for ecommerce project.

# Importa todas as opcoes default do OSCAR
from oscar.defaults import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
LANGUAGE_CODE = "pt_BR"
LANGUAGES = (
    ('pt', 'Português'),
    ('en', 'English'),
)

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

#########
# PATHS #
#########

import os
import sys

# Full filesystem path to the project.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_PARENT = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT_PARENT)

# Retirado do OSCAR SANDBOX
location = lambda x: os.path.join(PROJECT_ROOT, x)

# Name of the directory for the project.
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]

# Traduções
LOCALE_PATHS = (
    location('locale'),
)

# Every cache key will get prefixed with this value - here we set it to
# the name of the directory the project is in to try and use something
# project specific.
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_DIRNAME

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = location('static_root')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"

# Retirado de OSCAR SANDBOX: MEDIA_ROOT = onde estarão os user uploaded files
MEDIA_ROOT = location('media')
MEDIA_URL = '/media/'

# Package/module name to import the root urlpatterns from for the project.
ROOT_URLCONF = "%s.urls" % PROJECT_DIRNAME

# Put strings here, like "/home/html/django_templates"
# or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), '', x)
from oscar import OSCAR_MAIN_TEMPLATE_DIR
TEMPLATE_DIRS = (
    location('templates'),
    OSCAR_MAIN_TEMPLATE_DIR,
)

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    location("static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    # 'routers.RouterMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'website.middlewares.XsSharing',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # OSCAR MIDDLEWARE:
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

# ADDED FOR OSCAR
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    'oscar.apps.search.context_processors.search_form',
    'oscar.apps.promotions.context_processors.promotions',
    'oscar.apps.checkout.context_processors.checkout',
    'oscar.apps.customer.notifications.context_processors.notifications',
    'oscar.core.context_processors.metadata',
    'ecommerce.website.context_processors.url',
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ecommerce.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    #'ecommerce.apps.customer',
    #'ecommerce.apps.checkout',
    #'website',

    'south',
    'compressor',
]

# APPS FOR OSCAR
from oscar import get_core_apps

INSTALLED_APPS += get_core_apps(['ecommerce.apps.checkout', 'ecommerce.apps.customer', 'ecommerce.apps.catalogue'])

# TODO: Antes de ir para produção isso precisa ser alterado para um novo engine
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

OSCAR_DEFAULT_CURRENCY = 'BRL'
OSCAR_SHOP_NAME = 'TrustSign e-commerce'

# STATUS DAS ORDENS
OSCAR_INITIAL_ORDER_STATUS = 'Pendente'
OSCAR_INITIAL_LINE_STATUS = 'Pendente'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pendente': ('Em processamento', 'Cancelada',),
    'Em processamento': ('Pagamento Aprovado', 'Cancelada',),
    'Pagamento Aprovado': ('Concluído',),
    'Concluído': (),
    'Cancelada': (),
}

# Sobrescreva com os settings globais
from settings_global import *
DEFAULT_DATABASE = DATABASES.get('common')
DATABASES = {'default': DEFAULT_DATABASE}

# COBREBEM
COBREBEM_HOST = "https://teste.aprovafacil.com/cgi-bin/APFW"
COBREBEM_USER = "trustsign"

EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'AKIAJB23EUFD5S4FY76Q'
EMAIL_HOST_PASSWORD = 'AjfrHH5LIVaKku5iBMkbBs5CWM2IK0Z6ZhiXWKVQHHHV'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = SERVER_EMAIL = OSCAR_FROM_EMAIL = 'alessandro.reichert@ciopartner.com.br'