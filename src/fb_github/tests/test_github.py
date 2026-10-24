import datetime

from unittest import mock

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.shortcuts import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from firebot.tests import RequestsMockMixin
from fb_emails.tests.factories import IncomingMessageFactory
from fb_github.models import (
    EmailMap,
    Issue,
    Repository,
)
from fb_github.tasks import sanitize_old_issues
from fb_github.utils import (
    ASSOCIATE_EMAIL_TOKEN_MAX_AGE,
    ASSOCIATE_EMAIL_TOKEN_SALT,
    make_associate_email_token,
)
from fb_github.tests.factories import RepositoryFactory
from fb_github.tests.mocks import mock_github_api


class GitHubTestCase(RequestsMockMixin, TestCase):
    @mock_github_api
    def test_text(self):
        repo = RepositoryFactory.create(email_slug='test', login='firebot-test', name='Hello-World')

        # Test an issue from an unrecognized email address
        msg = IncomingMessageFactory.create()
        issue = repo.create_issue_from_incoming_msg(msg)
        self.assertTrue(msg.body_text in issue.body)
        self.assertTrue('Sent by {} ({})'.format(msg.from_name, msg.from_email) in issue.body)

        # Add email to map and try again
        msg = IncomingMessageFactory.create()
        repo.emailmap_set.create(email=msg.from_email, login='lenny')
        issue = repo.create_issue_from_incoming_msg(msg)
        self.assertTrue(msg.body_text in issue.body)
        self.assertTrue('Sent by @lenny ({})'.format(msg.from_email) in issue.body)

    @mock_github_api
    def test_sanitize_old_issues(self):
        repo = RepositoryFactory.create(email_slug='test', login='firebot-test', name='Hello-World')
        sanitize_txt = '<redacted>'

        msg1 = IncomingMessageFactory.create()
        issue1 = repo.create_issue_from_incoming_msg(msg1)

        msg2 = IncomingMessageFactory.create()
        issue2 = repo.create_issue_from_incoming_msg(msg2)

        self.assertNotEqual(issue1.body, sanitize_txt)
        self.assertNotEqual(issue1.gh_data, {})

        self.assertNotEqual(issue2.body, sanitize_txt)
        self.assertNotEqual(issue2.gh_data, {})

        # Run task, nothing interesting should happen
        sanitize_old_issues.delay()
        issue1.refresh_from_db()
        issue2.refresh_from_db()

        self.assertNotEqual(issue1.body, sanitize_txt)
        self.assertNotEqual(issue1.gh_data, {})

        self.assertNotEqual(issue2.body, sanitize_txt)
        self.assertNotEqual(issue2.gh_data, {})

        # Make issue1 old enough
        issue1.created_at -= datetime.timedelta(days=7)
        issue1.save()

        sanitize_old_issues.delay()
        issue1.refresh_from_db()
        issue2.refresh_from_db()

        self.assertEqual(issue1.body, sanitize_txt)
        self.assertEqual(issue1.gh_data, {})

        self.assertNotEqual(issue2.body, sanitize_txt)
        self.assertNotEqual(issue2.gh_data, {})


