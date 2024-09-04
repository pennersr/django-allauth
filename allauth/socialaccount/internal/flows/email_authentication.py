from allauth import app_settings as allauth_settings
from allauth.account.models import EmailAddress


def wipe_password(request, user, email: str):
    """
    Consider a scenario where an attacker signs up for an account using the
    email address of a victim. Obviously, the email address cannot be
    verified, yet the attacker -- knowing the password -- can wait until the
    victim appears.  When the victim signs in using email authentication, it
    is not obvious that the victim is signing into an account that was not
    created by the victim. As a result, both the attacker and the victim now
    have access to the account. To prevent this, we wipe the password of the
    account in case the email address was not verified, effectively locking
    out the attacker.
    """
    try:
        address = EmailAddress.objects.get_for_user(user, email)
    except EmailAddress.DoesNotExist:
        address = None
    if address and address.verified:
        # Verified email address, no reason to worry.
        return
    if user.has_usable_password():
        user.set_unusable_password()
        user.save(update_fields=["password"])
    # Also wipe any other sessions (upstream integrators may hook up to the
    # ending of the sessions to trigger e.g. backchannel logout.
    if allauth_settings.USERSESSIONS_ENABLED:
        from allauth.usersessions.internal.flows.sessions import (
            end_other_sessions,
        )

        end_other_sessions(request, user)
