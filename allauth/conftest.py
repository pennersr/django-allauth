import json
import random
import time
import uuid
from contextlib import contextmanager
from unittest.mock import Mock, PropertyMock, patch

from django.contrib.auth import get_user_model
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

import pytest

from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_pk_to_url_str, user_username
from allauth.core import context
from allauth.socialaccount.internal import statekit
from allauth.socialaccount.providers.base.constants import AuthProcess


def pytest_collection_modifyitems(config, items):
    if config.getoption("--ds") == "tests.headless_only.settings":
        removed_items = []
        for item in items:
            if not item.location[0].startswith("allauth/headless"):
                removed_items.append(item)
        for item in removed_items:
            items.remove(item)


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def password_factory():
    def f():
        return str(uuid.uuid4())

    return f


@pytest.fixture
def user_password(password_factory):
    return password_factory()


@pytest.fixture
def email_verified():
    return True


@pytest.fixture
def user_factory(email_factory, db, user_password, email_verified):
    def factory(
        email=None,
        username=None,
        commit=True,
        with_email=True,
        email_verified=email_verified,
        password=None,
        with_emailaddress=True,
        with_totp=False,
    ):
        if not username:
            username = uuid.uuid4().hex

        if not email and with_email:
            email = email_factory(username=username)

        User = get_user_model()
        user = User()
        if password == "!":
            user.password = password
        else:
            user.set_password(user_password if password is None else password)
        user_username(user, username)
        user_email(user, email or "")
        if commit:
            user.save()
            if email and with_emailaddress:
                EmailAddress.objects.create(
                    user=user,
                    email=email.lower(),
                    verified=email_verified,
                    primary=True,
                )
        if with_totp:
            from allauth.mfa.totp.internal import auth

            auth.TOTP.activate(user, auth.generate_totp_secret())
        return user

    return factory


@pytest.fixture
def email_factory():
    def factory(username=None, email=None, mixed_case=False):
        if email is None:
            if not username:
                username = uuid.uuid4().hex
            email = f"{username}@{uuid.uuid4().hex}.org"
        if mixed_case:
            email = "".join([random.choice([c.upper(), c.lower()]) for c in email])
        else:
            email = email.lower()
        return email

    return factory


@pytest.fixture
def reauthentication_bypass():
    @contextmanager
    def f():
        with patch(
            "allauth.account.internal.flows.reauthentication.did_recently_authenticate"
        ) as m:
            m.return_value = True
            yield

    return f


@pytest.fixture
def webauthn_authentication_bypass():
    @contextmanager
    def f(authenticator):
        from fido2.utils import websafe_encode

        from allauth.mfa.adapter import get_adapter

        with patch(
            "allauth.mfa.webauthn.internal.auth.WebAuthn.authenticator_data",
            new_callable=PropertyMock,
        ) as ad_m:
            with patch("fido2.server.Fido2Server.authenticate_begin") as ab_m:
                ab_m.return_value = ({}, {"state": "dummy"})
                with patch("fido2.server.Fido2Server.authenticate_complete") as ac_m:
                    with patch(
                        "allauth.mfa.webauthn.internal.auth.parse_authentication_response"
                    ) as m:
                        user_handle = (
                            get_adapter().get_public_key_credential_user_entity(
                                authenticator.user
                            )["id"]
                        )
                        authenticator_data = Mock()
                        authenticator_data.credential_data.credential_id = (
                            "credential_id"
                        )
                        ad_m.return_value = authenticator_data
                        m.return_value = Mock()
                        binding = Mock()
                        binding.credential_id = "credential_id"
                        ac_m.return_value = binding
                        yield json.dumps(
                            {"response": {"userHandle": websafe_encode(user_handle)}}
                        )

    return f


@pytest.fixture
def webauthn_registration_bypass():
    @contextmanager
    def f(user, passwordless):
        with patch("fido2.server.Fido2Server.register_complete") as rc_m:
            with patch(
                "allauth.mfa.webauthn.internal.auth.parse_registration_response"
            ) as m:
                m.return_value = Mock()

                class FakeAuthenticatorData(bytes):
                    def is_user_verified(self):
                        return passwordless

                binding = FakeAuthenticatorData(b"binding")
                rc_m.return_value = binding
                yield json.dumps(
                    {
                        "authenticatorAttachment": "cross-platform",
                        "clientExtensionResults": {"credProps": {"rk": passwordless}},
                        "id": "123",
                        "rawId": "456",
                        "response": {
                            "attestationObject": "ao",
                            "clientDataJSON": "cdj",
                            "transports": ["usb"],
                        },
                        "type": "public-key",
                    }
                )

    return f


@pytest.fixture(autouse=True)
def clear_context_request():
    context._request_var.set(None)


@pytest.fixture
def enable_cache(settings):
    from django.core.cache import cache

    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
    cache.clear()
    yield


@pytest.fixture
def totp_validation_bypass():
    @contextmanager
    def f():
        with patch("allauth.mfa.totp.internal.auth.validate_totp_code") as m:
            m.return_value = True
            yield

    return f


@pytest.fixture
def provider_id():
    return "unittest-server"


@pytest.fixture
def password_reset_key_generator():
    def f(user):
        from allauth.account import app_settings

        token_generator = app_settings.PASSWORD_RESET_TOKEN_GENERATOR()
        uid = user_pk_to_url_str(user)
        temp_key = token_generator.make_token(user)
        key = f"{uid}-{temp_key}"
        return key

    return f


@pytest.fixture
def google_provider_settings(settings):
    gsettings = {"APPS": [{"client_id": "client_id", "secret": "secret"}]}
    settings.SOCIALACCOUNT_PROVIDERS = {"google": gsettings}
    return gsettings


@pytest.fixture
def user_with_totp(user):
    from allauth.mfa.totp.internal import auth

    auth.TOTP.activate(user, auth.generate_totp_secret())
    return user


@pytest.fixture
def user_with_recovery_codes(user_with_totp):
    from allauth.mfa.recovery_codes.internal import auth

    auth.RecoveryCodes.activate(user_with_totp)
    return user_with_totp


@pytest.fixture
def passkey(user):
    from allauth.mfa.models import Authenticator

    authenticator = Authenticator.objects.create(
        user=user,
        type=Authenticator.Type.WEBAUTHN,
        data={
            "name": "Test passkey",
            "passwordless": True,
            "credential": {},
        },
    )
    return authenticator


@pytest.fixture
def user_with_passkey(user, passkey):
    return user


@pytest.fixture
def sociallogin_setup_state():
    def setup(client, process=None, next_url=None, **kwargs):
        state_id = "123"
        session = client.session
        state = {"process": process or AuthProcess.LOGIN, **kwargs}
        if next_url:
            state["next"] = next_url
        states = {}
        states[state_id] = [state, time.time()]
        session[statekit.STATES_SESSION_KEY] = states
        session.save()
        return state_id

    return setup


@pytest.fixture
def request_factory(rf):
    class RequestFactory:
        def get(self, path):
            request = rf.get(path)
            SessionMiddleware(lambda request: None).process_request(request)
            MessageMiddleware(lambda request: None).process_request(request)
            return request

    return RequestFactory()
