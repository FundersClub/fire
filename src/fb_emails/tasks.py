import logging

from celery import shared_task

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail
from django.db.models import F, Func, JSONField, TextField, Value
from django.template.loader import render_to_string
from django.utils import timezone

from fb_emails.models import IncomingMessage
from fb_github.models import IssueDeliveryRejected, Repository
from fb_github.utils import make_associate_email_token


LOG = logging.getLogger(__name__)

_SANITIZE_EXCLUDED_STATUSES = (
    IncomingMessage.Status.Sanitized,
    IncomingMessage.Status.Pending,
    IncomingMessage.Status.IssueError,
    IncomingMessage.Status.RepositoryArchived,
    IncomingMessage.Status.IssueBodyTooLong,
    IncomingMessage.Status.IssueTitleTooLong,
)


def _redact_post_data(expression, sanitize_txt):
    for key in ('html', 'text', 'subject'):
        expression = Func(
            expression,
            Value([key], output_field=ArrayField(TextField())),
            Value(sanitize_txt, output_field=JSONField()),
            function='jsonb_set',
            output_field=JSONField(),
        )
    return expression


@shared_task()
def process_incoming_message(msg_id):
    # Get message
    msg = IncomingMessage.objects.get(id=msg_id)
    if msg.status != IncomingMessage.Status.Pending:
        LOG.warning('Attempt to process already processed msg {}'.format(msg_id))
        return

    msg.processed_at = timezone.now()

    # See if we can match this to a GitHub repository
    email_slug, domain = msg.to_email.split('@')
    if domain != settings.EMAIL_DOMAIN:
        msg.status = IncomingMessage.Status.UnrecognizedDomain
        msg.save(update_fields=['processed_at', 'status'])
        return

    try:
        repo = Repository.objects.get(
            email_slug__iexact=email_slug,
            status=Repository.Status.Active,
        )
    except Repository.DoesNotExist:
        if email_slug not in settings.FIREBOT_BANNED_EMAIL_SLUGS:
            msg.reply_from_template('fb_emails/unknown-repo.txt', {
                'bot_username': settings.GITHUB_BOT_USERNAME,
                'email_slug': email_slug,
            })
        msg.status = IncomingMessage.Status.UnrecognizedUsername
        msg.save(update_fields=['processed_at', 'status'])

        return

    # Got our repo, create an issue
    try:
        issue = repo.create_issue_from_incoming_msg(msg)
    except IssueDeliveryRejected as error:
        issue = None
        msg.status = error.status
        LOG.warning('Message %s not delivered to repository %s: %s', msg.id, repo.id, msg.status)
    if not issue:
        if msg.status == IncomingMessage.Status.Pending:
            msg.status = IncomingMessage.Status.IssueError
        msg.save(update_fields=['processed_at', 'status'])

        body = render_to_string('fb_emails/create-issue-error.txt', {
            'msg': msg,
            'repo': repo,
        })

        send_mail(
            'Failed creating issue!',
            body,
            settings.DEFAULT_FROM_EMAIL,
            repo.admins.values_list('email', flat=True),
            fail_silently=False,
        )

        return

    # If we don't recognize this email address and haven't seen it before,
    # offer user to associate their GitHub account with this repo
    email_recognized = repo.emailmap_set.filter(email__iexact=msg.from_email).exists()
    email_seen_before = IncomingMessage.objects.filter(
        issue__repo=repo, from_email__iexact=msg.from_email
    ).exclude(id=msg.id).exists()
    if not email_recognized and not email_seen_before:
        msg.reply_from_template('fb_emails/offer-associate.html', {
            'associate_token': make_associate_email_token(msg),
            'repo': repo,
        }, html=True)

    msg.status = IncomingMessage.Status.Processed
    msg.save(update_fields=['processed_at', 'status'])


@shared_task()
def sanitize_old_emails():
    week_ago = timezone.now() - timezone.timedelta(days=7)
    sanitize_txt = '<redacted>'
    IncomingMessage.objects.filter(
        created_at__lte=week_ago
    ).exclude(
        status__in=_SANITIZE_EXCLUDED_STATUSES
    ).update(
        body_html=sanitize_txt,
        body_text=sanitize_txt,
        subject=sanitize_txt,
        original_post_data=_redact_post_data(F('original_post_data'), sanitize_txt),
        status=IncomingMessage.Status.Sanitized,
    )
