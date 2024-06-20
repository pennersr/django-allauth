from django.http import HttpRequest

from allauth.account.authentication import (
    get_authentication_records,
    record_authentication,
)
from allauth.account.internal import flows
from allauth.account.models import Login
from allauth.mfa.models import Authenticator


def post_authentication(
    request,
    authenticator: Authenticator,
    reauthenticated: bool = False,
    passwordless: bool = False,
) -> None:
    authenticator.record_usage()
    extra_data = {
        "id": authenticator.pk,
        "type": authenticator.type,
    }
    if reauthenticated:
        extra_data["reauthenticated"] = True
    if passwordless:
        extra_data["passwordless"] = True
    record_authentication(request, "mfa", **extra_data)


def perform_passwordless_login(request, authenticator: Authenticator, login: Login):
    post_authentication(request, authenticator, passwordless=True)
    return flows.login.perform_login(request, login)


def did_use_passwordless_login(request: HttpRequest) -> bool:
    records = get_authentication_records(request)
    return any(
        (record.get("method"), record.get("type"), record.get("passwordless"))
        == ("mfa", "webauthn", True)
        for record in records
    )
