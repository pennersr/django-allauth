import django
from django.http import HttpResponse
from django.test.client import AsyncClient
from django.urls import path, reverse

import pytest

from allauth.account.internal.decorators import login_not_required
from allauth.core.exceptions import ImmediateHttpResponse


@login_not_required
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
