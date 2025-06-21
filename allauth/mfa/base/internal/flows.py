from typing import Callable, Optional

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.flows.login import record_authentication
from allauth.core import context, ratelimit
from allauth.mfa import signals
from allauth.mfa.models import Authenticator


def delete_dangling_recovery_codes(user) -> Optional[Authenticator]:
    deleted_authenticator = None
    qs = Authenticator.objects.filter(user=user)
    if not qs.exclude(type=Authenticator.Type.RECOVERY_CODES).exists():
        deleted_authenticator = qs.first()
        qs.delete()
    return deleted_authenticator


def delete_and_cleanup(request, authenticator) -> None:
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
    record_authentication(request, authenticator.user, "mfa", **extra_data)


def check_rate_limit(user) -> Callable[[], None]:
    key = f"mfa-auth-user-{str(user.pk)}"
    if not ratelimit.consume(
        context.request,
        action="login_failed",
        key=key,
    ):
        raise get_account_adapter().validation_error("too_many_login_attempts")
    return lambda: ratelimit.clear(context.request, action="login_failed", key=key)
