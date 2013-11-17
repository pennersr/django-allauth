try:
    from mock import Mock, patch
except ImportError:
    from unittest.mock import Mock, patch

from openid.consumer import consumer

from django.test import TestCase
from django.core.urlresolvers import reverse

from . import views


class OpenIDTests(TestCase):

    def test_discovery_failure(self):
        """
        This used to generate a server 500:
        DiscoveryFailure: No usable OpenID services found
        for http://www.google.com/
        """
        resp = self.client.post(reverse('openid_login'),
                                dict(openid='http://www.google.com'))
        self.assertTrue('openid' in resp.context['form'].errors)

    def test_login(self):
        resp = self.client.post(reverse(views.login),
                                dict(openid='http://me.yahoo.com'))
        assert 'login.yahooapis' in resp['location']
        with patch('allauth.socialaccount.providers'
                   '.openid.views._openid_consumer') as consumer_mock:
            client = Mock()
            complete = Mock()
            consumer_mock.return_value = client
            client.complete = complete
            complete_response = Mock()
            complete.return_value = complete_response
            complete_response.status = consumer.SUCCESS
            complete_response.identity_url = 'http://dummy/john/'
            with patch('allauth.socialaccount.providers'
                       '.openid.utils.SRegResponse'):
                with patch('allauth.socialaccount.providers'
                           '.openid.utils.FetchResponse'):
                    resp = self.client.post(reverse('openid_callback'))
                    self.assertEqual('http://testserver/accounts/profile/',
                                     resp['location'])
