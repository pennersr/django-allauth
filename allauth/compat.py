import django
from django.test import TestCase as DjangoTestCase

if django.VERSION > (1, 8,):
    from collections import OrderedDict
else:
    from django.utils.datastructures import SortedDict as OrderedDict  # noqa

try:
    from mock import Mock, patch
except ImportError:
    from unittest.mock import Mock, patch  # noqa

try:
    from urllib.parse import parse_qsl, urlparse, urlunparse
except ImportError:
    from urlparse import parse_qsl, urlparse, urlunparse  # noqa

try:
    import importlib
except ImportError:
    from django.utils import importlib  # noqa


class TestCase(DjangoTestCase):

    def assertRedirects(self, response, expected_url,
                        fetch_redirect_response=True,
                        **kwargs):
        if django.VERSION >= (1, 7,):
            super(TestCase, self).assertRedirects(
                response,
                expected_url,
                fetch_redirect_response=fetch_redirect_response,
                **kwargs)

        elif fetch_redirect_response:
            super(TestCase, self).assertRedirects(
                response,
                expected_url,
                **kwargs)
        else:
            self.assertEqual(302, response.status_code)
            actual_url = response['location']
            if expected_url[0] == '/':
                parts = list(urlparse(actual_url))
                parts[0] = parts[1] = ''
                actual_url = urlunparse(parts)
            self.assertEqual(expected_url, actual_url)
