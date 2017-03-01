import logging

from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from djchoices import DjangoChoices, ChoiceItem as C

from fb_github.client import get_github_client
from fb_github.utils import msg_to_markdown


LOG = logging.getLogger(__name__)


def email_slug_default():
    return uuid4().hex[:8]


class RepositoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Repository.Status.Active)


class Repository(models.Model):
    class Status(DjangoChoices):
        PendingAccept = C('pending-accept', 'Pending accept')
        PendingInviterApproval = C('pending-inviter-approval', 'Pending inviter approval')
        Active = C('active', 'Active')

    admins = models.ManyToManyField(settings.AUTH_USER_MODEL)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_slug = models.SlugField(default=email_slug_default, unique=True)
    inviter_login = models.CharField(max_length=200)
    login = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    original_invitation_data = JSONField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PendingAccept)

    objects = RepositoryQuerySet.as_manager()

    class Meta:
        unique_together = (
            ('login', 'name', ),
        )
        verbose_name_plural = 'Repositories'

    def __str__(self):
        return '{} ({})'.format(
            self.full_name,
            self.get_status_display(),
        )

    @property
    def email(self):
        return '{}@{}'.format(self.email_slug, settings.EMAIL_DOMAIN)

    @property
    def full_name(self):
        return '{}/{}'.format(self.login, self.name)

    @property
    def gh_repo(self):
        return get_github_client().repository(self.login, self.name)

    @property
    def gh_url(self):
        return 'https://github.com/' + self.full_name

    def is_editable_by(self, user):
        return user.is_staff or user in self.admins.all()

    def create_issue_from_incoming_msg(self, msg):
        try:
            body = msg_to_markdown(self, msg)
        except:
            if settings.DEBUG:
                raise
            LOG.exception('failed msg_to_markdown on {} {}'.format(self.id, msg.id))
            body = msg.body_text

        # Create issue on github
        gh_issue = self.gh_repo.create_issue(
            title=msg.subject,
            body=body,
        )
        if not gh_issue:
            LOG.error('failed creating github issue for {} {}'.format(self.id, msg.id))
            return

        return Issue.objects.create(
            body=body,
            gh_data=gh_issue.as_dict(),
            issue_number=gh_issue.number,
            msg=msg,
            repo=self,
        )


class EmailMap(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    login = models.CharField(max_length=200)
    repo = models.ForeignKey(Repository)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('created_at', )
        unique_together = (
            ('repo', 'email', ),
        )

    def __str__(self):
        return '@{}: {} -> {}'.format(
            self.repo.full_name,
            self.email,
            self.login,
        )


class Issue(models.Model):
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    gh_data = JSONField()
    issue_number = models.PositiveIntegerField()
    msg = models.OneToOneField('fb_emails.IncomingMessage')
    repo = models.ForeignKey(Repository)

    def __str__(self):
        return 'Issue #{} on {}'.format(self.issue_number, self.repo)

    @property
    def gh_issue(self):
        return get_github_client().issue(self.repo.login, self.repo.name, self.issue_number)
