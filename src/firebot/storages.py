from django.conf import settings
from django.utils.encoding import filepath_to_uri
from storages.backends.s3boto import S3BotoStorage


class S3MediaFilesStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        super(S3MediaFilesStorage, self).__init__(*args, **kwargs)

        self.access_key = settings.MEDIAFILES_AWS_ACCESS_KEY_ID
        self.secret_key = settings.MEDIAFILES_AWS_SECRET_ACCESS_KEY
        self.bucket_name = settings.MEDIAFILES_AWS_STORAGE_BUCKET_NAME
        self.file_overwrite = False
        self.querystring_auth = False
        self.headers = {
            'Cache-Control': 'max-age=31536000, public',
        }
