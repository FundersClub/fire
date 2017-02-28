from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

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
        url = reverse('repository-detail', args=[self.repo1.id])

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

        # Only email_slug should be updateable
        orig_data = dict(resp.data)
        new_data = dict(resp.data)
        for k in new_data.keys():
            new_data[k] = 'lol'

        resp = self.client.put(url, new_data)

        self.assertEqual(resp.data['email_slug'], 'lol')

        resp.data['email_slug'] = orig_data['email_slug']
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
                'repo': 'http://testserver/api/github/repository/{}/'.format(self.repo1.id),
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
            'repo': reverse('repository-detail', args=[self.repo2.id]),
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
            'repo': reverse('repository-detail', args=[self.repo1.id]),
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.data,
            {'non_field_errors': ['The fields repo, email must make a unique set.']}
        )

        # Create an email map on an unrelated repo and then attempt to use this on
        # repo1, which should work.
        self.repo2.emailmap_set.create(email='test@me.com', login='test')
        resp = self.client.post(url, data={
            'email': 'test@me.com',
            'login': 'woo',
            'repo': reverse('repository-detail', args=[self.repo1.id]),
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # And trying again should fail
        resp = self.client.post(url, data={
            'email': 'test@me.com',
            'login': 'woo',
            'repo': reverse('repository-detail', args=[self.repo1.id]),
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
                            'repo': 'http://testserver/api/github/repository/{}/'.format(self.repo1.id),
                            'url': 'http://testserver/api/github/email-map/{}/'.format(self.repo1.emailmap_set.get().id),
                        },
                    ],
                    'email_slug': self.repo1.email_slug,
                    'login': self.repo1.login,
                    'name': self.repo1.name,
                    'status': 'active',
                    'url': 'http://testserver/api/github/repository/{}/'.format(self.repo1.id),
                    'urls': {
                        'purge_attachments': 'http://testserver/api/github/repository/{}/purge_attachments/'.format(self.repo1.id),
                    },
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
                    'email_slug': self.repo2.email_slug,
                    'login': self.repo2.login,
                    'name': self.repo2.name,
                    'status': 'active',
                    'url': 'http://testserver/api/github/repository/{}/'.format(self.repo2.id),
                    'urls': {
                        'purge_attachments': 'http://testserver/api/github/repository/{}/purge_attachments/'.format(self.repo2.id),
                    },

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
