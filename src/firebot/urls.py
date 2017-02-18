from django.conf import settings
from django.conf.urls import (
    include,
    url,
)
from django.conf.urls.static import static
from django.contrib import admin

import firebot.views


urlpatterns = [
    url(r'^$', firebot.views.index, name='index'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^test-500/$', firebot.views.test_500),
    url(r'^emails/', include('fb_emails.urls')),
    url(r'^github/', include('fb_github.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
