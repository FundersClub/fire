from allauth.socialaccount.adapter import get_adapter as get_socialaccount_adapter
from django.contrib.auth import get_user_model
from django.test import (
    RequestFactory,
    TestCase,
)
from django.urls import reverse


class SignupTestCase(TestCase):
    def test_local_signup_closed(self):
        url = reverse('account_signup')

        resp = self.client.get(url)
        self.assertTemplateUsed(resp, 'account/signup_closed.html')

        resp = self.client.post(url, {
            'username': 'octocat',
            'email': 'octocat@example.com',
            'password1': 'correct-horse-battery-staple',
            'password2': 'correct-horse-battery-staple',
        })
        self.assertTemplateUsed(resp, 'account/signup_closed.html')
        self.assertFalse(get_user_model().objects.filter(username='octocat').exists())

    def test_github_signup_open(self):
        request = RequestFactory().get('/')
        self.assertTrue(get_socialaccount_adapter(request).is_open_for_signup(request, None))
