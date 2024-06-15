from typing import Optional

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
