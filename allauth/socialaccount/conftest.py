import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialLogin


@pytest.fixture
def sociallogin_factory(user_factory):
    def factory(
        email=None,
        with_email=True,
        provider="unittest-server",
        uid="123",
        email_verified=True,
    ):
        user = user_factory(email=email, commit=False, with_email=with_email)
        account = SocialAccount(provider=provider, uid=uid)
        sociallogin = SocialLogin(user=user, account=account)
        if with_email:
            sociallogin.email_addresses = [
                EmailAddress(email=user.email, verified=email_verified, primary=True)
            ]
        return sociallogin

    return factory
