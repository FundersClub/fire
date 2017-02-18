import json

from email.utils import parseaddr
from functools import partial

from django.db import transaction
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from fb_emails.tasks import process_incoming_message
from fb_emails.models import (
    Attachment,
    IncomingMessage,
)


@method_decorator(csrf_exempt, name='dispatch')
class SendGridParseView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        from_name, from_email = parseaddr(data['from'])

        msg = IncomingMessage.objects.create(
            body_html=data.get('html', ''),
            body_text=data['text'],
            from_email=from_email,
            from_name=from_name,
            original_post_data=dict(data),
            subject=data['subject'],
            to_email=json.loads(data['envelope'])['to'][0],
        )

        for name, info in json.loads(data.get('attachment-info', '{}')).items():
            Attachment.objects.create(
                content_id=info.get('content-id', ''),
                content_type=info.get('type', ''),
                file=request.FILES[name],
                msg=msg,
            )

        transaction.on_commit(partial(process_incoming_message.delay, msg.id))
        return HttpResponse()
