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
            self.assertEqual(
                expected_url,
                response['location'])
