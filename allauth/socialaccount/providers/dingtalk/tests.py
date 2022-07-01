from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DingtalkProvider


class DingtalkTests(OAuth2TestsMixin, TestCase):
    provider_id = DingtalkProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                'nick': 'aiden',
                'unionId': 'hTaCSb1nM4RXii6jaQvHZqQiEiE',
                'avatarUrl': 'https://static-legacy.dingtalk.com/media/lADPDg7mViaksW3NBJPNBJI_1170_1171.jpg',
                'openId': 'ELdCPlk0V2LodZHx3n0p5AiEiE',
            }
            """,
        )
