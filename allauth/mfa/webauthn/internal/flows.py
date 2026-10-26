from __future__ import annotations

from collections.abc import Iterable

from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest, HttpResponse

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal import flows
from allauth.account.internal.flows.login import get_authentication_records
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.account.models import Login
from allauth.core.internal.httpkit import authenticated_user
from allauth.mfa import signals
from allauth.mfa.base.internal.flows import delete_and_cleanup, post_authentication
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.flows import auto_generate_recovery_codes
from allauth.mfa.webauthn.internal import auth


def begin_registration(
    request: HttpRequest, user, passwordless: bool, signup: bool = False
) -> dict:
    if not signup:
        raise_if_reauthentication_required(request, app="allauth.mfa")
    creation_options = auth.begin_registration(user, passwordless)
    return creation_options


def signup_authenticator(
    request: HttpRequest, user, name: str, credential: dict
) -> Authenticator:
    authenticator, rc_authenticator = _signup_or_add_authenticator(
        request, user, name, credential, signup=True
    )
    return authenticator


def add_authenticator(
    request: HttpRequest, name: str, credential: dict
) -> tuple[Authenticator, Authenticator | None]:
    raise_if_reauthentication_required(request, app="allauth.mfa")
    return _signup_or_add_authenticator(
        request,
        user=request.user,
        name=name,
        credential=credential,
        signup=False,
    )


def _signup_or_add_authenticator(
    request: HttpRequest,
    user,
    name: str,
    credential: dict,
    signup: bool = False,
) -> tuple[Authenticator, Authenticator | None]:
    authenticator = auth.WebAuthn.add(
        user,
        name,
        credential,
    ).instance
    signals.authenticator_added.send(
        sender=Authenticator,
        request=request,
        user=user,
        authenticator=authenticator,
    )
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/webauthn_added.txt")
    if not signup:
        adapter.send_notification_mail("mfa/email/webauthn_added", user)
    rc_authenticator = None
    if not signup:
        rc_authenticator = auto_generate_recovery_codes(request)
    return authenticator, rc_authenticator


def remove_authenticators(
    request: HttpRequest, authenticators: Iterable[Authenticator]
) -> None:
    raise_if_reauthentication_required(request, app="allauth.mfa")
    for authenticator in authenticators:
        _remove_authenticator_without_reauthentication(request, authenticator)


def remove_authenticator(request: HttpRequest, authenticator: Authenticator) -> None:
    raise_if_reauthentication_required(request, app="allauth.mfa")
    _remove_authenticator_without_reauthentication(request, authenticator)


def _remove_authenticator_without_reauthentication(
    request: HttpRequest, authenticator: Authenticator
) -> None:
    delete_and_cleanup(request, authenticator)
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/webauthn_removed.txt")
    adapter.send_notification_mail(
        "mfa/email/webauthn_removed", authenticated_user(request)
    )


def perform_passwordless_login(
    request: HttpRequest, authenticator: Authenticator, login: Login
) -> HttpResponse:
    post_authentication(request, authenticator, passwordless=True)
    return flows.login.perform_login(request, login)


def did_use_passwordless_login(request: HttpRequest, user: AbstractBaseUser) -> bool:
    records = get_authentication_records(request, user)
    return any(
        (record.get("method"), record.get("type"), record.get("passwordless"))
        == ("mfa", "webauthn", True)
        for record in records
    )


def reauthenticate(request: HttpRequest, authenticator: Authenticator) -> None:
    post_authentication(request, authenticator, reauthenticated=True)


def rename_authenticator(
    request: HttpRequest, authenticator: Authenticator, name: str
) -> None:
    raise_if_reauthentication_required(request, app="allauth.mfa")
    wrapper = authenticator.wrap()
    wrapper.name = name
    authenticator.save()
