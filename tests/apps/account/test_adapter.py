import sys
from http import HTTPStatus

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

import pytest

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse


class PreLoginRedirectAccountAdapter(DefaultAccountAdapter):
    def pre_login(self, *args, **kwargs):
        raise ImmediateHttpResponse(HttpResponseRedirect("/foo"))


def test_adapter_pre_login(settings, user, user_password, client):
    settings.ACCOUNT_ADAPTER = (
        "tests.apps.account.test_adapter.PreLoginRedirectAccountAdapter"
    )
    resp = client.post(
        reverse("account_login"),
        {"login": user.username, "password": user_password},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == "/foo"


@pytest.mark.parametrize(
    "x_forwarded_for,expected_ip",
    [
        ("", None),
        ("192.168.1.1", "192.168.1.1"),
        ("192.168.1.1:12345", "192.168.1.1"),
        (
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:db8:85a3::8a2e:370:7334",
        ),
        (
            "[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:12345",
            "2001:db8:85a3::8a2e:370:7334",
        ),
        ("2001:db8::1:0", "2001:db8::1:0"),
        ("[2001:db8::1:0]:12345", "2001:db8::1:0"),
        ("::abc:7:def", "::abc:7:def"),
        ("::1", "::1"),
        ("[::1]:12345", "::1"),
    ]
    + (
        [
            # not supported by ipaddress py3.8
            ("fe80::1234%1", "fe80::1234%1"),
        ]
        if sys.version_info >= (3, 9)
        else []
    ),
)
def test_get_client_ip_vs_x_forwarded_for(rf, x_forwarded_for, expected_ip):
    request = rf.get("/", HTTP_X_FORWARDED_FOR=x_forwarded_for)
    ip = DefaultAccountAdapter(request=request).get_client_ip(request)
    assert ip == (expected_ip if expected_ip else request.META["REMOTE_ADDR"])


@pytest.mark.parametrize(
    "x_forwarded_for",
    [
        " ",
        "999.999.999.999",
        "[999.999.999.999]",
        "999.999.999.999:12345",
        "[999.999.999.999]:12345",
        "[192.0.0.2]",
        "[192.0.0.2]:12345",
        "192.[0].0.2",
        "192.[0].0.2:12345",
        "192.[0.0].2:12345",
        "[192.[0.0].2:12345",
        "2001:db8::1:0:12345",
        "[2001:db8::1:0:12345]",
        "2001:0db8:85a3:0000:0000:8a2e:0370:12345",
        "[2001:0db8:85a3:0000:0000:8a2e:0370]:7334:12345",
        "XwDxNk4JQhUft')) OR 18=(SELECT 18 FROM PG_SLEEP(15))--",
    ],
)
def test_get_client_ip_vs_invalid_x_forwarded_for(rf, x_forwarded_for):
    request = rf.get("/", HTTP_X_FORWARDED_FOR=x_forwarded_for)
    with pytest.raises(PermissionDenied):
        DefaultAccountAdapter(request=request).get_client_ip(request)