class GitHubAPITestCase(RequestsMockMixin, APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username='user1')
        self.repo1 = RepositoryFactory.create()
        self.repo1.admins.add(self.user1)
        self.repo1.emailmap_set.create(
            email='a@b.com',
            login='lenny',
        )

        self.user2 = get_user_model().objects.create_user(username='user2')
        self.repo2 = RepositoryFactory.create()
        self.repo2.admins.add(self.user2)

        self.user3 = get_user_model().objects.create_user(username='user3')

    def test_repo(self):
        url = reverse('repository-detail', args=[self.repo1.uuid])

        # Should 403 on unauthenticated user
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Should 404 on the wrong user
        self.client.force_authenticate(user=self.user2)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Should work on the correct user
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Only soem fields should be updateable
        orig_data = dict(resp.data)
        new_data = dict(resp.data)
        for k in new_data.keys():
            if k == 'include_sender_email_in_issue':
                new_data[k] = 'false'
            else:
                new_data[k] = 'lol'

        resp = self.client.put(url, new_data)

        self.assertEqual(resp.data['email_slug'], 'lol')
        self.assertEqual(resp.data['include_sender_email_in_issue'], False)

        resp.data['email'] = orig_data['email']
        resp.data['email_slug'] = orig_data['email_slug']
        resp.data['include_sender_email_in_issue'] = orig_data['include_sender_email_in_issue']
        self.assertEqual(resp.data, orig_data)

        # Changing to a slug that's already in use, empty or banned should fail
        orig_data['email_slug'] = self.repo2.email_slug
        resp = self.client.put(url, orig_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {'email_slug': ['repository with this email slug already exists.']})

        orig_data['email_slug'] = ''
        resp = self.client.put(url, orig_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {'email_slug': ['This field may not be blank.']})

        orig_data['email_slug'] = 'support'
        resp = self.client.put(url, orig_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {'email_slug': ['"support" is not permitted.']})

        # For now, delete doesn't work and neither does creating a new repo this way
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        resp = self.client.post(reverse('repository-list'))
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_email_map(self):
        url = reverse('emailmap-list')

        # No go if not logged in
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Should only see ones we have access to
        self.client.force_authenticate(user=self.user2)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

        self.client.force_authenticate(user=self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [
            {
                'email': 'a@b.com',
                'login': 'lenny',
                'repo': 'http://testserver/api/github/repository/{}/'.format(self.repo1.uuid),
                'url': 'http://testserver/api/github/email-map/{}/'.format(self.repo1.emailmap_set.get().id),
            },
        ])

        # Try to create an email map without the required data
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.data,
            {'email': ['This field is required.'], 'login': ['This field is required.'], 'repo': ['This field is required.']},
        )

        # Try to create an email map pointing to a repo we don't have access to
        resp = self.client.post(url, data={
            'email': 'test@me.com',
            'login': 'woo',
            'repo': reverse('repository-detail', args=[self.repo2.uuid]),
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.data,
            {'repo': ['Invalid hyperlink - Object does not exist.']}
        )

        # Try to create an email map for an email that already exists
        resp = self.client.post(url, data={
            'email': self.repo1.emailmap_set.get().email,
            'login': 'woo',
            'repo': reverse('repository-detail', args=[self.repo1.uuid]),
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.data,
            {'non_field_errors': ['Email address is already in use.']}
        )

        # Create an email map on an unrelated repo and then attempt to use this on
        # repo1, which should work.
        self.repo2.emailmap_set.create(email='test@me.com', login='test')
        resp = self.client.post(url, data={
            'email': 'test@me.com',
            'login': 'woo',
            'repo': reverse('repository-detail', args=[self.repo1.uuid]),
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # And trying again should fail
        resp = self.client.post(url, data={
            'email': 'test@me.com',
            'login': 'woo',
            'repo': reverse('repository-detail', args=[self.repo1.uuid]),
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me(self):
        url = reverse('fb-github-me')

        # Test unauthenticated request
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {'is_authenticated': False})

        # Test the first user
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {
            'repositories': [
                {
                    'emailmap_set': [
                        {
                            'email': 'a@b.com',
                            'login': 'lenny',
                            'repo': 'http://testserver/api/github/repository/{}/'.format(self.repo1.uuid),
                            'url': 'http://testserver/api/github/email-map/{}/'.format(self.repo1.emailmap_set.get().id),
                        },
                    ],
                    'email': self.repo1.email,
                    'email_domain': settings.EMAIL_DOMAIN,
                    'email_slug': self.repo1.email_slug,
                    'full_name': self.repo1.full_name,
                    'inviter_login': self.repo1.inviter_login,
                    'login': self.repo1.login,
                    'name': self.repo1.name,
                    'status': 'active',
                    'url': 'http://testserver/api/github/repository/{}/'.format(self.repo1.uuid),
                    'urls': {
                        'github': self.repo1.gh_url,
                        'emailmap_add': 'http://testserver/api/github/email-map/',
                        'purge_attachments': 'http://testserver/api/github/repository/{}/purge_attachments/'.format(self.repo1.uuid),
                    },
                    'uuid': str(self.repo1.uuid),
                    'include_sender_email_in_issue': True,
                },
            ],
            'username': self.user1.username,
            'is_authenticated': True,
            'urls': {
                'logout': 'http://testserver/accounts/logout/',
            },
        })

        # Test the second user
        self.client.force_authenticate(user=self.user2)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {
            'repositories': [
                {
                    'emailmap_set': [],
                    'email': self.repo2.email,
                    'email_domain': settings.EMAIL_DOMAIN,
                    'email_slug': self.repo2.email_slug,
                    'full_name': self.repo2.full_name,
                    'inviter_login': self.repo2.inviter_login,
                    'login': self.repo2.login,
                    'name': self.repo2.name,
                    'status': 'active',
                    'url': 'http://testserver/api/github/repository/{}/'.format(self.repo2.uuid),
                    'urls': {
                        'github': self.repo2.gh_url,
                        'emailmap_add': 'http://testserver/api/github/email-map/',
                        'purge_attachments': 'http://testserver/api/github/repository/{}/purge_attachments/'.format(self.repo2.uuid),
                    },
                    'uuid': str(self.repo2.uuid),
                    'include_sender_email_in_issue': True,
                },
            ],
            'username': self.user2.username,
            'is_authenticated': True,
            'urls': {
                'logout': 'http://testserver/accounts/logout/',
            },
        })

        # Test the third user
        self.client.force_authenticate(user=self.user3)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {
            'repositories': [],
            'username': self.user3.username,
            'is_authenticated': True,
            'urls': {
                'logout': 'http://testserver/accounts/logout/',
            },
        })

    def test_approve(self):
        # user1 is the GitHub account (id 1001, login octocat) that invited the bot
        self.repo1.inviter_login = 'octocat'
        self.repo1.original_invitation_data = {'inviter': {'id': 1001, 'login': 'octocat'}}
        self.repo1.status = Repository.Status.PendingAccept
        self.repo1.save()
        SocialAccount.objects.create(user=self.user1, provider='github', uid='1001')

        url = reverse('repository-approve', args=[self.repo1.uuid])

        # Anonymous users are rejected outright
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.repo1.refresh_from_db()
        self.assertEqual(self.repo1.status, Repository.Status.PendingAccept)

        # Try as the wrong user
        self.client.force_authenticate(user=self.user2)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {
            'full_name': '{}/{}'.format(self.repo1.login, self.repo1.name),
            'inviter_login': self.repo1.inviter_login,
            'login': self.repo1.login,
            'name': self.repo1.name,
            'status': 'pending-accept',
            'url': 'http://testserver/api/github/repository/{}/'.format(self.repo1.uuid),
        })

        # Try as the right user, but before the bot accepted the invite
        self.assertEqual(self.repo1.status, Repository.Status.PendingAccept)

        self.client.force_authenticate(user=self.user1)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {
            'emailmap_set': [
                {
                    'email': 'a@b.com',
                    'login': 'lenny',
                    'repo': 'http://testserver/api/github/repository/{}/'.format(self.repo1.uuid),
                    'url': 'http://testserver/api/github/email-map/{}/'.format(self.repo1.emailmap_set.get().id),
                },
            ],
            'email': self.repo1.email,
            'email_domain': settings.EMAIL_DOMAIN,
            'email_slug': self.repo1.email_slug,
            'full_name': self.repo1.full_name,
            'login': self.repo1.login,
            'inviter_login': self.repo1.inviter_login,
            'name': self.repo1.name,
            'status': 'pending-accept',
            'url': 'http://testserver/api/github/repository/{}/'.format(self.repo1.uuid),
            'urls': {
                'github': self.repo1.gh_url,
                'emailmap_add': 'http://testserver/api/github/email-map/',
                'purge_attachments': 'http://testserver/api/github/repository/{}/purge_attachments/'.format(self.repo1.uuid),
            },
            'uuid': str(self.repo1.uuid),
            'include_sender_email_in_issue': True,
        })

        # Switch to the correct state and try both users again
        self.repo1.status = Repository.Status.PendingInviterApproval
        self.repo1.save()

        self.client.force_authenticate(user=self.user2)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {
            'full_name': '{}/{}'.format(self.repo1.login, self.repo1.name),
            'inviter_login': self.repo1.inviter_login,
            'login': self.repo1.login,
            'name': self.repo1.name,
            'status': 'pending-inviter-approval',
            'url': 'http://testserver/api/github/repository/{}/'.format(self.repo1.uuid),
        })

        # A local account whose self-chosen username matches the inviter's
        # GitHub login must not be able to approve
        impostor = get_user_model().objects.create_user(username='octocat')
        self.client.force_authenticate(user=impostor)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'pending-inviter-approval')
        self.assertNotIn('emailmap_set', resp.data)

        # Nor can a different linked GitHub account
        other_gh = get_user_model().objects.create_user(username='other-gh')
        SocialAccount.objects.create(user=other_gh, provider='github', uid='2002')
        self.client.force_authenticate(user=other_gh)
        resp = self.client.post(url)
        self.assertEqual(resp.data['status'], 'pending-inviter-approval')

        self.repo1.refresh_from_db()
        self.assertEqual(self.repo1.status, Repository.Status.PendingInviterApproval)
        self.assertNotIn(impostor, self.repo1.admins.all())
        self.assertNotIn(other_gh, self.repo1.admins.all())

        self.client.force_authenticate(user=self.user1)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {
            'emailmap_set': [
                {
                    'email': 'a@b.com',
                    'login': 'lenny',
                    'repo': 'http://testserver/api/github/repository/{}/'.format(self.repo1.uuid),
                    'url': 'http://testserver/api/github/email-map/{}/'.format(self.repo1.emailmap_set.get().id),
                },
            ],
            'email': self.repo1.email,
            'email_domain': settings.EMAIL_DOMAIN,
            'email_slug': self.repo1.email_slug,
            'full_name': self.repo1.full_name,
            'inviter_login': self.repo1.inviter_login,
            'login': self.repo1.login,
            'name': self.repo1.name,
            'status': 'active',
            'url': 'http://testserver/api/github/repository/{}/'.format(self.repo1.uuid),
            'urls': {
                'github': self.repo1.gh_url,
                'emailmap_add': 'http://testserver/api/github/email-map/',
                'purge_attachments': 'http://testserver/api/github/repository/{}/purge_attachments/'.format(self.repo1.uuid),
            },
            'uuid': str(self.repo1.uuid),
            'include_sender_email_in_issue': True,
        })


