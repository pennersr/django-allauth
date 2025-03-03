from typing import Any, Dict

from django.forms.fields import Field

from allauth.account.models import EmailAddress
from allauth.account.utils import user_display, user_username
from allauth.core.internal.adapter import BaseAdapter
from allauth.core.internal.httpkit import default_get_frontend_url
from allauth.headless import app_settings
from allauth.utils import import_attribute


class DefaultHeadlessAdapter(BaseAdapter):
    """The adapter class allows you to override various functionality of the
    ``allauth.headless`` app.  To do so, point ``settings.HEADLESS_ADAPTER`` to your own
    class that derives from ``DefaultHeadlessAdapter`` and override the behavior by
    altering the implementation of the methods according to your own need.
    """

    error_messages = {
        # For the following error messages i18n is not an issue as these should not be
        # showing up in a UI.
        "account_not_found": "Unknown account.",
        "client_id_required": "`client_id` required.",
        "invalid_token": "Invalid token.",
        "token_authentication_not_supported": "Provider does not support token authentication.",
        "token_required": "`id_token` and/or `access_token` required.",
        "required": Field.default_error_messages["required"],
        "unknown_email": "Unknown email address.",
        "unknown_provider": "Unknown provider.",
        "invalid_url": "Invalid URL.",
    }

    def serialize_user(self, user) -> Dict[str, Any]:
        """
        Returns the basic user data. Note that this data is also exposed in
        partly authenticated scenario's (e.g. password reset, email
        verification).
        """
        ret = {
            "display": user_display(user),
            "has_usable_password": user.has_usable_password(),
        }
        if user.pk:
            ret["id"] = user.pk
            email = EmailAddress.objects.get_primary_email(user)
            if email:
                ret["email"] = email
        username = user_username(user)
        if username:
            ret["username"] = username
        return ret

    def get_frontend_url(self, urlname, **kwargs):
        """Return the frontend URL for the given URL name."""
        return default_get_frontend_url(self.request, urlname, **kwargs)


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()
