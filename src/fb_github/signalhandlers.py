from allauth.account.models import EmailAddress
from django.dispatch import receiver

from allauth.account.signals import user_signed_up

from fb_github.client import get_github_client


@receiver(user_signed_up)
def sync_github_emails_on_signup(sender, request, user, **kwargs):
    sociallogin = kwargs.get('sociallogin')
    if not sociallogin or sociallogin.account.provider != 'github':
        return

    gh_client = get_github_client(sociallogin.account.extra_data['login'], sociallogin.token.token)
    gh_emails = list(gh_client.emails())

    # If we don't have an email address, grab one from GitHub
    if not user.email:
        assert not user.emailaddress_set.exists()
        gh_primary_email = next(gh_email for gh_email in gh_emails if gh_email.primary)

        user.email = gh_primary_email.email
        user.save(update_fields=['email'])

        # Add email if we don't already have it on our system
        if not EmailAddress.objects.filter(email=gh_primary_email.email).exists():
            user.emailaddress_set.create(
                email=gh_primary_email.email,
                primary=True,
                verified=gh_primary_email.verified,
            )

    # Create email address objects for all GitHub emails we currently have
    for gh_email in gh_emails:
        if not EmailAddress.objects.filter(email=gh_email.email).exists():
            user.emailaddress_set.get_or_create(
                email=gh_email.email,
                verified=gh_email.verified,
            )
