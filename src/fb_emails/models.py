from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string

from djchoices import DjangoChoices, ChoiceItem as C


class IncomingMessage(models.Model):
    class Status(DjangoChoices):
        Pending = C('pending', 'Pending processing')
        UnrecognizedDomain = C('unrecognized-domain', 'Unrecognized domain')
        UnrecognizedUsername = C('unrecognized-username', 'Unrecognized username')
        IssueError = C('issue-error', 'Failed creating issue')
        Processed = C('processed', 'Processed')

    body_html = models.TextField()
    body_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    from_email = models.EmailField(max_length=200)
    from_name = models.CharField(max_length=200)
    original_post_data = JSONField()
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.Pending)
    subject = models.CharField(max_length=500)
    to_email = models.EmailField(max_length=200)
    uuid = models.UUIDField(default=uuid4)

    def reply_from_template(self, template_name, extra_context=None):
        context = {
            'msg': self,
            'settings': settings,
        }
        if extra_context:
            context.update(extra_context)

        return send_mail(
            'Re: ' + self.subject,
            render_to_string(template_name, context),
            settings.DEFAULT_FROM_EMAIL,
            ['{} <{}>'.format(self.from_name, self.from_email) if self.from_name else self.from_email],
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
    msg = models.ForeignKey(IncomingMessage)
