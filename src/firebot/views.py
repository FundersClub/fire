import json
import os

from django.conf import settings
from django.http import HttpResponse

from fb_github.api import MeView


def test_500(request):
    raise Exception('test!')


def app_html(request):
    # Inject data into frontend.
    data_to_update = [
        ('#CONTACT_URL', settings.CONTACT_URL),
        ('#PRIVACY_POLICY_URL', settings.PRIVACY_POLICY_URL),
        ('#TERMS_OF_SERVICE_URL', settings.TERMS_OF_SERVICE_URL),
        ('window.ME_DATA = null;', 'window.ME_DATA = {};'.format(json.dumps(MeView.get_me_data(request))))
    ]

    buf = open(os.path.join(settings.STATIC_FRONTEND_ROOT, 'app.html')).read()
    for token, data in data_to_update:
        buf = buf.replace(token, data)

    return HttpResponse(buf)
