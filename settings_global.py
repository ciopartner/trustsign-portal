# -*- coding: utf-8 -*-
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
###########################################
# GLOBAL SETTINGS FOR MEZZANINE AND OSCAR #
###########################################

########################
# MAIN DJANGO SETTINGS #
########################

# People who get code error notifications.
# In the format (('Full Name', 'email@example.com'),
#                ('Full Name', 'anotheremail@example.com'))
ADMINS = (
    ('Alessandro Reichert', 'alessandro.reichert@ciopartner.com.br'),
)
MANAGERS = ADMINS

ALLOWED_HOSTS = [
    '*.ciopartner.com.br',
    '*.trustsign.com.br',
]

# Para evitar as URLs com problema no LIGHTTPD
FORCE_SCRIPT_NAME = ''

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# If you set this to True, Django will use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "pt_BR"

# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = "199dea65-51c5-4ded-9b3d-eb95f22878bb4b9286f0-db7f-4dda-8b1b-8a32faa6aee9f8cd3ea6-cdee-48ef-a813-042d4b1b3e68"

# Tuple of IP addresses, as strings, that:
#   * See debug comments, when DEBUG is true
#   * Receive x-headers
INTERNAL_IPS = ("127.0.0.1",)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

# Os dois primeiros servem para fazer login com e-mail
AUTHENTICATION_BACKENDS = (
    "mezzanine.core.auth_backends.MezzanineBackend",
    'oscar.apps.customer.auth_backends.Emailbackend',
    'django.contrib.auth.backends.ModelBackend',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


###########
# LOGGING #
###########
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)-15s %(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)-15s %(levelname)s %(message)s [%(pathname)s:%(lineno)d %(funcName)s]'
        },
        'verysimple': {
            'format': '%(asctime)-15s %(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': os.path.join(PROJECT_ROOT, 'logs', 'logfile.log'),
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
        'logfile_comodo': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'verysimple',
            'filename': os.path.join(PROJECT_ROOT, 'logs', 'logfile-comodo.log'),
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 50,
        },
        'logfile_crm': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'verysimple',
            'filename': os.path.join(PROJECT_ROOT, 'logs', 'logfile-crm.log'),
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 50,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        'portal': {
            'handlers': ['console', 'logfile', 'mail_admins'],
            'level': 'INFO'
        },
        'ecommerce': {
            'handlers': ['console', 'logfile', 'mail_admins'],
            'level': 'INFO'
        },
        'libs.crm': {
            'handlers': ['console', 'logfile_crm'],
            'level': 'DEBUG'
        },
        'libs.comodo': {
            'handlers': ['console', 'logfile_comodo'],
            'level': 'DEBUG'
        },
        'oscar': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG'
        }
    },
}


#############
# DATABASES #
#############

# DATABASE_ROUTERS = ['routers.UserSessionRouter']

DATABASES = {
    "common": {
        # Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": PROJECT_ROOT+"/common.db",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    },
    "mezzanine": {
        # Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": "../mezzanine.db",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    },
    "checkout": {
        # Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": "../checkout.db",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}

###################
# DEPLOY SETTINGS #
###################

# These settings are used by the default fabfile.py provided.
# Check fabfile.py for defaults.

# FABRIC = {
#     "SSH_USER": "", # SSH username
#     "SSH_PASS":  "", # SSH password (consider key-based authentication)
#     "SSH_KEY_PATH":  "", # Local path to SSH key file, for key-based auth
#     "HOSTS": [], # List of hosts to deploy to
#     "VIRTUALENV_HOME":  "", # Absolute remote path for virtualenvs
#     "PROJECT_NAME": "", # Unique identifier for project
#     "REQUIREMENTS_PATH": "", # Path to pip requirements, relative to project
#     "GUNICORN_PORT": 8000, # Port gunicorn will listen on
#     "LOCALE": "en_US.UTF-8", # Should end with ".UTF-8"
#     "LIVE_HOSTNAME": "www.example.com", # Host for public site.
#     "REPO_URL": "", # Git or Mercurial remote repo URL for the project
#     "DB_PASS": "", # Live database password
#     "ADMIN_PASS": "", # Live admin user password
# }

ENVIRONMENT = os.getenv('TRUSTSIGN_ENVIRONMENT', 'DEV')
if ENVIRONMENT == 'DEV':
    DEBUG = True
    URL_PORTAL = '/portal/'
    URL_ECOMMERCE = '/ecommerce/'
    # Para que haja compartilhamento de sessions...
    SESSION_COOKIE_DOMAIN = 'localhost'
elif ENVIRONMENT == 'QAS':
    DEBUG = True
    URL_PORTAL = '/portal/'
    URL_ECOMMERCE = '/ecommerce/'
    # Para que haja compartilhamento de sessions...
    SESSION_COOKIE_DOMAIN = 't.trustsign.com.br'
elif ENVIRONMENT == 'PRD':
    DEBUG = False
    URL_PORTAL = '/portal/'
    URL_ECOMMERCE = '/ecommerce/'
    # Para que haja compartilhamento de sessions...
    SESSION_COOKIE_DOMAIN = 'trustsign.com.br'

URL_CONTINUAR_COMPRANDO = URL_PORTAL + 'certificado-digital'

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
try:
    from local_settings import *
except ImportError:
    pass
