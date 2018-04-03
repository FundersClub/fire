import logging

from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from github3.exceptions import ForbiddenError

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
            login=repo_invitation.repository['owner']['login'],
            name=repo_invitation.repository['name'],
            defaults={
                'inviter_login': repo_invitation.inviter.login,
                'original_invitation_data': repo_invitation.as_dict(),
            },
        )
        if created:
            accept_new_repo.delay(repo.id)
        else:
            # Repository already created, just accept the invitation
            repo_invitation.accept()


@shared_task(bind=True, max_retries=3)
def accept_new_repo(self, repo_id):
    try:
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

        gh_issue = repo.gh_repo.create_issue(
            title='Finish adding @{} to your repo'.format(settings.GITHUB_BOT_USERNAME),
            body=body,
        )
        repo.initial_issue = Issue.objects.create(
            body=body,
            gh_data=gh_issue.as_dict(),
            issue_number=gh_issue.number,
            repo=repo,
        )

        repo.status = Repository.Status.PendingInviterApproval
        repo.save(update_fields=['status', 'initial_issue'])
    except Exception as exc:
        self.retry(exc=exc, countdown=5)


@shared_task()
def update_issue_after_email_association(issue_id):
    issue = Issue.objects.get(id=issue_id)
    msg = issue.msg
    gh_issue = issue.gh_issue

    body = gh_issue.body.splitlines()
    orig_sent_by = 'Sent by {} ({})'.format(msg.from_name, msg.from_email)
    if orig_sent_by not in body[0]:
        print('Ok')
        return

    map_entry = issue.repo.emailmap_set.filter(email=msg.from_email).get()
    new_sent_by = 'Sent by {} (@{})'.format(msg.from_name, map_entry.login)
    body[0] = body[0].replace(orig_sent_by, new_sent_by)

    try:
        gh_issue.edit(gh_issue.title, '\n'.join(body))
    except ForbiddenError:
        pass


@shared_task()
def sanitize_old_issues():
    week_ago = timezone.now() - timezone.timedelta(days=7)
    Issue.objects.filter(created_at__lte=week_ago).update(
        body='<redacted>',
        gh_data={},
    )
