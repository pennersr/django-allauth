import uuid
from contextlib import contextmanager
from unittest.mock import patch

from django.contrib.auth import get_user_model

import pytest

from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_username
from allauth.core import context


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
def user_factory(email_factory, db, user_password):
    def factory(
        email=None,
        username=None,
        commit=True,
        with_email=True,
        email_verified=True,
        password=None,
        with_emailaddress=True,
    ):
        if not username:
            username = uuid.uuid4().hex

        if not email and with_email:
            email = email_factory(username=username)

        User = get_user_model()
        user = User()
        user.set_password(user_password if password is None else password)
        user_username(user, username)
        user_email(user, email or "")
        if commit:
            user.save()
            if email and with_emailaddress:
                EmailAddress.objects.create(
                    user=user, email=email, verified=email_verified, primary=True
                )

        return user

    return factory


@pytest.fixture
def email_factory():
    def factory(username=None):
        if not username:
            username = uuid.uuid4().hex
        return f"{username}@{uuid.uuid4().hex}.org"

    return factory


@pytest.fixture
def reauthentication_bypass():
    @contextmanager
    def f():
        with patch("allauth.account.decorators.did_recently_authenticate") as m:
            m.return_value = True
            yield

    return f


@pytest.fixture(autouse=True)
def clear_context_request():
    context._request_var.set(None)


@pytest.fixture
def enable_cache(settings):
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
    yield
