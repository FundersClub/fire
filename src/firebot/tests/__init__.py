import requests_mock


class RequestsMockMixin(object):
    def __call__(self, *args, **kwargs):
        with requests_mock.Mocker() as mock:
            self.requests_mock = mock
            return super(RequestsMockMixin, self).__call__(*args, **kwargs)
