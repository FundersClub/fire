import html2text
import logging
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import (
    EmailMultiAlternatives,
    send_mail,
)
from django.db import models
from django.template.loader import render_to_string


LOG = logging.getLogger(__name__)


class IncomingMessage(models.Model):
    class Status(models.TextChoices):
        Pending = 'pending', 'Pending processing'
        UnrecognizedDomain = 'unrecognized-domain', 'Unrecognized domain'
        UnrecognizedUsername = 'unrecognized-username', 'Unrecognized username'
        IssueError = 'issue-error', 'Failed creating issue'
        RepositoryArchived = 'repository-archived', 'Not delivered: repository archived'
        IssueBodyTooLong = 'issue-body-too-long', 'Not delivered: issue body too long'
        IssueTitleTooLong = 'issue-title-too-long', 'Not delivered: issue title too long'
        Processed = 'processed', 'Processed'
        Sanitized = 'sanitized', 'Sanitized'

    body_html = models.TextField()
    body_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    from_email = models.EmailField(max_length=500)
    from_name = models.CharField(max_length=500)
    original_post_data = models.JSONField()
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.Pending)
    subject = models.CharField(max_length=2000)
    to_email = models.EmailField(max_length=500)
    uuid = models.UUIDField(default=uuid4, unique=True)
    spam_score = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    def reply_from_template(self, template_name, extra_context=None, html=False):
        # Inbound mail can have a missing or malformed sender. There is no
        # address to reply to, but processing the message should still finish.
        try:
            validate_email(self.from_email)
        except ValidationError:
            LOG.warning('Skipping automatic reply for message %s: invalid sender address', self.pk)
            return 0

        context = {
            'msg': self,
            'settings': settings,
        }
        if extra_context:
            context.update(extra_context)

        body = render_to_string(template_name, context)
        subject = 'Re: ' + self.subject
        to = '"{}" <{}>'.format(
            self.from_name.replace('"', ''),
            self.from_email,
        ) if self.from_name else self.from_email

        # Sendgrid doesn't like square brackets in the `to` field.
        to = to.replace('[', '').replace(']', '')

        if html:
            h = html2text.HTML2Text(bodywidth=0)
            text_content = h.handle(body)
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to])
            msg.attach_alternative(body, "text/html")
            msg.send(fail_silently=False)
        else:
            return send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [to],
                fail_silently=False,
            )


def attachment_file_name(instance, filename):
    uuid = instance.msg.uuid if instance.msg else uuid4().hex
    return 'email-attachments/{}/{}'.format(uuid, filename)


class Attachment(models.Model):
    content_id = models.CharField(max_length=100)
    content_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(max_length=500, upload_to=attachment_file_name)
    msg = models.ForeignKey(IncomingMessage, on_delete=models.CASCADE)
