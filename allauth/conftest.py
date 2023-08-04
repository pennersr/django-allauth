import uuid

import pytest

from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_username
from allauth.utils import get_user_model


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def user_factory(email_factory, db):
    def factory(
        email=None, username=None, commit=True, with_email=True, email_verified=True
    ):
        if not username:
            username = uuid.uuid4().hex

        if not email and with_email:
            email = email_factory(username=username)

        User = get_user_model()
        user = User()
        user_username(user, username)
        user_email(user, email or "")
        if commit:
            user.save()
            if email:
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
