from unittest.mock import Mock

import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base.provider import Provider


@pytest.mark.parametrize(
    "email,emails,expected_email,expected_emails",
    [
        (
            "a@A.COM",
            [EmailAddress(email="A@a.com")],
            "a@a.com",
            [EmailAddress(email="a@a.com")],
        ),
        (
            None,
            [
                EmailAddress(email="A@a.com", primary=True),
                EmailAddress(email="b-AT-b.com"),
                EmailAddress(email="c@c.com", primary=False),
            ],
            "a@a.com",
            [EmailAddress(email="a@a.com"), EmailAddress(email="c@c.com")],
        ),
        (
            "a@A.COM",
            [EmailAddress(email="invalid.com")],
            "a@a.com",
            [EmailAddress(email="a@a.com")],
        ),
        (
            "a@A.COM",
            [EmailAddress(email="is@valid.com")],
            "a@a.com",
            [
                EmailAddress(email="a@a.com"),
                EmailAddress(email="is@valid.com"),
            ],
        ),
        (
            "invalid@test.email",
            [
                EmailAddress(email="invalid@test.email"),
            ],
            None,
            [],
        ),
        (
            "invalid@test.email",
            [
                EmailAddress(email="invalid@test.email"),
                EmailAddress(email="valid@test.email"),
            ],
            "valid@test.email",
            [EmailAddress(email="valid@test.email")],
        ),
    ],
)
def test_cleanup_email_addresses(email, emails, expected_email, expected_emails):
    app = Mock()
    app.settings = {"verified_email": None}
    provider = Provider(None, app=app)
    provider.id = "test"
    email = provider.cleanup_email_addresses(email, emails)
    assert email == expected_email
    assert len(emails) == len(expected_emails)
    for i, addr in enumerate(emails):
        assert addr.email == expected_emails[i].email
