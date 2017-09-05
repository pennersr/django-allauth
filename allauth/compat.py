import django
from django.utils import six


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


def int_to_base36(i):
    """
    Django on py2 raises ValueError on large values.
    """
    if six.PY2:
        char_set = '0123456789abcdefghijklmnopqrstuvwxyz'
        if i < 0:
            raise ValueError("Negative base36 conversion input.")
        if not isinstance(i, six.integer_types):
            raise TypeError("Non-integer base36 conversion input.")
        if i < 36:
            return char_set[i]
        b36 = ''
        while i != 0:
            i, n = divmod(i, 36)
            b36 = char_set[n] + b36
    else:
        from django.utils.http import int_to_base36
        b36 = int_to_base36(i)
    return b36


def base36_to_int(s):
    if six.PY2:
        if len(s) > 13:
            raise ValueError("Base36 input too large")
        value = int(s, 36)
    else:
        from django.utils.http import base36_to_int
        value = base36_to_int(s)
    return value
