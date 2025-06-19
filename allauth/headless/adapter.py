import dataclasses
import uuid
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.db import models
from django.forms.fields import Field

from allauth.account import app_settings as account_settings
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

        Do not override this method if you would like your customized user payloads
        to be reflected in the (dynamically rendered) OpenAPI specification. In that
        case, override ``get_user_dataclass()`` and ``user_as_dataclass`` instead.
        """
        return {
            k: v
            for k, v in dataclasses.asdict(self.user_as_dataclass(user)).items()
            if v not in ("", None)
        }

    def get_frontend_url(self, urlname, **kwargs):
        """Return the frontend URL for the given URL name."""
        return default_get_frontend_url(self.request, urlname, **kwargs)

    def user_as_dataclass(self, user):
        """
        See ``get_user_dataclass()``. This method returns an instance of
        that ``dataclass``, populated with the given ``user`` fields.
        """
        UserDc = self.get_user_dataclass()
        kwargs = {}
        User = get_user_model()
        pk_field_class = type(User._meta.pk)
        if not user.pk:
            id_dc = None
        elif issubclass(pk_field_class, models.IntegerField):
            id_dc = user.pk
        else:
            id_dc = str(user.pk)
        if account_settings.USER_MODEL_USERNAME_FIELD:
            kwargs["username"] = user_username(user)
        if user.pk:
            email = EmailAddress.objects.get_primary_email(user)
        else:
            email = None
        kwargs.update(
            {
                "id": id_dc,
                "email": email if email else None,
                "display": user_display(user),
                "has_usable_password": user.has_usable_password(),
            }
        )
        return UserDc(**kwargs)

    def get_user_dataclass(self):
        """
        Basic user data payloads are exposed in some of the headless responses. If
        you need to customize these payloads in such a way that your custom user
        payload is also reflected in the OpenAPI specification, you wil need to
        provide a ``dataclass`` representing the schema of your custom payload,
        as well as method that takes a ``User`` instance and wraps it into your
        dataclass. This method returns that ``dataclass``.
        """
        fields = []
        User = get_user_model()
        pk_field_class = type(User._meta.pk)
        if issubclass(pk_field_class, models.UUIDField):
            id_type = str
            id_example = str(uuid.uuid4())
        elif issubclass(pk_field_class, models.IntegerField):
            id_type = int
            id_example = 123
        else:
            id_type = str
            id_example = "uid"

        def dc_field(attr, typ, description, example):
            return (
                attr,
                typ,
                dataclasses.field(
                    metadata={
                        "description": description,
                        "example": example,
                    }
                ),
            )

        fields.extend(
            [
                dc_field("id", Optional[id_type], "The user ID.", id_example),
                dc_field(
                    "display", str, "The display name for the user.", "Magic Wizard"
                ),
                dc_field(
                    "email", Optional[str], "The email address.", "email@domain.org"
                ),
                dc_field(
                    "has_usable_password",
                    bool,
                    "Whether or not the account has a password set.",
                    True,
                ),
            ]
        )
        if account_settings.USER_MODEL_USERNAME_FIELD:
            fields.append(dc_field("username", str, "The username.", "wizard"))
        return dataclasses.make_dataclass("User", fields)


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()
