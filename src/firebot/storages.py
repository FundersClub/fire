from copy import copy

from botocore.config import Config
from django.conf import settings
from storages.backends.s3 import S3Storage


class S3MediaFilesStorage(S3Storage):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('access_key', settings.MEDIAFILES_AWS_ACCESS_KEY_ID)
        kwargs.setdefault('secret_key', settings.MEDIAFILES_AWS_SECRET_ACCESS_KEY)
        kwargs.setdefault('bucket_name', settings.MEDIAFILES_AWS_STORAGE_BUCKET_NAME)
        kwargs.setdefault('file_overwrite', False)
        kwargs.setdefault('querystring_auth', False)
        # Attachment URLs are embedded in GitHub issues, so objects must be
        # world-readable. The old boto2 backend applied public-read by default.
        kwargs.setdefault('default_acl', 'public-read')
        kwargs.setdefault('object_parameters', {
            'CacheControl': 'max-age=31536000, public',
        })
        super().__init__(*args, **kwargs)


def attachment_purge_storage(storage):
    """Use short S3 waits for web cleanup without changing upload settings."""
    if isinstance(storage, S3Storage):
        # S3Storage resets its thread-local connections when copied, so the
        # purge gets a separate client while retaining bucket/key settings.
        storage = copy(storage)
        storage.client_config = storage.client_config.merge(Config(
            connect_timeout=2,
            read_timeout=3,
            retries={'total_max_attempts': 1},
        ))
    return storage
