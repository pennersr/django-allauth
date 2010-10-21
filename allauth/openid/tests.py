from django.test import TestCase
from django.core.urlresolvers import reverse

import views

class OpenIDTests(TestCase):

    def test_discovery_failure(self):
        """
        This used to generate a server 500:
        DiscoveryFailure: No usable OpenID services found for http://www.google.com/
        """
        resp = self.client.post(reverse(views.login), 
                         dict(openid='http://www.google.com'))
        self.assertTrue(resp.context['form'].errors.has_key('openid'))

