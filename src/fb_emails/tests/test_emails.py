import datetime
import os
import re

from django.conf import settings
from django.core import mail
from django.db import connection
from django.test import (
    TestCase,
    TransactionTestCase,
)
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from fb_emails.models import IncomingMessage
from fb_emails.tasks import (
    process_incoming_message,
    sanitize_old_emails,
)
from fb_emails.tests.factories import IncomingMessageFactory
from fb_github.tests.factories import RepositoryFactory
from fb_github.tests.mocks import mock_github_api
from fb_github.utils import check_associate_email_token
from firebot.tests import RequestsMockMixin
from firebot.tests.factories import UserFactory


class SendGridParseTestCase(RequestsMockMixin, TransactionTestCase):
    def test_parse_unrecognized(self):
        resp = self.client.generic('POST',
            reverse('fb_emails:sendgrid-webhook-parse'),
            open(os.path.join(os.path.dirname(__file__), 'data', 'sendgrid-parse-with-attachment.txt'), 'rb').read(),
            content_type='multipart/form-data; boundary=xYzZY',
        )
        self.assertEqual(resp.status_code, 200)

        msg = IncomingMessage.objects.get()
        self.assertEqual(msg.attachment_set.count(), 2)
        self.assertEqual(msg.from_email, 'eran@fundersclub.com')
        self.assertEqual(msg.from_name, 'Eran Rundstein')
        self.assertEqual(msg.status, IncomingMessage.Status.UnrecognizedUsername)
        self.assertEqual(msg.subject, 'Attachment test')
        self.assertEqual(msg.to_email, 'test@fire.fundersclub.com')
        self.assertIsNotNone(msg.processed_at)

        for attachment in msg.attachment_set.all():
            self.assertTrue(str(msg.uuid) in attachment.file.name)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Re: Attachment test')
        self.assertTrue(
            'I do not recognize the e-mail address test@{}. Have you added fire (@{}) to your repository?'.format(settings.EMAIL_DOMAIN, settings.GITHUB_BOT_USERNAME)
            in mail.outbox[0].body
        )

    @mock_github_api
    def test_parse_recognized_attachments(self):
        RepositoryFactory.create(email_slug='test', login='firebot-test', name='Hello-World')
        resp = self.client.generic('POST',
            reverse('fb_emails:sendgrid-webhook-parse'),
            open(os.path.join(os.path.dirname(__file__), 'data', 'sendgrid-parse-with-attachment.txt'), 'rb').read(),
            content_type='multipart/form-data; boundary=xYzZY',
        )
        self.assertEqual(resp.status_code, 200)

        msg = IncomingMessage.objects.get()
        self.assertEqual(msg.attachment_set.count(), 2)
        self.assertEqual(msg.issue.issue_number, 1347)
        self.assertEqual(msg.status, IncomingMessage.Status.Processed)
        self.assertIsNotNone(msg.processed_at)

        for attachment in msg.attachment_set.all():
            self.assertTrue(attachment.file.url in msg.issue.body)

    @mock_github_api
    def test_parse_recognized_complex_html(self):
        RepositoryFactory.create(email_slug='test', login='firebot-test', name='Hello-World')
        resp = self.client.generic('POST',
            reverse('fb_emails:sendgrid-webhook-parse'),
            open(os.path.join(os.path.dirname(__file__), 'data', 'sendgrid-parse-from-sentry.txt'), 'rb').read(),
            content_type='multipart/form-data; boundary=xYzZY',
        )
        self.assertEqual(resp.status_code, 200)

        msg = IncomingMessage.objects.get()
        self.assertEqual(msg.attachment_set.count(), 0)
        self.assertEqual(msg.issue.issue_number, 1347)
        self.assertEqual(msg.status, IncomingMessage.Status.Processed)
        self.assertIsNotNone(msg.processed_at)
        self.assertTrue('Sent by {} ({})'.format(msg.from_name, msg.from_email) in msg.issue.body)

        test_text = r"""
\---------- Forwarded message ----------
From: **Sentry** <[noreply@md.getsentry.com](mailto:noreply@md.getsentry.com)>
Date: Sat, Feb 18, 2017 at 8:54 PM
Subject: [FundersClub Production] error: ReferenceError: clearOverlappingSelection is not defined
To: [eran@fundersclub.com](mailto:eran@fundersclub.com)
__
New alert from FundersClub Production.
[View on Sentry](https://sentry.io/)
#  [![Sentry](https://a0wx592cvgzripj.global.ssl.fastly.net/_static/e445fa38a26eeda40957d45e83ffe5b9/sentry/images/email/sentry_logo_full.png)](https://sentry.io)
---
##  New alert from [FundersClub Production](https://sentry.io/)
ID: b162081f6c7a4d29aa36050a275751f1"""
        body = '\n'.join(
            line.strip() for line in msg.issue.body.splitlines() if line.strip()
        )
        self.assertTrue(test_text in body)


