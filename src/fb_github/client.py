import github3

from django.conf import settings


def get_github_client(token=None):
    ghc = github3.login(token=token or settings.GITHUB_TOKEN)
    assert ghc.__class__ == github3.github.GitHub
    ghc.__class__ = GitHub
    return ghc


class GitHub(github3.github.GitHub):
    def repository_invitations(self, number=-1, etag=None):
        url = self._build_url('user', 'repository_invitations')
        return self._iter(
            int(number),
            url,
            RepositoryInvitation,
            {},
            etag,
            headers={'Accept': 'application/vnd.github.swamp-thing-preview+json'},
        )


class RepositoryInvitation(github3.models.GitHubCore):
    def _repr(self):
        return '<RepositoryInvitation [{} by {}]>'.format(
            self.repository.full_name,
            self.inviter.login,
        )

    def _update_attributes(self, invitation):
        self.repository = github3.repos.repo.Repository(invitation['repository'], self)
        self.inviter = github3.users.User(invitation['inviter'], self)
        self.invitee = github3.users.User(invitation['invitee'], self)

    def accept(self):
        return self._boolean(
            self._patch(self.url, headers={'Accept': 'application/vnd.github.swamp-thing-preview+json'}),
            204,
            404,
        )
