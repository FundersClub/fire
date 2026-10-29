from botocore.config import Config
from botocore.exceptions import ClientError
from botocore.stub import Stubber
from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase
from storages.backends.s3 import S3Storage

from firebot.storages import attachment_purge_storage


class PurgeStorageTests(SimpleTestCase):
    def test_purge_uses_separate_client_with_short_waits_and_no_retries(self):
        storage = S3Storage(
            access_key='test-key', secret_key='test-secret', bucket_name='test-bucket',
            location='attachments', region_name='us-east-1',
            client_config=Config(connect_timeout=60, read_timeout=60, retries={'max_attempts': 4}),
        )
        original_client = storage.connection.meta.client
        purge = attachment_purge_storage(storage)
        client = purge.connection.meta.client
        self.assertIsNot(client, original_client)
        self.assertEqual(client.meta.config.connect_timeout, 2)
        self.assertEqual(client.meta.config.read_timeout, 3)
        self.assertEqual(client.meta.config.retries['total_max_attempts'], 1)
        self.assertEqual(original_client.meta.config.connect_timeout, 60)
        self.assertEqual(original_client.meta.config.read_timeout, 60)
        self.assertEqual(original_client.meta.config.retries['total_max_attempts'], 5)
        self.assertEqual(purge.access_key, storage.access_key)
        self.assertIs(storage.connection.meta.client, original_client)

        with Stubber(client) as stub:
            params = {'Bucket': 'test-bucket', 'Key': 'attachments/example.txt'}
            stub.add_response('delete_object', {}, params)
            purge.delete('example.txt')
            stub.add_client_error('delete_object', service_error_code='NoSuchKey', http_status_code=404, expected_params=params)
            purge.delete('example.txt')
            stub.add_client_error('delete_object', service_error_code='AccessDenied', http_status_code=403, expected_params=params)
            with self.assertRaises(ClientError):
                purge.delete('example.txt')
            stub.assert_no_pending_responses()

    def test_non_s3_storage_keeps_its_delete_behavior(self):
        storage = FileSystemStorage()
        self.assertIs(attachment_purge_storage(storage), storage)
