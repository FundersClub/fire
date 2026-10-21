from unittest.mock import patch

from django.core import mail
from django.test import SimpleTestCase, TestCase, override_settings

from fb_emails.models import IncomingMessage
from fb_emails.tasks import process_incoming_message
from fb_emails.tests.factories import IncomingMessageFactory
from fb_github.tests.factories import RepositoryFactory
from fb_github.tests.mocks import mock_github_api
from firebot.tests import RequestsMockMixin


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ReplyAddressTests(SimpleTestCase):
    def test_invalid_senders_skip_plain_and_html_replies(self):
        for address in ('', 'admin', 'name@example.com\nBcc: other@example.com'):
            for html in (False, True):
                with self.subTest(address=address, html=html):
                    msg = IncomingMessage(from_email=address, from_name='Sender')
                    with patch('fb_emails.models.render_to_string') as render:
                        self.assertEqual(msg.reply_from_template('unused', html=html), 0)
                    render.assert_not_called()
        self.assertEqual(len(mail.outbox), 0)

    def test_valid_sender_keeps_display_name_and_both_message_types(self):
        msg = IncomingMessage(from_email='sender@example.com', from_name='Schäfer', subject='Question')
        with patch('fb_emails.models.render_to_string', return_value='<p>Hello</p>'):
            msg.reply_from_template('unused')
            msg.reply_from_template('unused', html=True)
        self.assertEqual(len(mail.outbox), 2)
        for message in mail.outbox:
            self.assertEqual(message.to, ['"Schäfer" <sender@example.com>'])
            self.assertEqual(message.subject, 'Re: Question')
        self.assertEqual(mail.outbox[1].alternatives[0][1], 'text/html')

    def test_delivery_errors_for_valid_senders_still_raise(self):
        msg = IncomingMessage(from_email='sender@example.com', subject='Question')
        for html, target in ((False, 'fb_emails.models.send_mail'),
                             (True, 'fb_emails.models.EmailMultiAlternatives.send')):
            with self.subTest(html=html), patch('fb_emails.models.render_to_string', return_value='Hello'):
                with patch(target, side_effect=RuntimeError('provider failure')):
                    with self.assertRaisesRegex(RuntimeError, 'provider failure'):
                        msg.reply_from_template('unused', html=html)


class InvalidSenderProcessingTests(RequestsMockMixin, TestCase):
    def test_unknown_repository_finishes_without_replying_to_missing_sender(self):
        msg = IncomingMessageFactory.create(from_email='', from_name='Sender')
        process_incoming_message(msg.id)
        msg.refresh_from_db()
        self.assertEqual(msg.status, IncomingMessage.Status.UnrecognizedUsername)
        self.assertIsNotNone(msg.processed_at)
        self.assertEqual(len(mail.outbox), 0)

    @mock_github_api
    def test_created_issue_finishes_without_association_email_to_invalid_sender(self):
        RepositoryFactory.create(email_slug='fake', login='firebot-test', name='Hello-World')
        msg = IncomingMessageFactory.create(from_email='admin', from_name='Sender')
        process_incoming_message(msg.id)
        msg.refresh_from_db()
        self.assertEqual(msg.status, IncomingMessage.Status.Processed)
        self.assertEqual(msg.issue.issue_number, 1347)
        self.assertIsNotNone(msg.processed_at)
        self.assertEqual(len(mail.outbox), 0)
