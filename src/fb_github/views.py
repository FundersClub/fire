from django import http
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from fb_emails.models import IncomingMessage
from fb_github.models import Repository
from fb_github.tasks import update_issue_after_email_association


class AssociateEmailView(TemplateView):
    template_name = 'fb_github/associate-email.html'

    def dispatch(self, request, *args, **kwargs):
        self.repo = get_object_or_404(
            Repository,
            login=kwargs['repo_login'],
            name=kwargs['repo_name'],
            status=Repository.Status.Active,
        )

        try:
            self.msg = get_object_or_404(
                IncomingMessage,
                issue__repo=self.repo,
                uuid=kwargs['msg_uuid'],
            )
        except ValueError:
            raise http.Http404

        self.associated = self.repo.emailmap_set.filter(email=self.msg.from_email).first()

        return super(AssociateEmailView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.associated:
            self.associated = self.repo.emailmap_set.create(
                email=self.msg.from_email,
                login=request.user.username,
                user=request.user,
            )
            update_issue_after_email_association.delay(self.msg.issue.id)
        return super(AssociateEmailView, self).get(request, *args, **kwargs)
