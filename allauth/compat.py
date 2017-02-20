import django


if django.VERSION > (1, 10,):
    from django.urls import NoReverseMatch, reverse, reverse_lazy
else:
    from django.core.urlresolvers import NoReverseMatch, reverse, reverse_lazy  # noqa

if django.VERSION > (1, 8,):
    from collections import OrderedDict
else:
    from django.utils.datastructures import SortedDict as OrderedDict  # noqa

if django.VERSION > (1, 8,):
    from django.template.loader import render_to_string
else:
    from django.template.loader import render_to_string as _render_to_string
    from django.template import RequestContext

    # Wire the Django >= 1.8 API to the Django < 1.7 implementation.
    def render_to_string(
            template_name, context=None, request=None, using=None):
        assert using is None, \
            "Multiple template engines required Django >= 1.8"
        return _render_to_string(
            template_name, context, RequestContext(request))

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
