from django.conf import settings
from django.conf.urls import (
    include,
    url,
)
from django.conf.urls.static import static
from django.contrib import admin
from django.views.static import serve

import firebot.views


urlpatterns = [
    # Static files
    url(r'^$', serve, {'path': 'index.html', 'document_root': settings.STATIC_FRONTEND_ROOT}, name='index'),
    url(r'^repos/$', serve, {'path': 'index.html', 'document_root': settings.STATIC_FRONTEND_ROOT}, name='index'),

    # Django Views
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include([
        url(r'^github/', include('fb_github.api')),
    ])),
    url(r'^test-500/$', firebot.views.test_500),
    url(r'^emails/', include('fb_emails.urls')),
    url(r'^github/', include('fb_github.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
