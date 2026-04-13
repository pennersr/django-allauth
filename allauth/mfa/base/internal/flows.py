from __future__ import annotations

from collections.abc import Callable

from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.flows.login import record_authentication
from allauth.core import context, ratelimit
from allauth.mfa import signals
from allauth.mfa.models import Authenticator


def delete_dangling_recovery_codes(user: AbstractBaseUser) -> Authenticator | None:
    deleted_authenticator = None
    qs = Authenticator.objects.filter(user_id=user.pk)
    if not qs.exclude(type=Authenticator.Type.RECOVERY_CODES).exists():
        deleted_authenticator = qs.first()
        qs.delete()
    return deleted_authenticator


def delete_and_cleanup(request: HttpRequest, authenticator) -> None:
    authenticator.delete()
    rc_auth = delete_dangling_recovery_codes(authenticator.user)
    for auth in [authenticator, rc_auth]:
        if auth:
            signals.authenticator_removed.send(
                sender=Authenticator,
                request=request,
                user=request.user,
                authenticator=auth,
            )


def post_authentication(
    request: HttpRequest,
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
    record_authentication(request, authenticator.user, "mfa", **extra_data)
    signals.authenticator_used.send(
        sender=Authenticator,
        request=request,
        user=authenticator.user,
        authenticator=authenticator,
        reauthenticated=reauthenticated,
        passwordless=passwordless,
    )


def check_rate_limit(user: AbstractBaseUser) -> Callable[[], None]:
    key = f"mfa-auth-user-{str(user.pk)}"
    if not ratelimit.consume(
        context.request,
        action="login_failed",
        key=key,
    ):
        raise get_account_adapter().validation_error("too_many_login_attempts")
    return lambda: ratelimit.clear(context.request, action="login_failed", key=key)
