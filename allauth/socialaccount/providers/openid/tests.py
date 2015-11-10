from openid.consumer import consumer

from django.core.urlresolvers import reverse

from allauth.utils import get_user_model
from allauth.tests import TestCase, Mock, patch

from . import views
from .utils import AXAttribute


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
                       '.openid.utils.SRegResponse') as sr_mock:
                with patch('allauth.socialaccount.providers'
                           '.openid.utils.FetchResponse') as fr_mock:
                    sreg_mock = Mock()
                    ax_mock = Mock()
                    sr_mock.fromSuccessResponse = sreg_mock
                    fr_mock.fromSuccessResponse = ax_mock
                    sreg_mock.return_value = {}
                    ax_mock.return_value = {AXAttribute.PERSON_FIRST_NAME:
                                            ['raymond']}
                    resp = self.client.post(reverse('openid_callback'))
                    self.assertRedirects(
                        resp,
                        'http://testserver/accounts/profile/',
                        fetch_redirect_response=False)
                    get_user_model().objects.get(first_name='raymond')
