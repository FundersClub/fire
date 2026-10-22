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
