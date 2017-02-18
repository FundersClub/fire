import dj_database_url
import os

from firebot.settings.base import *  # noqa


###############################################################################
# Django
###############################################################################

ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')
DEBUG = os.environ.get('DJANGO_DEBUG') == 'YES'
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

MEDIAFILES_AWS_STORAGE_BUCKET_NAME = os.environ['MEDIAFILES_AWS_STORAGE_BUCKET_NAME']
MEDIAFILES_AWS_ACCESS_KEY_ID = os.environ['MEDIAFILES_AWS_ACCESS_KEY_ID']
MEDIAFILES_AWS_SECRET_ACCESS_KEY = os.environ['MEDIAFILES_AWS_SECRET_ACCESS_KEY']
DEFAULT_FILE_STORAGE = 'firebot.storages.S3MediaFilesStorage'

DATABASES = {
    'default': dj_database_url.parse(
        os.environ['DATABASE_URL'],
        conn_max_age=int(os.environ.get('DJANGO_DB_CONN_MAX_AGE', 0)),
    ),
}

INSTALLED_APPS += (  # noqa
    'raven.contrib.django.raven_compat',
)

RAVEN_CONFIG = {
    'dsn': 'https://ec78c1fd42f144e2aca4facf5a012e87:205e3c07dfb44cbab804e6c40026d268@sentry.io/139935',
    'release': os.environ.get('HEROKU_SLUG_COMMIT'),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry', 'console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}


###############################################################################
# Celery
###############################################################################

CELERY_BROKER_URL = os.environ['REDIS_URL']


###############################################################################
# GitHub
###############################################################################

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']


###############################################################################
# Firebot
###############################################################################

BASE_URL = os.environ['FIREBOT_BASE_URL']


###############################################################################
# Emails
###############################################################################

EMAIL_BACKEND = 'sgbackend.SendGridBackend'
EMAIL_DOMAIN = os.environ['FIREBOT_EMAIL_DOMAIN']
DEFAULT_FROM_EMAIL = 'bot@' + EMAIL_DOMAIN
SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
SENDGRID_WEBHOOK_SECRET = os.environ['SENDGRID_WEBHOOK_SECRET']
