import django
from django.conf import settings
from django.http import HttpResponse
from django.test.client import AsyncClient
from django.urls import path, reverse

import pytest

from allauth.account.internal import flows
from allauth.account.middleware import AccountMiddleware
from allauth.core.exceptions import ImmediateHttpResponse


@pytest.mark.parametrize(
    "path,status_code,content_type,sec_fetch_dest, login_removed",
    [
        ("/", 200, "text/html", None, True),
        ("/", 200, "text/html", "empty", False),
        ("/", 200, "text/html", "document", True),
        ("/", 200, "text/html; charset=utf8", None, True),
        ("/", 200, "text/txt", None, False),
        ("/", 404, "text/html", None, False),
        (settings.STATIC_URL, 200, "text/html", None, False),
        ("/favicon.ico", 200, "image/x-icon", None, False),
        ("/robots.txt", 200, "text/plain", None, False),
        ("/robots.txt", 200, "text/html", None, False),
        ("/humans.txt", 200, "text/plain", None, False),
    ],
)
def test_remove_dangling_login(
    rf, path, status_code, login_removed, content_type, sec_fetch_dest
):
    request = rf.get(path)
    if sec_fetch_dest:
        # rf.get(headers=...) is Django 4.2+.
        request.META["HTTP_SEC_FETCH_DEST"] = sec_fetch_dest
    request.session = {"account_login": True}
    response = HttpResponse(status=status_code)
    response["Content-Type"] = content_type
    mw = AccountMiddleware(lambda request: response)
    mw(request)
    assert (flows.login.LOGIN_SESSION_KEY in request.session) is (not login_removed)


def raise_immediate_http_response(request):
    response = HttpResponse(content="raised-response")
    raise ImmediateHttpResponse(response=response)


urlpatterns = [path("raise", raise_immediate_http_response)]


def test_immediate_http_response(settings, client):
    settings.ROOT_URLCONF = "allauth.account.tests.test_middleware"
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
