from io import BytesIO
from typing import Dict
from urllib.parse import quote

from django.utils.http import urlencode
from django.utils.translation import gettext, gettext_lazy as _

from allauth import app_settings as allauth_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.utils import (
    user_display,
    user_email,
    user_pk_to_url_str,
    user_username,
)
from allauth.core import context
from allauth.core.internal.adapter import BaseAdapter
from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator
from allauth.utils import import_attribute


class DefaultMFAAdapter(BaseAdapter):
    """The adapter class allows you to override various functionality of the
    ``allauth.mfa`` app.  To do so, point ``settings.MFA_ADAPTER`` to your own
    class that derives from ``DefaultMFAAdapter`` and override the behavior by
    altering the implementation of the methods according to your own needs.
    """

    error_messages = {
        "add_email_blocked": _(
            "You cannot add an email address to an account protected by two-factor authentication."
        ),
        "cannot_delete_authenticator": _(
            "You cannot deactivate two-factor authentication."
        ),
        "cannot_generate_recovery_codes": _(
            "You cannot generate recovery codes without having two-factor authentication enabled."
        ),
        "incorrect_code": _("Incorrect code."),
        "unverified_email": _(
            "You cannot activate two-factor authentication until you have verified your email address."
        ),
    }
    "The error messages that can occur as part of MFA form handling."

    def get_totp_label(self, user) -> str:
        """Returns the label used for representing the given user in a TOTP QR
        code.
        """
        return self._get_user_identifier(user)

    def _get_user_identifier(self, user) -> str:
        """Human-palatable identifier for a user account. It is intended only
        for display.
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
            issuer = self._get_site_name()
        return issuer

    def build_totp_url(self, user, secret: str) -> str:
        label = self.get_totp_label(user)
        issuer = self.get_totp_issuer()
        params = {
            "secret": secret,
            # This is the default
            # "algorithm": "SHA1",
            "issuer": issuer,
        }
        if app_settings.TOTP_DIGITS != 6:
            params["digits"] = app_settings.TOTP_DIGITS
        if app_settings.TOTP_PERIOD != 30:
            params["period"] = app_settings.TOTP_PERIOD
        return f"otpauth://totp/{quote(label)}?{urlencode(params)}"

    def build_totp_svg(self, url: str) -> str:
        import qrcode
        from qrcode.image.svg import SvgPathImage

        img = qrcode.make(url, image_factory=SvgPathImage)
        buf = BytesIO()
        img.save(buf)
        return buf.getvalue().decode("utf8")

    def _get_site_name(self) -> str:
        if allauth_settings.SITES_ENABLED:
            from django.contrib.sites.models import Site

            return Site.objects.get_current(context.request).name
        else:
            return context.request.get_host()

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

    def can_delete_authenticator(self, authenticator: Authenticator) -> bool:
        return True

    def send_notification_mail(self, *args, **kwargs):
        return get_account_adapter().send_notification_mail(*args, **kwargs)

    def is_mfa_enabled(self, user, types=None) -> bool:
        """
        Returns ``True`` if (and only if) the user has 2FA enabled.
        """
        if user.is_anonymous:
            return False
        qs = Authenticator.objects.filter(user=user)
        if types is not None:
            qs = qs.filter(type__in=types)
        return qs.exists()

    def generate_authenticator_name(self, user, type: Authenticator.Type) -> str:
        """
        Generate a human friendly name for the key. Used to prefill the "Add
        key" form.
        """
        n = Authenticator.objects.filter(user=user, type=type).count()
        if n == 0:
            return gettext("Master key")
        elif n == 1:
            return gettext("Backup key")
        return gettext("Key nr. {number}").format(number=n + 1)

    def get_public_key_credential_rp_entity(self) -> Dict[str, str]:
        name = self._get_site_name()
        return {
            "id": context.request.get_host().partition(":")[0],
            "name": name,
        }

    def get_public_key_credential_user_entity(self, user) -> dict:
        return {
            "id": user_pk_to_url_str(user).encode("utf8"),
            "display_name": user_display(user),
            "name": self._get_user_identifier(user),
        }


def get_adapter() -> DefaultMFAAdapter:
    return import_attribute(app_settings.ADAPTER)()
