import logging

from celery import shared_task

from django.conf import settings
from django.utils import timezone

from fb_emails.models import IncomingMessage
from fb_github.models import Repository


LOG = logging.getLogger(__name__)


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
            email_slug=email_slug,
            status=Repository.Status.Active,
        )
    except Repository.DoesNotExist:
        msg.reply_from_template('fb_emails/unknown-repo.txt', {
            'email_slug': email_slug,
        })
        msg.status = IncomingMessage.Status.UnrecognizedUsername
        msg.save(update_fields=['processed_at', 'status'])

        return

    # # If we don't recognize this email address and haven't seen it before,
    # # offer user to associate their GitHub account with this repo
    email_recognized = repo.emailmap_set.filter(email=msg.from_email).exists()
    email_seen_before = IncomingMessage.objects.filter(
        issue__repo=repo, from_email=msg.from_email
    ).exclude(id=msg.id).exists()
    if not email_recognized and not email_seen_before:
        msg.reply_from_template('fb_emails/offer-associate.html', {
            'repo': repo,
        }, html=True)

    # Got our repo, create an issue
    if not repo.create_issue_from_incoming_msg(msg):
        # TODO need to track this, and report back to the user
        msg.status = IncomingMessage.Status.IssueError
        msg.save(update_fields=['processed_at', 'status'])
        return

    msg.status = IncomingMessage.Status.Processed
    msg.save(update_fields=['processed_at', 'status'])
