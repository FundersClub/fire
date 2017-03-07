import json
import os

from django.conf import settings
from django.http import HttpResponse

from fb_github.api import MeView


def test_500(request):
    raise Exception('test!')


def app_html(request):
    buf = open(os.path.join(settings.STATIC_FRONTEND_ROOT, 'app.html')).read()
    me_data = MeView.get_me_data(request)
    buf = buf.replace(
        'window.ME_DATA = null;',
        'window.ME_DATA = {};'.format(json.dumps(me_data))
    )
    return HttpResponse(buf)
