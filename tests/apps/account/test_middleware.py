from types import ModuleType

import django
from django.http import HttpResponse
from django.test import RequestFactory
from django.test.client import AsyncClient
from django.urls import path, reverse, set_urlconf

import pytest

from allauth.account.internal.decorators import login_not_required
from allauth.account.middleware import _should_redirect_accounts
from allauth.core.exceptions import ImmediateHttpResponse


@login_not_required
def raise_immediate_http_response(request):
    response = HttpResponse(content="raised-response")
    raise ImmediateHttpResponse(response=response)


urlpatterns = [path("raise", raise_immediate_http_response)]


def test_immediate_http_response(settings, client):
    settings.ROOT_URLCONF = "tests.apps.account.test_middleware"
    resp = client.get("/raise")
    assert resp.content == b"raised-response"


skip_django_lt_5 = pytest.mark.skipif(
    django.VERSION[0] < 5, reason="This test is allowed to fail on Django <5."
)


@skip_django_lt_5
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_accounts_redirect_async_ctx(user, db):
    aclient = AsyncClient()
    await aclient.aforce_login(user)
    resp = await aclient.get("/accounts/")
    assert resp["location"] == reverse("account_email")


def test_accounts_redirects_anonymous_to_login(client):
    resp = client.get("/accounts/")
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_login")


def _accounts_urlconf(login_path, email_path):
    urlconf = ModuleType("accounts_urlconf")
    urlconf.urlpatterns = [
        path(login_path, raise_immediate_http_response, name="account_login"),
        path(email_path, raise_immediate_http_response, name="account_email"),
    ]
    return urlconf


@pytest.mark.parametrize(
    "login_path,email_path,request_path,expected",
    [
        ("accounts/login/", "accounts/email/", "/accounts/", True),
        ("accounts/login/", "accounts/email/", "/accounts", False),
        ("accounts/login/", "accounts/email/", "/accounts/login/", False),
        ("accounts/login/", "accounts/email/", "/", False),
        ("en/accounts/login/", "en/accounts/email/", "/en/accounts/", True),
        ("accounts/login", "accounts/email", "/accounts/", True),
        ("login/", "email/", "/", False),
        ("auth/login/", "settings/email/", "/", False),
    ],
)
def test_should_redirect_accounts_only_for_the_shared_prefix(
    login_path, email_path, request_path, expected
):
    set_urlconf(_accounts_urlconf(login_path, email_path))
    try:
        request = RequestFactory().get(request_path)
        response = HttpResponse(status=404)
        assert _should_redirect_accounts(request, response) is expected
    finally:
        set_urlconf(None)