@mock.patch('fb_github.api.update_issue_after_email_association')
class AssociateEmailAPITestCase(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(username='admin')
        self.repo = RepositoryFactory.create()
        self.repo.admins.add(self.admin)

        self.sender = get_user_model().objects.create_user(username='sender')
        self.attacker = get_user_model().objects.create_user(username='attacker')

        self.msg = IncomingMessageFactory.create(from_email='sender@example.com')
        self.issue = Issue.objects.create(
            body='', gh_data={}, issue_number=1, msg=self.msg, repo=self.repo,
        )
        self.token = make_associate_email_token(self.msg)

        self.plain_url = reverse('fb-github-associate-email', args=[self.msg.uuid])
        self.token_url = reverse('fb-github-associate-email-token', args=[self.msg.uuid, self.token])

    def test_raw_uuid_rejected(self, task_mock):
        # Knowing the message uuid alone is not enough, logged in or not
        self.assertEqual(self.client.get(self.plain_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.post(self.plain_url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.attacker)
        self.assertEqual(self.client.get(self.plain_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.post(self.plain_url).status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse(EmailMap.objects.exists())
        task_mock.delay.assert_not_called()

    def test_bad_tokens_rejected(self, task_mock):
        other_msg = IncomingMessageFactory.create(from_email='attacker@example.com')
        Issue.objects.create(body='', gh_data={}, issue_number=2, msg=other_msg, repo=self.repo)
        bad_tokens = [
            'garbage',
            self.token[:-2] + 'xx',
            # Valid token for a different message (the attacker's own)
            make_associate_email_token(other_msg),
            # Right payload, wrong salt
            signing.dumps({'msg': str(self.msg.uuid), 'email': self.msg.from_email}),
            # Right salt and message, but a different email address
            signing.dumps({'msg': str(self.msg.uuid), 'email': 'attacker@example.com'}, salt=ASSOCIATE_EMAIL_TOKEN_SALT),
        ]

        self.client.force_authenticate(user=self.attacker)
        for token in bad_tokens:
            url = reverse('fb-github-associate-email-token', args=[self.msg.uuid, token])
            self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND, token)
            self.assertEqual(self.client.post(url).status_code, status.HTTP_403_FORBIDDEN, token)

        # Expired token
        issued_at = datetime.datetime.now().timestamp() - ASSOCIATE_EMAIL_TOKEN_MAX_AGE - 60
        with mock.patch('django.core.signing.time.time', return_value=issued_at):
            old_token = make_associate_email_token(self.msg)
        url = reverse('fb-github-associate-email-token', args=[self.msg.uuid, old_token])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse(EmailMap.objects.exists())
        task_mock.delay.assert_not_called()

    def test_sender_with_token(self, task_mock):
        # Anonymous users can view the offer with a valid token, but not claim it
        resp = self.client.get(self.token_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['email'], 'sender@example.com')
        self.assertEqual(resp.data['url'], 'http://testserver' + self.token_url)
        self.assertEqual(self.client.post(self.token_url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.sender)
        resp = self.client.post(self.token_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['login'], 'sender')

        entry = self.repo.emailmap_set.get()
        self.assertEqual(entry.email, 'sender@example.com')
        self.assertEqual(entry.user, self.sender)
        task_mock.delay.assert_called_once_with(self.issue.id)

        # The same sender can retry a claim and requeue its issue update.
        resp = self.client.post(self.token_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(self.repo.emailmap_set.count(), 1)
        self.assertEqual(task_mock.delay.call_count, 2)

    def test_repo_admin_without_token(self, task_mock):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.plain_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['url'], 'http://testserver' + self.plain_url)

        resp = self.client.post(self.plain_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(self.repo.emailmap_set.get().login, 'admin')

    def test_admin_of_other_repo_rejected(self, task_mock):
        other_repo = RepositoryFactory.create()
        other_repo.admins.add(self.attacker)

        self.client.force_authenticate(user=self.attacker)
        self.assertEqual(self.client.post(self.plain_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(EmailMap.objects.exists())
