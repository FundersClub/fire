import os
from firebot.settings.base import *  # noqa


###############################################################################
# Django
###############################################################################
DEBUG = True
SECRET_KEY = 'o*3#%*xmxb2dgfpn$1835f1p49!i=9kuq(e#zvczkcvg1d)xsk'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'mediafiles'))  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'firebot',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
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
        },
        'django': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}


###############################################################################
# Celery
###############################################################################

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
# CELERY_BROKER_URL = 'redis://localhost:6379/1'


###############################################################################
# GitHub
###############################################################################

GITHUB_BOT_USERNAME = 'firebot-test-local'
GITHUB_TOKEN = '173c367ffc34aafe96118576eae3fde982a337ab'


###############################################################################
# Firebot
###############################################################################

BASE_URL = 'http://localhost:12001'


###############################################################################
# Emails
###############################################################################

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_DOMAIN = 'fire.fundersclub.com'
DEFAULT_FROM_EMAIL = 'bot@' + EMAIL_DOMAIN
SENDGRID_API_KEY = 'unused'
SENDGRID_WEBHOOK_SECRET = 'secret'
