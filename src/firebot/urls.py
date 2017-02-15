from django.conf.urls import url
from django.contrib import admin

import firebot.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test-500/$', firebot.views.test_500),
]
