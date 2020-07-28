from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import MixerProvider


class MixerTests(OAuth2TestsMixin, TestCase):
    provider_id = MixerProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "avatarUrl": "https://uploads.mixer.com/avatar/2evg7cnb.jpg",
            "id": 101052282,
            "bio": "Ninja is the one of the world's most popular gamers.",
            "channel": {
                "id": 90571077,
                "audience": "teen",
                "token": "ninja",
                "viewersCurrent": 0,
                "viewersTotal": 43349053,
                "numFollowers": 2840127,
                "name": "TEM TEM TIME",
                "online": false,
                "languageId": "en"
            },
            "createdAt": "2019-08-01T16:45:00.000Z",
            "deleatedAt": null,
            "experience": 401922,
            "frontendVersion": null,
            "groups": [
                {"id": 1, "name": "User"},
                {"id": 19, "name": "Partner"},
                {"id": 12, "name": "Pro"}
            ],
            "level": 103,
            "primaryTeam": null,
            "social": {
                "facebook": "https://www.facebook.com/NinjaTB"
            },
            "sparks": 7874598,
            "updatedAt": "2020-01-06T19:26:43.640Z",
            "username": "Ninja",
            "verified": true
        }""")
