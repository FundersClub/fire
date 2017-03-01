import os


###############################################################################
# Django
###############################################################################

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'django_extensions',
    'rest_framework',

    'firebot',
    'fb_emails',
    'fb_github',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'firebot.middleware.XForwardedForMiddleware',
]

ROOT_URLCONF = 'firebot.urls'

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
                'firebot.context_processors.firebot_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'firebot.wsgi.application'

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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'staticfiles'))
STATIC_FRONTEND_ROOT = os.path.join(STATIC_ROOT, 'frontend')
STATICFILES_DIRS = [
    os.path.abspath(os.path.join(BASE_DIR, '..', 'dist-frontend'))
]
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

###############################################################################
# Allauth
###############################################################################

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': [
            'user:email',
        ],
        'VERIFIED_EMAIL': True,
    }
}


###############################################################################
# Django Rest Framework
###############################################################################

# TODO review this
# REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': (),
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework.authentication.SessionAuthentication',
#         'rest_framework.authentication.BasicAuthentication',
#     ),
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 20,
#     'DEFAULT_PARSER_CLASSES': (
#         'rest_framework.parsers.JSONParser',
#         'rest_framework.parsers.FormParser',
#         'rest_framework.parsers.MultiPartParser',
#     ),
# }


###############################################################################
# Celery
###############################################################################

CELERY_IGNORE_RESULT = True
from firebot.settings.tasks import *  # noqa


###############################################################################
# Firebot
###############################################################################

FIREBOT_BANNED_EMAIL_SLUGS = (
    'abuse',
    'admin',
    'administrator',
    'billing',
    'catalyst',
    'compliance',
    'dev',
    'devnull',
    'dns',
    'fc',
    'fire',
    'ftp',
    'fundersclub',
    'help',
    'hostmaster',
    'info',
    'inoc',
    'ispfeedback',
    'ispsupport',
    'list',
    'list-request',
    'maildaemon',
    'no-reply',
    'noc',
    'noreply',
    'null',
    'phish',
    'phishing',
    'postmaster',
    'privacy',
    'registrar',
    'root',
    'security',
    'spam',
    'support',
    'sysadmin',
    'tech',
    'undisclosed-recipients',
    'unsubscribe',
    'usenet',
    'uucp',
    'webmaster',
    'www',
)
