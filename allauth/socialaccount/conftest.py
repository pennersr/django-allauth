import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import (
    SocialAccount,
    SocialLogin,
    SocialToken,
)


@pytest.fixture
def sociallogin_factory(user_factory):
    def factory(
        email=None,
        username=None,
        with_email=True,
        provider="unittest-server",
        uid="123",
        email_verified=True,
        with_token=False,
    ):
        user = user_factory(
            username=username, email=email, commit=False, with_email=with_email
        )
        account = SocialAccount(provider=provider, uid=uid)
        sociallogin = SocialLogin(user=user, account=account)
        if with_email:
            sociallogin.email_addresses = [
                EmailAddress(email=user.email, verified=email_verified, primary=True)
            ]
        if with_token:
            sociallogin.token = SocialToken(token="123", token_secret="456")
        return sociallogin

    return factory
