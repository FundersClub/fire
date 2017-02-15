import dj_database_url

from firebot.settings.base import *  # noqa

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DATABASES = {
    'default': dj_database_url.parse(
        os.environ['DJANGO_DB'],
        conn_max_age=int(os.environ.get('DJANGO_DB_CONN_MAX_AGE', 0)),
    ),
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'firebot',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
    },
}
