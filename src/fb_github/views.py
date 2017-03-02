from django import http
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from fb_emails.models import IncomingMessage
from fb_github.models import Repository
from fb_github.tasks import update_issue_after_email_association


class RepoAdminMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.repo = get_object_or_404(
            Repository,
            login=kwargs['repo_login'],
            name=kwargs['repo_name'],
            status=Repository.Status.Active,
        )
        if not self.repo.is_editable_by(request.user):
            raise http.Http404

        return super(RepoAdminMixin, self).dispatch(request, *args, **kwargs)


class IndexView(RepoAdminMixin, TemplateView):
    template_name = 'fb_github/index.html'


class InviterApprovalView(TemplateView):
    template_name = 'fb_github/inviter-approval.html'

    def dispatch(self, request, *args, **kwargs):
        self.repo = get_object_or_404(
            Repository,
            login=kwargs['repo_login'],
            name=kwargs['repo_name'],
        )

        if self.repo.status == Repository.Status.PendingAccept:
            raise http.Http404
        elif self.repo.status != Repository.Status.PendingInviterApproval:
            return http.HttpResponseRedirect(reverse('fb_github:index', kwargs=kwargs))

        return super(InviterApprovalView, self).dispatch(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        repo = self.repo
        if not (request.user.is_authenticated() and request.user.username == repo.inviter_login):
            raise http.Http404

        repo.approved_at = timezone.now()
        repo.status = Repository.Status.Active
        repo.save(update_fields=['approved_at', 'status'])

        repo.admins.add(request.user)

        for emailaddress in request.user.emailaddress_set.filter(verified=True):
            repo.emailmap_set.create(
                email=emailaddress.email,
                login=request.user.username,
                user=request.user,
            )

        return http.HttpResponseRedirect(reverse('repos'))


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
