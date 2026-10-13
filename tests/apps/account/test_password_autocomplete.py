"""
Regression tests for autocomplete="new-password" on the password
confirmation field.

Password managers and browsers use autocomplete="new-password" to identify
the field(s) that a freshly suggested password should be filled into. When
only the first password field carries the attribute, a suggested password is
filled into password1 but not password2, forcing the user to copy/type the
confirmation by hand. Both fields of a "set a new password" pair must
therefore carry the same autocomplete value.
"""

import pytest

from allauth.account.forms import (
    ChangePasswordForm,
    ResetPasswordKeyForm,
    SetPasswordForm,
)


@pytest.mark.parametrize(
    "form_class",
    [ChangePasswordForm, SetPasswordForm, ResetPasswordKeyForm],
)
def test_both_password_fields_have_new_password_autocomplete(form_class):
    form = form_class()
    for field_name in ("password1", "password2"):
        rendered = str(form[field_name])
        assert (
            'autocomplete="new-password"' in rendered
        ), f'{form_class.__name__}.{field_name} is missing autocomplete="new-password"'
