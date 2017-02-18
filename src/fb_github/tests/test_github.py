from django.test import TestCase

from firebot.tests import RequestsMockMixin
from fb_emails.tests.factories import IncomingMessageFactory
from fb_github.tests.mocks import mock_github_api
from fb_github.tests.factories import RepositoryFactory


class GitHubTestCase(RequestsMockMixin, TestCase):
    @mock_github_api
    def test_text(self):
        repo = RepositoryFactory.create(email_slug='test', login='firebot-test', name='Hello-World')

        # Test an issue from an unrecognized email address
        msg = IncomingMessageFactory.create()
        issue = repo.create_issue_from_incoming_msg(msg)
        self.assertTrue(msg.body_text in issue.body)
        self.assertTrue('sent by {} ({})'.format(msg.from_name, msg.from_email) in issue.body)

        # Add email to map and try again
        msg = IncomingMessageFactory.create()
        repo.emailmap_set.create(email=msg.from_email, login='lenny')
        issue = repo.create_issue_from_incoming_msg(msg)
        self.assertTrue(msg.body_text in issue.body)
        self.assertTrue('sent by @lenny ({})'.format(msg.from_email) in issue.body)
