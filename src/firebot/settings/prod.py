import dj_database_url
import os

from firebot.settings.base import *  # noqa


###############################################################################
# Django
###############################################################################

ADMIN_URL = os.environ.get('DJANGO_ADMIN_URL')
ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')
CSRF_COOKIE_SECURE = True
DEBUG = os.environ.get('DJANGO_DEBUG') == 'YES'
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True

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

if os.environ.get('SENTRY_DSN'):
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        release=os.environ.get('HEROKU_SLUG_COMMIT'),
        integrations=[CeleryIntegration(), DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
        attach_stacktrace=True,
    )


###############################################################################
# Celery
###############################################################################

CELERY_BROKER_URL = os.environ['REDIS_URL']


###############################################################################
# GitHub
###############################################################################

GITHUB_BOT_USERNAME = os.environ['GITHUB_BOT_USERNAME']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']


###############################################################################
# Firebot
###############################################################################

BASE_URL = os.environ['FIREBOT_BASE_URL']
CONTACT_URL = os.environ['CONTACT_URL']
PRIVACY_POLICY_URL = os.environ['PRIVACY_POLICY_URL']
TERMS_OF_SERVICE_URL = os.environ['TERMS_OF_SERVICE_URL']
FIREBOT_BANNED_EMAIL_DOMAINS = os.environ['FIREBOT_BANNED_EMAIL_DOMAINS'].split(',')


###############################################################################
# Emails
###############################################################################

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
EMAIL_DOMAIN = os.environ['FIREBOT_EMAIL_DOMAIN']
DEFAULT_FROM_EMAIL = 'bot@' + EMAIL_DOMAIN
SERVER_EMAIL = DEFAULT_FROM_EMAIL
SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
SENDGRID_WEBHOOK_SECRET = os.environ['SENDGRID_WEBHOOK_SECRET']
