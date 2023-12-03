from django.utils.translation import gettext_lazy as _

from allauth import app_settings as allauth_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.utils import user_email, user_username
from allauth.core import context
from allauth.mfa import app_settings
from allauth.utils import import_attribute


class DefaultMFAAdapter:
    """The adapter class allows you to override various functionality of the
    ``allauth.mfa`` app.  To do so, point ``settings.MFA_ADAPTER`` to your own
    class that derives from ``DefaultMFAAdapter`` and override the behavior by
    altering the implementation of the methods according to your own need.
    """

    error_messages = {
        "unverified_email": _(
            "You cannot activate two-factor authentication until you have verified your email address."
        ),
        "add_email_blocked": _(
            "You cannot add an email address to an account protected by two-factor authentication."
        ),
        "incorrect_code": _("Incorrect code."),
        "cannot_delete_authenticator": _(
            "You cannot deactivate two-factor authentication."
        ),
    }
    "The error messages that can occur as part of MFA form handling."

    def get_totp_label(self, user) -> str:
        """Returns the label used for representing the given user in a TOTP QR
        code.
        """
        label = user_email(user)
        if not label:
            label = user_username(user)
        if not label:
            label = str(user)
        return label

    def get_totp_issuer(self) -> str:
        """Returns the TOTP issuer name that will be contained in the TOTP QR
        code.
        """
        issuer = app_settings.TOTP_ISSUER
        if not issuer:
            if allauth_settings.SITES_ENABLED:
                from django.contrib.sites.models import Site

                issuer = Site.objects.get_current(context.request).name
            else:
                issuer = context.request.get_host()
        return issuer

    def encrypt(self, text: str) -> str:
        """Secrets such as the TOTP key are stored in the database.  This
        hook can be used to encrypt those so that they are not stored in the
        clear in the database.
        """
        return text

    def decrypt(self, encrypted_text: str) -> str:
        """Counter part of ``encrypt()``."""
        text = encrypted_text
        return text

    def can_delete_authenticator(self, authenticator):
        return True

    def send_notification_mail(self, *args, **kwargs):
        return get_account_adapter().send_notification_mail(*args, **kwargs)


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()
