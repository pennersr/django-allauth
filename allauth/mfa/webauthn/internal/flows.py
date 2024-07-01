from typing import Iterable, Optional, Tuple

from django.contrib import messages
from django.http import HttpRequest

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.authentication import get_authentication_records
from allauth.account.internal import flows
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.account.models import Login
from allauth.mfa import signals
from allauth.mfa.base.internal.flows import (
    delete_and_cleanup,
    post_authentication,
)
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.flows import (
    auto_generate_recovery_codes,
)
from allauth.mfa.webauthn.internal import auth


def begin_registration(request: HttpRequest, user, passwordless: bool) -> dict:
    raise_if_reauthentication_required(request)
    creation_options = auth.begin_registration(user, passwordless)
    return creation_options


def add_authenticator(
    request, name: str, credential: dict
) -> Tuple[Authenticator, Optional[Authenticator]]:
    raise_if_reauthentication_required(request)
    authenticator = auth.WebAuthn.add(
        request.user,
        name,
        credential,
    ).instance
    signals.authenticator_added.send(
        sender=Authenticator,
        request=request,
        user=request.user,
        authenticator=authenticator,
    )
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/webauthn_added.txt")
    adapter.send_notification_mail("mfa/email/webauthn_added", request.user)
    rc_authenticator = auto_generate_recovery_codes(request)
    return authenticator, rc_authenticator


def remove_authenticators(request, authenticators: Iterable[Authenticator]) -> None:
    raise_if_reauthentication_required(request)
    for authenticator in authenticators:
        remove_authenticator(request, authenticator)


def remove_authenticator(request, authenticator: Authenticator):
    raise_if_reauthentication_required(request)
    delete_and_cleanup(request, authenticator)
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/webauthn_removed.txt")
    adapter.send_notification_mail("mfa/email/webauthn_removed", request.user)


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


def reauthenticate(request: HttpRequest, authenticator: Authenticator):
    post_authentication(request, authenticator, reauthenticated=True)


def rename_authenticator(request, authenticator: Authenticator, name: str):
    raise_if_reauthentication_required(request)
    wrapper = authenticator.wrap()
    wrapper.name = name
    authenticator.save()
