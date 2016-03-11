from django.core.urlresolvers import reverse

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse, mocked_response
from allauth.socialaccount.providers import registry
from allauth.compat import parse_qs, urlparse

from .provider import ShopifyProvider


class ShopifyTests(create_oauth2_tests(registry.by_id(ShopifyProvider.id))):
    def login(self, resp_mock, process='login', with_refresh_token=True):
        resp = self.client.get(reverse(self.provider.id + '_login'),
                               {'process': process, 'shop': 'test'})
        p = urlparse(resp['location'])
        q = parse_qs(p.query)
        complete_url = reverse(self.provider.id+'_callback')
        self.assertGreater(q['redirect_uri'][0]
                           .find(complete_url), 0)
        response_json = self \
            .get_login_response_json(with_refresh_token=with_refresh_token)
        with mocked_response(
                MockedResponse(
                    200,
                    response_json,
                    {'content-type': 'application/json'}),
                resp_mock):
            resp = self.client.get(complete_url,
                                   {'code': 'test',
                                    'state': q['state'][0],
                                    'shop': 'test',
                                    })
        return resp

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "shop": {
                "id": "1234566",
                "name": "Test Shop",
                "email": "email@example.com"
            }
        }
        """)
