from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework.test import APITestCase

from fb_emails.tests.factories import IncomingMessageFactory
from fb_github.models import Issue
from fb_github.tests.factories import RepositoryFactory
from firebot.tests import RequestsMockMixin


class EmailAssociationTests(RequestsMockMixin, APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='member')
        self.repo = RepositoryFactory.create()
        self.msg = IncomingMessageFactory.create()
        self.issue = Issue.objects.create(repo=self.repo, msg=self.msg, issue_number=1, gh_data={})
        self.url = reverse('fb-github-associate-email', args=[self.msg.uuid])

    @patch('fb_github.api.update_issue_after_email_association.delay')
    def test_repeat_association_returns_success_without_a_duplicate(self, update):
        self.client.force_authenticate(user=self.user)
        for _ in range(2):
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['login'], self.user.username)
        self.assertEqual(self.repo.emailmap_set.count(), 1)
        entry = self.repo.emailmap_set.get()
        self.assertEqual(entry.user_id, self.user.id)
        update.assert_called_with(self.issue.id)

    @patch('fb_github.api.update_issue_after_email_association.delay')
    def test_existing_mapping_to_another_login_is_not_overwritten(self, update):
        self.repo.emailmap_set.create(email=self.msg.from_email, login='someone-else')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.repo.emailmap_set.get().login, 'someone-else')
        update.assert_not_called()

    @patch('fb_github.api.update_issue_after_email_association.delay')
    def test_existing_mapping_to_same_login_is_accepted(self, update):
        self.repo.emailmap_set.create(email=self.msg.from_email, login=self.user.username)
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.post(self.url).status_code, 200)
        self.assertEqual(self.repo.emailmap_set.count(), 1)
        update.assert_called_once_with(self.issue.id)

    @patch('fb_github.api.update_issue_after_email_association.delay')
    def test_unauthenticated_request_cannot_associate_email(self, update):
        self.assertEqual(self.client.post(self.url).status_code, 403)
        self.assertEqual(self.repo.emailmap_set.count(), 0)
        update.assert_not_called()
