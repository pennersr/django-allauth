from django.forms.fields import Field

from allauth.core.internal.adapter import BaseAdapter
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
        "email_or_username": "Pass only one of email or username, not both.",
        "invalid_token": "Invalid token.",
        "token_authentication_not_supported": "Provider does not support token authentication.",
        "token_required": "`id_token` and/or `access_token` required.",
        "required": Field.default_error_messages["required"],
        "unknown_email": "Unknown email address.",
        "invalid_url": "Invalid URL.",
    }


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()
