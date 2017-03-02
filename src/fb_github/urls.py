from django.conf.urls import url, include

from fb_github import views


app_name = 'fb_github'
urlpatterns = [
    url(r'^(?P<repo_login>[\w\d-]+)/(?P<repo_name>[\w\d-]+)/', include([
        url(r'^associate-email/(?P<msg_uuid>[\w\d-]+)/$', views.AssociateEmailView.as_view(), name='associate-email'),
    ])),
]
