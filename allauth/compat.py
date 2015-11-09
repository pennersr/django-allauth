import django

if django.VERSION > (1, 8,):
    from collections import OrderedDict
else:
    from django.utils.datastructures import SortedDict as OrderedDict  # noqa

try:
    from urllib.parse import parse_qsl, urlparse, urlunparse
except ImportError:
    from urlparse import parse_qsl, urlparse, urlunparse  # noqa

try:
    import importlib
except ImportError:
    from django.utils import importlib  # noqa
