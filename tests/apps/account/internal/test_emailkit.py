import pytest

from allauth.account.internal import emailkit


@pytest.mark.parametrize(
    "email,valid",
    [
        (
            "this.email.address.is.a.bit.too.long.but.should.still.validate@example.com",
            True,
        ),
        (
            ("x" * 300)
            + "this.email.address.is.a.bit.too.long.but.should.still.validate@example.com",
            False,
        ),
    ],
)
def test_email_validation(email, valid):
    clean_email = emailkit.valid_email_or_none(email)
    if valid:
        assert clean_email == email
    else:
        assert clean_email is None
