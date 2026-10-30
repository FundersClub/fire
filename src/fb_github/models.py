import logging
import re

from uuid import uuid4

from django.conf import settings
from django.db import (
    models,
    transaction,
)
from django.utils import timezone
from github3.exceptions import ForbiddenError, GitHubException, UnprocessableEntity

from fb_emails.models import IncomingMessage

from fb_github.client import get_github_client
from fb_github.utils import msg_to_markdown


LOG = logging.getLogger(__name__)


class IssueDeliveryRejected(Exception):
    """A known GitHub rejection; no issue was created."""

    def __init__(self, status):
        self.status = status
        super().__init__(status)


def rejected_issue_status(error):
    if isinstance(error, ForbiddenError) and error.message == 'Repository was archived so is read-only.':
        return IncomingMessage.Status.RepositoryArchived
    if isinstance(error, UnprocessableEntity):
        errors = error.errors
        if not isinstance(errors, list) or not errors:
            return None
        statuses = []
        for detail in errors:
            if not isinstance(detail, dict) or detail.get('resource') != 'Issue':
                return None
            field = detail.get('field')
            if field not in ('body', 'title') or detail.get('code') != 'custom':
                return None
            message = detail.get('message', '')
            if not isinstance(message, str) or not re.fullmatch(
                field + r' is too long(?: \(maximum is \d+ characters\))?', message, re.IGNORECASE,
            ):
                return None
            statuses.append(IncomingMessage.Status.IssueBodyTooLong if field == 'body'
                            else IncomingMessage.Status.IssueTitleTooLong)
        if len(set(statuses)) == 1:
            return statuses[0]
    return None


def validation_fields(error):
    """Keep diagnostics useful without copying provider text or email content."""
    errors = getattr(error, 'errors', [])
    if not isinstance(errors, list):
        return []
    return sorted({detail['field'] for detail in errors if isinstance(detail, dict)
                   and detail.get('resource') == 'Issue'
                   and detail.get('field') in ('title', 'body', 'assignees', 'labels', 'milestone')})


def validation_details(error):
    """Bound diagnostics and replace provider text with known values only."""
    errors = getattr(error, 'errors', None)
    if not isinstance(errors, list):
        return {'shape': 'missing' if errors is None else 'other'}
    details = []
    allowed = {
        'resource': ('Issue',),
        'field': ('title', 'body', 'assignees', 'labels', 'milestone'),
        'code': ('missing', 'missing_field', 'invalid', 'already_exists', 'unprocessable', 'custom'),
    }
    for error_detail in errors[:10]:
        if not isinstance(error_detail, dict):
            details.append({'shape': 'other'})
            continue
        detail = {
            key: error_detail[key] if error_detail.get(key) in values else
            ('missing' if key not in error_detail else 'other')
            for key, values in allowed.items()
        }
        message = error_detail.get('message')
        detail['reason'] = 'missing' if message is None else 'other'
        if isinstance(message, str):
            match = re.fullmatch(r'(body|title) is too long(?: \(maximum is \d+ characters\))?',
                                 message, re.IGNORECASE)
            if match:
                detail['reason'] = match.group(1).lower() + '-too-long'
        details.append(detail)
    return {'shape': 'list', 'count': len(errors), 'details': details}


def email_slug_default():
    return uuid4().hex[:8]


class RepositoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Repository.Status.Active)


class Repository(models.Model):
    class Status(models.TextChoices):
        PendingAccept = 'pending-accept', 'Pending accept'
        PendingInviterApproval = 'pending-inviter-approval', 'Pending inviter approval'
        Active = 'active', 'Active'

    admins = models.ManyToManyField(settings.AUTH_USER_MODEL)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_slug = models.SlugField(default=email_slug_default, unique=True)
    initial_issue = models.ForeignKey('Issue', null=True, blank=True, on_delete=models.SET_NULL)
    inviter_login = models.CharField(max_length=200)
    login = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    original_invitation_data = models.JSONField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PendingAccept)
    uuid = models.UUIDField(default=uuid4, unique=True)

    include_sender_email_in_issue = models.BooleanField(default=True)

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
        except:  # noqa
            if settings.DEBUG:
                raise
            LOG.exception('failed msg_to_markdown on {} {}'.format(self.id, msg.id))
            body = msg.body_text

        # Create issue on github
        try:
            gh_repo = self.gh_repo
            if gh_repo.archived is True:
                raise IssueDeliveryRejected(IncomingMessage.Status.RepositoryArchived)
            gh_issue = gh_repo.create_issue(
                title=msg.subject or 'New issue',
                body=body,
            )
        except GitHubException as error:
            rejected_status = rejected_issue_status(error)
            if rejected_status:
                raise IssueDeliveryRejected(rejected_status) from error
            diagnostics = {
                'github_status': getattr(error, 'code', None),
                'github_validation_fields': validation_fields(error),
                'github_validation_details': validation_details(error),
                'issue_title_length': len(msg.subject or 'New issue'),
                'issue_body_length': len(body),
            }
            # Celery's console formatter omits LogRecord.extra. Keep these safe
            # details in the message too, even when Sentry misses the event.
            LOG.exception('failed creating github issue for %s %s: %s',
                          self.id, msg.id, diagnostics, extra=diagnostics)
            return

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

    @transaction.atomic
    def approve_by_inviter(self, user):
        assert self.status == Repository.Status.PendingInviterApproval

        self.approved_at = timezone.now()
        self.status = Repository.Status.Active
        self.save(update_fields=['approved_at', 'status'])

        self.admins.add(user)

        for emailaddress in user.emailaddress_set.filter(verified=True):
            self.emailmap_set.create(
                email=emailaddress.email,
                login=user.username,
                user=user,
            )

        try:
            self.initial_issue.gh_issue.close()
        except:  # noqa
            pass


class EmailMap(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    login = models.CharField(max_length=200)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
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
    gh_data = models.JSONField()
    issue_number = models.PositiveIntegerField()
    msg = models.OneToOneField('fb_emails.IncomingMessage', blank=True, null=True, on_delete=models.SET_NULL)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return 'Issue #{} on {}'.format(self.issue_number, self.repo)

    @property
    def gh_issue(self):
        return get_github_client().issue(self.repo.login, self.repo.name, self.issue_number)
