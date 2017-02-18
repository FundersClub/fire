import os
import re

from functools import wraps

from firebot.tests import RequestsMockMixin


def mock_github_api(fn):
    def data(filename):
        return open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r').read()

    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        assert isinstance(self, RequestsMockMixin)

        self.requests_mock.register_uri(
            'GET',
            re.compile('https://api.github.com/repos/[\d\w-]+/[\d\w-]+'),
            text=data('github-repo.json'),
        )

        self.requests_mock.register_uri(
            'POST',
            'https://api.github.com/repos/firebot-test/Hello-World/issues',
            text=data('github-issue.json'),
            status_code=201,
        )

        return fn(self, *args, **kwargs)
    return wrapped
