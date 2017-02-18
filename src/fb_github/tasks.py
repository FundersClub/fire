import logging

from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string

from fb_github.client import (
    get_github_client,
    RepositoryInvitation,
)
from fb_github.models import (
    Issue,
    Repository,
)


LOG = logging.getLogger()


@shared_task()
def poll_invitations():
    for repo_invitation in get_github_client().repository_invitations():
        repo, created = Repository.objects.get_or_create(
            login=repo_invitation.repository.owner.login,
            name=repo_invitation.repository.name,
            defaults={
                'inviter_login': repo_invitation.inviter.login,
                'original_invitation_data': repo_invitation.as_dict(),
            },
        )
        if created or True:
            accept_new_repo.delay(repo.id)


@shared_task()
def accept_new_repo(repo_id):
    repo = Repository.objects.get(id=repo_id)

    if repo.status != Repository.Status.PendingAccept:
        LOG.warning('Attempted to accept already accepted repo: {}'.format(repo))
        return

    repo_invitation = RepositoryInvitation(repo.original_invitation_data, get_github_client())
    repo_invitation.accept()

    body = render_to_string('fb_github/initial-issue.txt', {
        'repo': repo,
        'settings': settings,
    })

    repo.gh_repo.create_issue(
        title='FireBot says hi!',
        body=body,
    )

    repo.status = Repository.Status.PendingInviterApproval
    repo.save(update_fields=['status'])


@shared_task()
def update_issue_after_email_association(issue_id):
    issue = Issue.objects.get(id=issue_id)
    msg = issue.msg
    gh_issue = issue.gh_issue

    body = gh_issue.body.splitlines()
    orig_sent_by = 'sent by {} ({})'.format(msg.from_name, msg.from_email)
    if orig_sent_by not in body[0]:
        print('Ok')
        return

    map_entry = issue.repo.emailmap_set.filter(email=msg.from_email).get()
    new_sent_by = 'sent by {} (@{})'.format(msg.from_name, map_entry.login)
    body[0] = body[0].replace(orig_sent_by, new_sent_by)

    gh_issue.edit(gh_issue.title, '\n'.join(body))
