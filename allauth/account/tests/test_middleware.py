from django.conf import settings
from django.http import HttpResponse

import pytest

from allauth.account.middleware import AccountMiddleware


@pytest.mark.parametrize(
    "path,status_code,login_removed",
    [
        ("/", 200, True),
        ("/", 404, False),
        (settings.STATIC_URL, 200, False),
        ("/favicon.ico", 200, False),
        ("/robots.txt", 200, False),
        ("/humans.txt", 200, False),
    ],
)
def test_remove_dangling_login(rf, path, status_code, login_removed):
    request = rf.get(path)
    request.session = {"account_login": True}
    mw = AccountMiddleware(lambda request: HttpResponse(status=status_code))
    mw(request)
    assert ("account_login" in request.session) is (not login_removed)
