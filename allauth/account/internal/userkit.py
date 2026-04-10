from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import FieldDoesNotExist
from django.utils.encoding import force_str

from allauth.account import app_settings
from allauth.utils import import_callable


def user_id_to_str(user: AbstractBaseUser) -> str:
    return user._meta.pk.value_to_string(user)


def str_to_user_id(value: str):
    return get_user_model()._meta.pk.to_python(value)


def user_field(user: AbstractBaseUser, field, *args, commit=False):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if not field:
        return
    User = get_user_model()
    try:
        field_meta = User._meta.get_field(field)
        max_length = field_meta.max_length  # type:ignore[union-attr]
    except FieldDoesNotExist:
        if not hasattr(user, field):
            return
        max_length = None
    if args:
        # Setter
        v = args[0]
        if v:
            v = v[0:max_length]
        elif v is None and not field_meta.null:  # type:ignore[union-attr]
            v = ""
        setattr(user, field, v)
        if commit:
            user.save(update_fields=[field])
    else:
        # Getter
        return getattr(user, field)


def did_user_login(user: AbstractBaseUser | None) -> bool:
    return user is not None and user.last_login is not None


_user_display_callable = None


def default_user_display(user: AbstractBaseUser) -> str:
    ret = ""
    if app_settings.USER_MODEL_USERNAME_FIELD:
        ret = getattr(user, app_settings.USER_MODEL_USERNAME_FIELD)
    return ret or force_str(user) or force_str(user._meta.verbose_name)


def user_display(user: AbstractBaseUser) -> str:
    global _user_display_callable
    if not _user_display_callable:
        f = getattr(settings, "ACCOUNT_USER_DISPLAY", default_user_display)
        _user_display_callable = import_callable(f)
    return _user_display_callable(user)


def user_username(user: AbstractBaseUser, *args, commit=False):
    if args and not app_settings.PRESERVE_USERNAME_CASING and args[0]:
        args = tuple([args[0].lower()])
    return user_field(user, app_settings.USER_MODEL_USERNAME_FIELD, *args)


def user_email(user: AbstractBaseUser, *args, commit=False):
    if args and args[0]:
        args = tuple([args[0].lower()])
    ret = user_field(user, app_settings.USER_MODEL_EMAIL_FIELD, *args, commit=commit)
    if ret:
        ret = ret.lower()
    return ret
