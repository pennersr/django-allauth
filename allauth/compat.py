import django


if django.VERSION > (1, 10,):
    from django.urls import NoReverseMatch, reverse, reverse_lazy
else:
    from django.core.urlresolvers import NoReverseMatch, reverse, reverse_lazy  # noqa

try:
    from urllib.parse import parse_qsl, parse_qs, urlparse, urlunparse
except ImportError:
    from urlparse import parse_qsl, parse_qs, urlparse, urlunparse  # noqa

if django.VERSION >= (1, 9, 0):
    from django.contrib.auth.password_validation import validate_password
else:
    def validate_password(password, user=None, password_validators=None):
        pass


def template_context_value(context, key):
    try:
        value = context[key]
    except KeyError:
        value = getattr(context, key)
    return value


def is_anonymous(user):
    if django.VERSION > (1, 10,):
        return user.is_anonymous
    else:
        return user.is_anonymous()


def is_authenticated(user):
    if django.VERSION > (1, 10,):
        return user.is_authenticated
    else:
        return user.is_authenticated()
