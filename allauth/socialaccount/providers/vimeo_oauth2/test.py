from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import VimeoOAuth2Provider


class VimeoOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = VimeoOAuth2Provider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
            "uri": "/users/12345",
            "name": "AllAuth",
            "link": "https://vimeo.com/user12345",
            "created_time": "2012-06-04T00:02:16+00:00",
            "pictures": {
                "uri": null,
                "active": false,
                "type": "default",
                "sizes": [{
                    "width": 30,
                    "height": 30,
                    "link": "https://i.vimeocdn.com/portrait/defaults-blue_30x30.png"
                }],
                "resource_key": "1234567890abcdef"
            },
            "resource_key": "1234567890abcdef",
            "account": "pro"
        }""",
        )  # noqa
