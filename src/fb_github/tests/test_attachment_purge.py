from unittest import mock

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.shortcuts import reverse
from rest_framework.test import APITestCase

from fb_emails.models import Attachment
from fb_emails.tests.factories import IncomingMessageFactory
from fb_github.models import Issue, Repository
from fb_github.tests.factories import RepositoryFactory


class AttachmentPurgeTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='purge-admin')
        self.repo = RepositoryFactory.create()
        self.repo.admins.add(self.user)
        self.url = reverse('repository-purge-attachments', args=[self.repo.uuid])
        self.client.force_authenticate(self.user)
        self.storage = mock.Mock()
        patcher = mock.patch('fb_github.api.attachment_purge_storage', return_value=self.storage)
        patcher.start()
        self.addCleanup(patcher.stop)

    def purge(self, data=None):
        return self.client.post(self.url, {'through_id': None} if data is None else data, format='json')

    def attachments(self, count=1, repo=None):
        msg = IncomingMessageFactory.create()
        Issue.objects.create(msg=msg, repo=repo or self.repo, issue_number=1, body='', gh_data={})
        return [Attachment.objects.create(msg=msg, file='test/{}/{}'.format(msg.pk, i)) for i in range(count)]

    def test_batches_resume_and_preserve_new_and_other_repo_attachments(self):
        attachments = self.attachments(12)
        other = self.attachments(repo=RepositoryFactory.create())[0]
        first = self.purge()
        self.assertEqual(first.status_code, 202)
        self.assertEqual(first.data, {'through_id': attachments[-1].pk})
        self.assertEqual(self.storage.delete.call_count, 10)
        new = self.attachments()[0]

        second = self.purge(first.data)
        self.assertEqual(second.status_code, 204)
        self.assertEqual(self.storage.delete.call_count, 12)
        self.assertCountEqual(Attachment.objects.values_list('pk', flat=True), [other.pk, new.pk])
        # Repeating a completed batch does not expand its cutoff.
        self.assertEqual(self.purge(first.data).status_code, 204)
        self.assertEqual(self.storage.delete.call_count, 12)

    def test_slow_delete_ends_batch_and_keeps_remaining_rows(self):
        attachments = self.attachments(3)
        with mock.patch('fb_github.api.monotonic', side_effect=[0, 0, 5]):
            response = self.purge()
        self.assertEqual(response.status_code, 202)
        self.storage.delete.assert_called_once_with(attachments[0].file.name)
        self.assertEqual(Attachment.objects.count(), 2)

    def test_storage_failure_stops_and_keeps_failed_and_later_files_for_retry(self):
        attachments = self.attachments(3)
        self.storage.delete.side_effect = [None, OSError('storage unavailable')]
        with self.assertRaises(OSError):
            self.purge()
        self.assertEqual(self.storage.delete.call_count, 2)
        self.assertFalse(Attachment.objects.filter(pk=attachments[0].pk).exists())
        for attachment in attachments[1:]:
            attachment.refresh_from_db()
            self.assertTrue(attachment.file.name)
        self.storage.delete.side_effect = None
        self.assertEqual(self.purge().status_code, 204)
        self.assertFalse(Attachment.objects.exists())

    def test_database_failure_does_not_clear_file_reference(self):
        attachment = self.attachments()[0]
        name = attachment.file.name
        with mock.patch.object(Attachment, 'delete', side_effect=DatabaseError('database unavailable')):
            with self.assertRaises(DatabaseError):
                self.purge()
        attachment.refresh_from_db()
        self.assertEqual(attachment.file.name, name)
        self.assertEqual(self.purge().status_code, 204)

    def test_concurrent_delete_does_not_recreate_attachment(self):
        attachment = self.attachments()[0]
        self.storage.delete.side_effect = lambda name: Attachment.objects.filter(pk=attachment.pk).delete()
        self.assertEqual(self.purge().status_code, 204)
        self.assertFalse(Attachment.objects.exists())

    def test_empty_repository_finishes_without_storage_delete(self):
        self.assertEqual(self.purge().status_code, 204)
        self.storage.delete.assert_not_called()

    def test_authentication_and_repository_admin_required_on_every_batch(self):
        attachment = self.attachments()[0]
        self.client.force_authenticate(None)
        self.assertEqual(self.purge().status_code, 403)
        outsider = get_user_model().objects.create_user(username='outsider', is_staff=True)
        self.client.force_authenticate(outsider)
        self.assertEqual(self.purge({'through_id': attachment.pk}).status_code, 404)
        self.client.force_authenticate(self.user)
        self.repo.admins.remove(self.user)
        self.assertEqual(self.purge({'through_id': attachment.pk}).status_code, 404)
        self.storage.delete.assert_not_called()
        self.assertTrue(Attachment.objects.filter(pk=attachment.pk).exists())

    def test_inactive_repository_cannot_be_purged(self):
        self.attachments()
        self.repo.status = Repository.Status.PendingInviterApproval
        self.repo.save()
        self.assertEqual(self.purge().status_code, 404)
        self.storage.delete.assert_not_called()

    def test_invalid_cutoff_does_not_delete_anything(self):
        self.attachments()
        for value in ['bad', -1, 1.5, 2 ** 64]:
            with self.subTest(value=value):
                self.assertEqual(self.purge({'through_id': value}).status_code, 400)
        self.storage.delete.assert_not_called()

    def test_old_client_cannot_mistake_a_partial_purge_for_completion(self):
        self.attachments(12)
        self.assertEqual(self.purge({}).status_code, 400)
        self.storage.delete.assert_not_called()
        self.assertEqual(Attachment.objects.count(), 12)