class EmailsTestCase(RequestsMockMixin, TestCase):
    @mock_github_api
    def test_association_email(self):
        # Repo we'll be testing against (IncomingMessageFactory defaults to fake@)
        repo = RepositoryFactory.create(email_slug='fake', login='firebot-test', name='Hello-World')

        # This repo shouldn't affect the association because the slug is different
        repo2 = RepositoryFactory.create()
        repo2.emailmap_set.create(email='who@dat.com', login='whatever')

        # First time we send from this address should trigger an email
        msg = IncomingMessageFactory.create(from_email='who@dat.com')
        process_incoming_message.delay(msg.id)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Re: ' + msg.subject)
        self.assertTrue('Congratulations! You just created your first issue using fire.' in mail.outbox[0].body)

        expected_url = settings.BASE_URL + '/associate-email/{}/'.format(msg.uuid)
        self.assertTrue(expected_url in mail.outbox[0].body)

        # The link carries a signed token for this message's sender
        token = re.search(re.escape(expected_url) + r'([^/"]+)/', mail.outbox[0].body).group(1)
        self.assertTrue(check_associate_email_token(msg, token))
        del mail.outbox[:]

        # Send another message, we shouldn't receive an email this time unless it's from a new address
        msg = IncomingMessageFactory.create(from_email='who@dat.com')
        process_incoming_message.delay(msg.id)

        self.assertEqual(len(mail.outbox), 0)

        msg = IncomingMessageFactory.create(from_email='oh@snap.com')
        process_incoming_message.delay(msg.id)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Re: ' + msg.subject)
        self.assertTrue('Congratulations! You just created your first issue using fire.' in mail.outbox[0].body)

        expected_url = settings.BASE_URL + '/associate-email/{}/'.format(msg.uuid)
        self.assertTrue(expected_url in mail.outbox[0].body)
        del mail.outbox[:]

        # Send a message from an address that is mapped on this repo
        map_entry = repo.emailmap_set.create(email='le@lenny.com', login='lenny')

        msg = IncomingMessageFactory.create(from_email='le@lenny.com')
        process_incoming_message.delay(msg.id)

        self.assertEqual(len(mail.outbox), 0)

        # Delete the map entry, still no emails should go because we already got an email from this user
        map_entry.delete()

        msg = IncomingMessageFactory.create(from_email='le@lenny.com')
        process_incoming_message.delay(msg.id)

        self.assertEqual(len(mail.outbox), 0)

        # Send an email to the other repo, this should trigger an email
        repo2_email = '{}@{}'.format(repo2.email_slug, settings.EMAIL_DOMAIN)
        msg = IncomingMessageFactory.create(
            from_email='le@lenny.com',
            to_email=repo2_email,
        )
        process_incoming_message.delay(msg.id)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Re: ' + msg.subject)
        self.assertTrue('Congratulations! You just created your first issue using fire.' in mail.outbox[0].body)

        expected_url = settings.BASE_URL + '/associate-email/{}/'.format(msg.uuid)
        self.assertTrue(expected_url in mail.outbox[0].body)
        del mail.outbox[:]

        # Deleting all emails from this address and sending again should trigger the email
        IncomingMessage.objects.filter(from_email='le@lenny.com').delete()

        msg = IncomingMessageFactory.create(from_email='le@lenny.com')
        process_incoming_message.delay(msg.id)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Re: ' + msg.subject)
        self.assertTrue('Congratulations! You just created your first issue using fire.' in mail.outbox[0].body)

        expected_url = settings.BASE_URL + '/associate-email/{}/'.format(msg.uuid)
        self.assertTrue(expected_url in mail.outbox[0].body)
        del mail.outbox[:]

    def test_sanitize_old_emails(self):
        sanitize_txt = '<redacted>'

        # Create two test emails
        msg1 = IncomingMessageFactory.create(status=IncomingMessage.Status.Processed)
        msg2 = IncomingMessageFactory.create(status=IncomingMessage.Status.Processed)

        self.assertNotEqual(msg1.subject, sanitize_txt)
        self.assertNotEqual(msg1.body_html, sanitize_txt)
        self.assertNotEqual(msg1.body_text, sanitize_txt)

        self.assertNotEqual(msg2.subject, sanitize_txt)
        self.assertNotEqual(msg2.body_html, sanitize_txt)
        self.assertNotEqual(msg2.body_text, sanitize_txt)

        # Messages are not old enough so nothing should happen
        sanitize_old_emails.delay()
        msg1.refresh_from_db()
        msg2.refresh_from_db()

        self.assertNotEqual(msg1.subject, sanitize_txt)
        self.assertNotEqual(msg1.body_html, sanitize_txt)
        self.assertNotEqual(msg1.body_text, sanitize_txt)

        self.assertNotEqual(msg2.subject, sanitize_txt)
        self.assertNotEqual(msg2.body_html, sanitize_txt)
        self.assertNotEqual(msg2.body_text, sanitize_txt)

        # Make msg1 old enough so it should get sanitized
        msg1.created_at -= datetime.timedelta(days=7)
        msg1.save()

        sanitize_old_emails.delay()
        msg1.refresh_from_db()
        msg2.refresh_from_db()

        self.assertEqual(msg1.subject, sanitize_txt)
        self.assertEqual(msg1.body_html, sanitize_txt)
        self.assertEqual(msg1.body_text, sanitize_txt)

        self.assertNotEqual(msg2.subject, sanitize_txt)
        self.assertNotEqual(msg2.body_html, sanitize_txt)
        self.assertNotEqual(msg2.body_text, sanitize_txt)

    def test_sanitize_old_emails_uses_one_query(self):
        sanitize_txt = '<redacted>'
        batch_size = 12
        old = timezone.now() - datetime.timedelta(days=8)
        messages = []
        for index in range(batch_size):
            status = (
                IncomingMessage.Status.UnrecognizedUsername
                if index == 0 else IncomingMessage.Status.Processed
            )
            msg = IncomingMessageFactory.create(
                status=status,
                body_html='<p>secret {}</p>'.format(index),
                body_text='secret body {}'.format(index),
                subject='secret subject {}'.format(index),
                from_email='sender{}@example.com'.format(index),
                from_name='Sender {}'.format(index),
                to_email='repo@{}'.format(settings.EMAIL_DOMAIN),
                original_post_data={
                    'html': '<p>secret {}</p>'.format(index),
                    'text': 'secret body {}'.format(index),
                    'subject': 'secret subject {}'.format(index),
                    'envelope': '{"to":["reader@example.com"]}',
                    'from': 'Sender <reader@example.com>',
                    'marker': index,
                },
                spam_score='1.2500',
            )
            IncomingMessage.objects.filter(pk=msg.pk).update(created_at=old, processed_at=old)
            msg.refresh_from_db()
            messages.append(msg)

        blank_post = IncomingMessageFactory.create(
            status=IncomingMessage.Status.Processed,
            body_html='<p>only columns</p>',
            body_text='only columns',
            subject='only columns',
            original_post_data={},
        )
        IncomingMessage.objects.filter(pk=blank_post.pk).update(created_at=old)

        young = IncomingMessageFactory.create(
            status=IncomingMessage.Status.Processed,
            body_html='<p>still new</p>',
            body_text='still new',
            subject='still new',
            original_post_data={'text': 'still new', 'marker': 'young'},
        )
        pending = IncomingMessageFactory.create(
            status=IncomingMessage.Status.Pending,
            body_text='keep pending',
            subject='keep pending',
            original_post_data={'text': 'keep pending', 'marker': 'pending'},
        )
        IncomingMessage.objects.filter(pk=pending.pk).update(created_at=old)
        already = IncomingMessageFactory.create(
            status=IncomingMessage.Status.Sanitized,
            body_html=sanitize_txt,
            body_text=sanitize_txt,
            subject=sanitize_txt,
            original_post_data={
                'html': sanitize_txt,
                'text': sanitize_txt,
                'subject': sanitize_txt,
                'marker': 'already',
            },
        )
        IncomingMessage.objects.filter(pk=already.pk).update(created_at=old)

        with CaptureQueriesContext(connection) as captured:
            sanitize_old_emails()

        query_sql = [query['sql'] for query in captured]
        self.assertEqual(
            len(query_sql),
            1,
            'expected one cleanup statement, ran {}:\n{}'.format(
                len(query_sql),
                '\n'.join(query_sql),
            ),
        )
        self.assertTrue(query_sql[0].lstrip().upper().startswith('UPDATE'))

        for msg in messages:
            before_email = msg.from_email
            before_name = msg.from_name
            before_to = msg.to_email
            before_uuid = msg.uuid
            before_spam = msg.spam_score
            before_processed = msg.processed_at
            before_created = msg.created_at
            marker = msg.original_post_data['marker']
            msg.refresh_from_db()
            self.assertEqual(msg.status, IncomingMessage.Status.Sanitized)
            self.assertEqual(msg.body_html, sanitize_txt)
            self.assertEqual(msg.body_text, sanitize_txt)
            self.assertEqual(msg.subject, sanitize_txt)
            self.assertEqual(msg.original_post_data['html'], sanitize_txt)
            self.assertEqual(msg.original_post_data['text'], sanitize_txt)
            self.assertEqual(msg.original_post_data['subject'], sanitize_txt)
            self.assertEqual(msg.original_post_data['envelope'], '{"to":["reader@example.com"]}')
            self.assertEqual(msg.original_post_data['from'], 'Sender <reader@example.com>')
            self.assertEqual(msg.original_post_data['marker'], marker)
            self.assertEqual(msg.from_email, before_email)
            self.assertEqual(msg.from_name, before_name)
            self.assertEqual(msg.to_email, before_to)
            self.assertEqual(msg.uuid, before_uuid)
            self.assertEqual(msg.spam_score, before_spam)
            self.assertEqual(msg.processed_at, before_processed)
            self.assertEqual(msg.created_at, before_created)

        blank_post.refresh_from_db()
        self.assertEqual(blank_post.status, IncomingMessage.Status.Sanitized)
        self.assertEqual(blank_post.body_html, sanitize_txt)
        self.assertEqual(blank_post.body_text, sanitize_txt)
        self.assertEqual(blank_post.subject, sanitize_txt)
        self.assertEqual(blank_post.original_post_data, {
            'html': sanitize_txt,
            'text': sanitize_txt,
            'subject': sanitize_txt,
        })

        young.refresh_from_db()
        self.assertEqual(young.status, IncomingMessage.Status.Processed)
        self.assertEqual(young.body_text, 'still new')
        self.assertEqual(young.subject, 'still new')
        self.assertEqual(young.original_post_data, {'text': 'still new', 'marker': 'young'})

        pending.refresh_from_db()
        self.assertEqual(pending.status, IncomingMessage.Status.Pending)
        self.assertEqual(pending.body_text, 'keep pending')
        self.assertEqual(pending.original_post_data['text'], 'keep pending')

        already.refresh_from_db()
        self.assertEqual(already.status, IncomingMessage.Status.Sanitized)
        self.assertEqual(already.original_post_data['marker'], 'already')

    @mock_github_api
    def test_issue_create_error(self):
        # Hack to replace the issue creation API with one that fails
        self.requests_mock._adapter._matchers = [
            m for m in self.requests_mock._adapter._matchers
            if m._url != 'https://api.github.com/repos/firebot-test/Hello-World/issues'
        ]

        self.requests_mock.register_uri(
            'POST',
            'https://api.github.com/repos/firebot-test/Hello-World/issues',
            text='{}',
            status_code=404,
        )

        # Repo we'll be testing against (IncomingMessageFactory defaults to fake@)
        repo = RepositoryFactory.create(email_slug='fake', login='firebot-test', name='Hello-World')

        # Ensure we have an admin on this rpeo
        repo.admins.add(UserFactory.create())

        # Create and process message
        msg = IncomingMessageFactory.create(from_email='who@dat.com')
        process_incoming_message.delay(msg.id)

        self.assertTrue(msg.from_email in mail.outbox[0].body)
        self.assertTrue(repo.email in mail.outbox[0].body)
