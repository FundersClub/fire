from django.conf import settings
from django.conf.urls import url

from fb_emails import views


app_name = 'fb_emails'
urlpatterns = [
    url(r'^sendgrid/{}/parse/$'.format(settings.SENDGRID_WEBHOOK_SECRET), views.SendGridParseView.as_view(), name='sendgrid-webhook-parse'),
]
