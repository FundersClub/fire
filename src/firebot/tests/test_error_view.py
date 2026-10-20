from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase

from firebot.views import test_500 as error_test_view


class ErrorTestViewAccessTests(SimpleTestCase):
    def request_for(self, user):
        request = RequestFactory().get('/test-500/')
        request.user = user
        return request

    def test_anonymous_request_does_not_raise(self):
        response = error_test_view(self.request_for(AnonymousUser()))
        self.assertEqual(response.status_code, 302)

    def test_regular_user_does_not_raise(self):
        response = error_test_view(self.request_for(SimpleNamespace(is_active=True, is_staff=False)))
        self.assertEqual(response.status_code, 302)

    def test_inactive_staff_does_not_raise(self):
        response = error_test_view(self.request_for(SimpleNamespace(is_active=False, is_staff=True)))
        self.assertEqual(response.status_code, 302)

    def test_active_staff_can_still_test_error_reporting(self):
        with self.assertRaisesRegex(Exception, 'test!'):
            error_test_view(self.request_for(SimpleNamespace(is_active=True, is_staff=True)))
