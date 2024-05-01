import time

import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.internal import statekit
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
    def setup(client, process=None, next_url=None):
        state_id = "123"
        session = client.session
        state = {"process": process or AuthProcess.LOGIN}
        if next_url:
            state["next"] = next_url
        states = {}
        states[state_id] = [state, time.time()]
        session[statekit.STATES_SESSION_KEY] = states
        session.save()
        return state_id

    return setup


@pytest.fixture
def google_provier_settings(settings):
    settings.SOCIALACCOUNT_PROVIDERS = {
        "google": {"APPS": [{"client_id": "client_id", "secret": "secret"}]}
    }
