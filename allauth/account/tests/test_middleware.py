from django.conf import settings
from django.http import HttpResponse

import pytest

from allauth.account.middleware import AccountMiddleware


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
    assert ("account_login" in request.session) is (not login_removed)
