import dj_database_url

from firebot.settings.base import *  # noqa


ALLOWED_HOSTS = ','.split(os.environ['DJANGO_ALLOWED_HOSTS'])
DEBUG = os.environ.get('DJANGO_DEBUG') == 'YES'
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASES = {
    'default': dj_database_url.parse(
        os.environ['DATABASE_URL'],
        conn_max_age=int(os.environ.get('DJANGO_DB_CONN_MAX_AGE', 0)),
    ),
}
