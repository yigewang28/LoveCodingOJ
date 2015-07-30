"""
Django settings for webapp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ConfigParser
import djcelery

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


TEMPLATE_DIRS = (
   os.path.join(os.path.dirname(__file__),'../oj/template'),
)
STATICFILES_DIRS = ( 
    os.path.join(os.path.dirname(__file__),'../oj/static'),
)
print os.path.join(os.path.dirname(__file__),'../oj/static')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=nyjs!%kbl+q%696fku5o=7lf1j39e_(x66$cry(fd=7h0#_y('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    '.amazonaws.com',
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oj',
    'djcelery',                 # Add Django Celery
    'kombu.transport.django',   # Add support for the django:// broker
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
#BROKER_URL = 'django://'
# celery config info
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

djcelery.setup_loader()
BROKER_BACKEND = "djkombu.transport.DatabaseTransport"

ROOT_URLCONF = 'webapp.urls'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/home'
WSGI_APPLICATION = 'webapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = 'media/'
MEDIA_URL = '/media/'

config = ConfigParser.ConfigParser()
config.read("config.ini")

EMAIL_HOST = config.get('Email', 'Host')
EMAIL_PORT = config.get('Email', 'Port')
EMAIL_HOST_USER = config.get('Email', 'User')
EMAIL_HOST_PASSWORD = config.get('Email', 'Password')
EMAIL_USE_SSL = True

print 'EMAIL_HOST',EMAIL_HOST+':'+str(EMAIL_PORT)
print 'EMAIL_HOST_USER',EMAIL_HOST_USER
