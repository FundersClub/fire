from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework.test import APITestCase

from fb_emails.tests.factories import IncomingMessageFactory
from fb_github.models import Issue
from fb_github.tasks import update_issue_after_email_association
from fb_github.tests.factories import RepositoryFactory
from fb_github.utils import make_associate_email_token
from firebot.tests import RequestsMockMixin


class EmailAssociationTests(RequestsMockMixin, APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='member')
        self.repo = RepositoryFactory.create()
        self.msg = IncomingMessageFactory.create()
        self.issue = Issue.objects.create(repo=self.repo, msg=self.msg, issue_number=1, gh_data={})
        self.url = reverse(
            'fb-github-associate-email-token',
            args=[self.msg.uuid, make_associate_email_token(self.msg)],
        )

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
        self.assertEqual(update.call_count, 2)
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

    @patch('fb_github.api.update_issue_after_email_association.delay')
    def test_matching_login_owned_by_another_user_is_a_conflict(self, update):
        other_user = get_user_model().objects.create_user(username='other')
        entry = self.repo.emailmap_set.create(
            email=self.msg.from_email, login=self.user.username, user=other_user,
        )
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.post(self.url).status_code, 409)
        entry.refresh_from_db()
        self.assertEqual(entry.user_id, other_user.id)
        update.assert_not_called()

    @patch('fb_github.api.update_issue_after_email_association.delay')
    def test_retry_after_queue_failure_reuses_mapping_and_requeues(self, update):
        update.side_effect = [RuntimeError('queue unavailable'), None]
        self.client.force_authenticate(user=self.user)
        with self.assertRaisesRegex(RuntimeError, 'queue unavailable'):
            self.client.post(self.url)
        self.assertEqual(self.repo.emailmap_set.count(), 1)
        self.assertEqual(self.client.post(self.url).status_code, 200)
        self.assertEqual(self.repo.emailmap_set.count(), 1)
        self.assertEqual(update.call_count, 2)

    @patch('fb_github.api.update_issue_after_email_association.delay')
    def test_existing_mapping_does_not_bypass_authorization(self, update):
        self.repo.emailmap_set.create(
            email=self.msg.from_email, login=self.user.username, user=self.user,
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('fb-github-associate-email', args=[self.msg.uuid])
        self.assertEqual(self.client.post(url).status_code, 403)
        update.assert_not_called()

    @patch('fb_github.models.get_github_client')
    def test_repeated_issue_update_only_edits_sender_header_once(self, github):
        self.repo.emailmap_set.create(
            email=self.msg.from_email, login=self.user.username, user=self.user,
        )
        gh_issue = github.return_value.issue.return_value
        gh_issue.title = 'A question'
        gh_issue.body = 'Sent by {} ({})\n\nMessage body'.format(
            self.msg.from_name, self.msg.from_email,
        )

        def edit(title, body):
            gh_issue.body = body
            return True

        gh_issue.edit.side_effect = edit
        update_issue_after_email_association(self.issue.id)
        expected_body = 'Sent by {} (@{})\n\nMessage body'.format(
            self.msg.from_name, self.user.username,
        )
        self.assertEqual(gh_issue.body, expected_body)
        update_issue_after_email_association(self.issue.id)
        self.assertEqual(gh_issue.body, expected_body)
        gh_issue.edit.assert_called_once_with('A question', expected_body)
