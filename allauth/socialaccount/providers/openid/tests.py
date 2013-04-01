import sys

from django.test import TestCase
from django.core.urlresolvers import reverse

from . import views


class OpenIDTests(TestCase):

    def test_discovery_failure(self):
        """
        This used to generate a server 500:
        DiscoveryFailure: No usable OpenID services found for http://www.google.com/
        """
        # FIXME: Due to an issue in python3-openid I am temporarily
        # disabling this test for Python 3 until this is sorted out.
        # Doesn't reproduce locally, only on Travis.
        #
        # ...
        # /discover.py", line 164, in fromHTML
        # 
        # link_attrs = html_parse.parseLinkAttrs(html)
        # 
        # File "/home/travis/virtualenv/python3.3/lib/python3.3/site-packages/openid/consumer/html_parse.py", line 189, in parseLinkAttrs
        # 
        # html = html.decode("utf-8")
        # 
        # UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position 7955: invalid start byte
        if sys.version_info[0] >= 3:
            return
        # (end FIXME)

        resp = self.client.post(reverse(views.login),
                         dict(openid='http://www.google.com'))
        self.assertTrue('openid' in resp.context['form'].errors)
