from django.conf import settings
from django.http import HttpResponse

import pytest

from allauth.account.middleware import AccountMiddleware


@pytest.mark.parametrize(
    "path,status_code,content_type,login_removed",
    [
        ("/", 200, "text/html", True),
        ("/", 200, "text/html; charset=utf8", True),
        ("/", 200, "text/txt", False),
        ("/", 404, "text/html", False),
        (settings.STATIC_URL, 200, "text/html", False),
        ("/favicon.ico", 200, "image/x-icon", False),
        ("/robots.txt", 200, "text/plain", False),
        ("/robots.txt", 200, "text/html", False),
        ("/humans.txt", 200, "text/plain", False),
    ],
)
def test_remove_dangling_login(rf, path, status_code, login_removed, content_type):
    request = rf.get(path)
    request.session = {"account_login": True}
    response = HttpResponse(status=status_code)
    response["Content-Type"] = content_type
    mw = AccountMiddleware(lambda request: response)
    mw(request)
    assert ("account_login" in request.session) is (not login_removed)
