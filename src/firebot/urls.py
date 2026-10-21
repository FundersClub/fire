from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import (
    include,
    re_path,
)
from django.views.static import serve

import firebot.views


urlpatterns = [
    # Django Views
    re_path(r'^accounts/', include('allauth.urls')),
    re_path(r'^{}/'.format(getattr(settings, 'ADMIN_URL', 'admin')), admin.site.urls),
    re_path(r'^api/', include([
        re_path(r'^github/', include('fb_github.api')),
    ])),
    re_path(r'^test-500/$', firebot.views.test_500),
    re_path(r'^emails/', include('fb_emails.urls')),

    # Static files
    re_path(r'^$', serve, {'path': 'static.html', 'document_root': settings.STATIC_FRONTEND_ROOT}, name='index'),
    re_path(r'^.+', firebot.views.app_html, name='repos'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
