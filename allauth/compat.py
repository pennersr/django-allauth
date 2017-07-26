import django


try:
    from collections import UserDict
except ImportError:
    from UserDict import UserDict  # noqa

if django.VERSION > (1, 10,):
    from django.urls import NoReverseMatch, reverse, reverse_lazy
else:
    from django.core.urlresolvers import NoReverseMatch, reverse, reverse_lazy  # noqa

try:
    from urllib.parse import parse_qsl, parse_qs, urlparse, urlunparse, urljoin
except ImportError:
    from urlparse import parse_qsl, parse_qs, urlparse, urlunparse, urljoin  # noqa

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


def authenticate(request=None, **credentials):
    from django.contrib.auth import authenticate
    if django.VERSION >= (1, 11, 0):
        return authenticate(request=request, **credentials)
    else:
        return authenticate(**credentials)
