import github3
from github3.repos.invitation import Invitation as RepositoryInvitation  # noqa: F401

from django.conf import settings


def get_github_client(username=None, token=None):
    # `username` is accepted for backwards compatibility; token auth identifies the user.
    return github3.login(token=token or settings.GITHUB_TOKEN)
