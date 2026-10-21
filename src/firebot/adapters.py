from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Accounts may only be created by logging in with GitHub. Local
        # username/password signup let anyone pick an arbitrary username.
        return False


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        # The default implementation defers to the account adapter, which
        # would also close GitHub signup.
        return True
