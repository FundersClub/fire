from django.conf import settings
from django.urls import re_path

from fb_emails import views


app_name = 'fb_emails'
urlpatterns = [
    re_path(r'^sendgrid/{}/parse/$'.format(settings.SENDGRID_WEBHOOK_SECRET), views.SendGridParseView.as_view(), name='sendgrid-webhook-parse'),
]
