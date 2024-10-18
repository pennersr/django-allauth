from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.socialaccount.adapter import get_adapter


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


def test_config_from_app_settings(google_provider_settings, rf, db, settings):
    settings.SOCIALACCOUNT_PROVIDERS["google"]["APPS"][0]["settings"] = {
        "scope": ["this", "that"],
        "auth_params": {"x": "y"},
    }
    settings.SOCIALACCOUNT_PROVIDERS["google"]["SCOPE"] = ["not-this"]
    settings.SOCIALACCOUNT_PROVIDERS["google"]["AUTH_PARAMS"] = {"not": "this"}
    provider = get_adapter().get_provider(rf.get("/"), "google")
    assert provider.get_scope() == ["this", "that"]
    assert provider.get_auth_params() == {"x": "y"}


def test_config_from_provider_config(google_provider_settings, rf, db, settings):
    settings.SOCIALACCOUNT_PROVIDERS["google"]["SCOPE"] = ["some-scope"]
    settings.SOCIALACCOUNT_PROVIDERS["google"]["AUTH_PARAMS"] = {"auth": "param"}
    provider = get_adapter().get_provider(rf.get("/"), "google")
    assert provider.get_scope() == ["some-scope"]
    assert provider.get_auth_params() == {"auth": "param"}
