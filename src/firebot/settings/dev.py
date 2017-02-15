from firebot.settings.base import *  # noqa


###############################################################################
# Django
###############################################################################
DEBUG = True
SECRET_KEY = 'o*3#%*xmxb2dgfpn$1835f1p49!i=9kuq(e#zvczkcvg1d)xsk'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'firebot',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
    },
}


###############################################################################
# Celery
###############################################################################

#CELERY_TASK_ALWAYS_EAGER = True
#CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_BROKER_URL = 'redis://localhost:6379/1'
