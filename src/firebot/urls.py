from django.conf import settings
from django.conf.urls import (
    include,
    url,
)
from django.conf.urls.static import static
from django.contrib import admin

import firebot.views


urlpatterns = [
    # Django Views
    url(r'^accounts/', include('allauth.urls')),
    url(r'^{}/'.format(getattr(settings, 'ADMIN_URL', 'admin')), admin.site.urls),
    url(r'^api/', include([
        url(r'^github/', include('fb_github.api')),
    ])),
    url(r'^test-500/$', firebot.views.test_500),
    url(r'^emails/', include('fb_emails.urls')),

    # Static homepage and clientside app
    url(r'^$', firebot.views.static_html, name='static'),
    url(r'^.+', firebot.views.app_html, name='app'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
