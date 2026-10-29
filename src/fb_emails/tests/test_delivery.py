import datetime
import json
from pathlib import Path
from unittest.mock import patch

from django.core import mail
from django.test import TestCase
from django.utils import timezone
from requests.exceptions import ConnectionError

from fb_emails.models import IncomingMessage
from fb_emails.tasks import process_incoming_message, sanitize_old_emails
from fb_emails.tests.factories import IncomingMessageFactory
from fb_github.models import Issue
from fb_github.tests.factories import RepositoryFactory
from firebot.tests import RequestsMockMixin
from firebot.tests.factories import UserFactory


class DeliveryTests(RequestsMockMixin, TestCase):
    def setUp(self):
        self.repo = RepositoryFactory.create(email_slug='fake', login='firebot-test', name='Hello-World')
        self.repo.admins.add(UserFactory.create(email='admin@example.com'))
        self.msg = IncomingMessageFactory.create(
            subject='Original subject', body_text='Original body', body_html='<p>Original body</p>',
            original_post_data={'subject': 'Original subject', 'text': 'Original body', 'html': '<p>Original body</p>'},
        )
        self.repo_url = 'https://api.github.com/repos/firebot-test/Hello-World'
        self.issue_url = self.repo_url + '/issues'
        self.github_data = json.loads(
            (Path(__file__).parents[2] / 'fb_github/tests/data/github-repo.json').read_text()
        )
        self.github_data['archived'] = False
        self.requests_mock.get(self.repo_url, json=self.github_data)

    def assert_rejected(self, status, notice):
        with patch.object(IncomingMessage, 'reply_from_template') as reply:
            process_incoming_message(self.msg.id)
        reply.assert_not_called()
        self.msg.refresh_from_db()
        self.assertEqual(self.msg.status, status)
        self.assertIsNotNone(self.msg.processed_at)
        self.assertFalse(Issue.objects.exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['admin@example.com'])
        self.assertIn(notice, mail.outbox[0].body)
        self.assertIn(str(self.msg.uuid), mail.outbox[0].body)
        # Redelivery of the task must not repeat the provider call or notification.
        request_count = self.requests_mock.call_count
        process_incoming_message(self.msg.id)
        self.assertEqual(self.requests_mock.call_count, request_count)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(self.msg.body_text, 'Original body')
        self.assertEqual(self.msg.original_post_data['text'], 'Original body')

    def test_archived_repo_prevents_issue_post(self):
        self.github_data['archived'] = True
        self.requests_mock.get(self.repo_url, json=self.github_data)
        self.assert_rejected(IncomingMessage.Status.RepositoryArchived, 'archived and read-only')
        self.assertEqual([r.method for r in self.requests_mock.request_history], ['GET'])

    def test_archived_between_lookup_and_create(self):
        self.requests_mock.post(self.issue_url, status_code=403,
                                json={'message': 'Repository was archived so is read-only.'})
        self.assert_rejected(IncomingMessage.Status.RepositoryArchived, 'archived and read-only')
        self.assertEqual([r.method for r in self.requests_mock.request_history], ['GET', 'POST'])

    def test_explicit_body_length_rejection(self):
        self.requests_mock.post(self.issue_url, status_code=422, json={
            'message': 'Validation Failed', 'errors': [
                {'resource': 'Issue', 'field': 'body', 'code': 'custom', 'message': 'body is too long'},
                {'resource': 'Issue', 'field': 'body', 'code': 'custom',
                 'message': 'body is too long (maximum is 65536 characters)'},
            ],
        })
        self.assert_rejected(IncomingMessage.Status.IssueBodyTooLong, 'body is too long')
        posted = self.requests_mock.request_history[-1].json()
        self.assertIn('Original body', posted['body'])
        self.assertEqual(posted['title'], 'Original subject')

    def test_explicit_title_length_rejection(self):
        self.requests_mock.post(self.issue_url, status_code=422, json={
            'message': 'Validation Failed', 'errors': [
                {'resource': 'Issue', 'field': 'title', 'code': 'custom', 'message': 'title is too long'},
            ],
        })
        self.assert_rejected(IncomingMessage.Status.IssueTitleTooLong, 'title is too long')

    def test_other_github_errors_remain_visible(self):
        for status, details in [
            (403, {'message': 'Resource not accessible by integration'}),
            (422, {'message': 'Validation Failed'}),
            (422, {'message': 'Validation Failed', 'errors': 'unexpected shape'}),
            (422, {'message': 'Validation Failed', 'errors': [
                {'resource': 'Issue', 'field': 'body', 'code': 'custom', 'message': 'unrecognized PRIVATE value'},
            ]}),
            (500, {'message': 'Server error'}),
        ]:
            with self.subTest(status=status, details=details):
                self.msg.status = IncomingMessage.Status.Pending
                self.msg.save()
                mail.outbox.clear()
                self.requests_mock.post(self.issue_url, status_code=status, json=details)
                with self.assertLogs('fb_github.models', level='ERROR') as logs:
                    self.assert_rejected(IncomingMessage.Status.IssueError, 'check the error')
                record = logs.records[0]
                self.assertIsNotNone(record.exc_info)
                self.assertEqual(record.github_status, status)
                self.assertEqual(record.issue_title_length, len(self.msg.subject))
                self.assertNotIn('PRIVATE', repr(record.github_validation_fields))

    def test_transport_failure_stays_visible_without_automatic_retry(self):
        self.requests_mock.post(self.issue_url, exc=ConnectionError('connection lost'))
        with self.assertLogs('fb_github.models', level='ERROR') as logs:
            self.assert_rejected(IncomingMessage.Status.IssueError, 'response was lost')
        self.assertIsNotNone(logs.records[0].exc_info)
        self.assertEqual([r.method for r in self.requests_mock.request_history], ['GET', 'POST'])

    def test_notification_failure_does_not_lose_rejection_state_or_retry_issue(self):
        self.github_data['archived'] = True
        self.requests_mock.get(self.repo_url, json=self.github_data)
        with patch('fb_emails.tasks.send_mail', side_effect=RuntimeError('mail provider unavailable')):
            with self.assertRaisesRegex(RuntimeError, 'mail provider unavailable'):
                process_incoming_message(self.msg.id)
        self.msg.refresh_from_db()
        self.assertEqual(self.msg.status, IncomingMessage.Status.RepositoryArchived)
        process_incoming_message(self.msg.id)
        self.assertEqual(self.requests_mock.call_count, 1)
        self.assertFalse(Issue.objects.exists())

    def test_cleanup_keeps_pending_and_failed_mail(self):
        retained = [IncomingMessage.Status.Pending, IncomingMessage.Status.IssueError,
                    IncomingMessage.Status.RepositoryArchived, IncomingMessage.Status.IssueBodyTooLong,
                    IncomingMessage.Status.IssueTitleTooLong]
        for status in retained + [IncomingMessage.Status.Processed]:
            with self.subTest(status=status):
                msg = IncomingMessageFactory.create(status=status, body_text='keep me',
                                                    original_post_data={'text': 'keep me'})
                IncomingMessage.objects.filter(pk=msg.pk).update(created_at=timezone.now() - datetime.timedelta(days=8))
                sanitize_old_emails()
                msg.refresh_from_db()
                if status in retained:
                    self.assertEqual(msg.status, status)
                    self.assertEqual(msg.body_text, 'keep me')
                    self.assertEqual(msg.original_post_data, {'text': 'keep me'})
                else:
                    self.assertEqual(msg.status, IncomingMessage.Status.Sanitized)
                    self.assertEqual(msg.body_text, '<redacted>')
