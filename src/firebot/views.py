import json
import os

from django.conf import settings
from django.http import HttpResponse

from fb_github.api import MeView


def test_500(request):
    raise Exception('test!')


def _escape_json_for_script(data):
    # Escape characters that could break out of a <script> block or terminate
    # the script element. json.dumps() defaults to ensure_ascii=True, so
    # U+2028/U+2029 are already escaped; <, >, & are ASCII and are not, so we
    # escape them here. Matches the scheme used by Django's json_script.
    return (
        json.dumps(data)
        .replace('<', '\\u003c')
        .replace('>', '\\u003e')
        .replace('&', '\\u0026')
    )


def app_html(request):
    # Inject data into frontend.
    data_to_update = [
        ('#CONTACT_URL', settings.CONTACT_URL),
        ('#PRIVACY_POLICY_URL', settings.PRIVACY_POLICY_URL),
        ('#TERMS_OF_SERVICE_URL', settings.TERMS_OF_SERVICE_URL),
        ('window.ME_DATA = null;', 'window.ME_DATA = {};'.format(_escape_json_for_script(MeView.get_me_data(request)))),
    ]

    buf = open(os.path.join(settings.STATIC_FRONTEND_ROOT, 'app.html')).read()
    for token, data in data_to_update:
        buf = buf.replace(token, data)

    return HttpResponse(buf)
