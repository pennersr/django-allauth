from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.parametrize(
    "samesite_strict,did_already_redirect,expect_redirect",
    [
        (True, False, True),
        (True, True, False),
        (False, False, False),
    ],
)
def test_samesite_strict(
    client,
    samesite_strict,
    settings,
    google_provider_settings,
    did_already_redirect,
    expect_redirect,
    db,
):
    settings.SESSION_COOKIE_SAMESITE = "Strict" if samesite_strict else "Lax"
    query = "?state=123"
    resp = client.get(
        reverse("google_callback") + query + ("&_redir" if did_already_redirect else "")
    )
    if expect_redirect:
        assertTemplateUsed(resp, "socialaccount/login_redirect.html")
        assert (
            resp.context["redirect_to"]
            == reverse("google_callback") + query + "&_redir="
        )
    else:
        assertTemplateUsed(resp, "socialaccount/authentication_error.html")
