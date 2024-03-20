import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.providers.base.constants import AuthProcess


@pytest.fixture
def sociallogin_factory(user_factory):
    def factory(
        email=None,
        username=None,
        with_email=True,
        provider="unittest-server",
        uid="123",
        email_verified=True,
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
        return sociallogin

    return factory


@pytest.fixture
def sociallogin_setup_state():
    def setup(client):
        state = "123"
        session = client.session
        session["socialaccount_state"] = [{"process": AuthProcess.LOGIN}, state]
        session.save()
        return state

    return setup
